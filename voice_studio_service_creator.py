#!/usr/bin/env python3
"""
VoiceStudio - Service-ize the Engine Gateway
Create Windows Service + scripts + WiX fragment
"""

import os
import sys
from pathlib import Path

def create_engine_gateway_service():
    """Create Windows Service for Engine Gateway"""
    
    # Determine repo path
    repo_paths = [r"C:\VoiceStudio", r"C:\Users\Tyler\VoiceStudio"]
    repo = None
    for path in repo_paths:
        if os.path.exists(path):
            repo = path
            break
    
    if not repo:
        raise Exception("Repo not found at C:\\VoiceStudio or C:\\Users\\Tyler\\VoiceStudio")
    
    print(f"Using repo path: {repo}")
    
    # Create directory structure
    svc_root = os.path.join(repo, "Services", "EngineGateway.ServiceHost")
    scripts_dir = os.path.join(repo, "scripts")
    tools_dir = os.path.join(repo, "tools")
    wix_dir = os.path.join(repo, "Installer", "VoiceStudio.Installer", "WixFragments")
    
    for dir_path in [svc_root, scripts_dir, tools_dir, wix_dir]:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Service project file
    proj_file = os.path.join(svc_root, "EngineGateway.ServiceHost.csproj")
    proj_content = '''<Project Sdk="Microsoft.NET.Sdk.Worker">
  <PropertyGroup>
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWindowsService>true</UseWindowsService>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <AssemblyName>VoiceStudio.EngineGateway.ServiceHost</AssemblyName>
    <RootNamespace>VoiceStudio.EngineGateway.ServiceHost</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.Extensions.Hosting.WindowsServices" Version="8.0.1" />
    <PackageReference Include="Serilog" Version="3.1.1" />
    <PackageReference Include="Serilog.Sinks.File" Version="5.0.0" />
    <PackageReference Include="Serilog.Extensions.Hosting" Version="8.0.0" />
  </ItemGroup>
</Project>'''
    
    with open(proj_file, 'w', encoding='utf-8') as f:
        f.write(proj_content)
    print(f"Created project file: {proj_file}")
    
    # Directory.Build.props
    props_file = os.path.join(svc_root, "Directory.Build.props")
    props_content = '''<Project>
  <PropertyGroup>
    <PlatformTarget>x64</PlatformTarget>
  </PropertyGroup>
</Project>'''
    
    with open(props_file, 'w', encoding='utf-8') as f:
        f.write(props_content)
    print(f"Created props file: {props_file}")
    
    # Program.cs
    prog_file = os.path.join(svc_root, "Program.cs")
    prog_content = '''using System.Diagnostics;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Serilog;

namespace VoiceStudio.EngineGateway.ServiceHost
{
  public class Program
  {
    public static async Task Main(string[] args)
    {
      var logs = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "VoiceStudio","logs");
      Directory.CreateDirectory(logs);
      Log.Logger = new LoggerConfiguration()
        .MinimumLevel.Information()
        .WriteTo.File(Path.Combine(logs,"engine_gateway_service.log"), rollingInterval: RollingInterval.Day, retainedFileCountLimit: 7)
        .CreateLogger();

      try
      {
        await Host.CreateDefaultBuilder(args)
          .UseWindowsService()
          .UseSerilog()
          .ConfigureServices((ctx, services) =>
          {
            services.AddHostedService<GatewaySupervisor>();
            services.Configure<GatewayOptions>(ctx.Configuration.GetSection("Gateway"));
          })
          .Build()
          .RunAsync();
      }
      catch (Exception ex)
      {
        Log.Fatal(ex, "EngineGateway service crashed at bootstrap");
      }
      finally { Log.CloseAndFlush(); }
    }
  }

  public class GatewayOptions
  {
    public string PythonExe { get; set; } =
      Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "VoiceStudio","pyenv","Scripts","python.exe");
    public string GatewayPy { get; set; } =
      Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "VoiceStudio","workers","ops","engine_gateway.py");
    public int Port { get; set; } = 59120;
    public int RestartDelayMs { get; set; } = 1500;
  }

  public class GatewaySupervisor : BackgroundService
  {
    private readonly ILogger<GatewaySupervisor> _logger;
    private readonly GatewayOptions _opt;
    private Process? _proc;

    public GatewaySupervisor(ILogger<GatewaySupervisor> logger, Microsoft.Extensions.Options.IOptions<GatewayOptions> opt)
    { _logger = logger; _opt = opt.Value; }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
      _logger.LogInformation("EngineGateway supervisor starting; Python={PythonExe}, Script={GatewayPy}, Port={Port}",
        _opt.PythonExe, _opt.GatewayPy, _opt.Port);

      while (!stoppingToken.IsCancellationRequested)
      {
        try
        {
          if (!File.Exists(_opt.PythonExe) || !File.Exists(_opt.GatewayPy))
          {
            _logger.LogWarning("Python or gateway script missing. Waiting for provisioning...");
            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            continue;
          }

          var psi = new ProcessStartInfo(_opt.PythonExe, _opt.GatewayPy)
          {
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true
          };
          _proc = Process.Start(psi);
          _logger.LogInformation("EngineGateway started (PID {Pid})", _proc?.Id);

          _proc!.OutputDataReceived += (_, e) => { if(e.Data!=null) _logger.LogInformation(e.Data); };
          _proc.ErrorDataReceived  += (_, e) => { if(e.Data!=null) _logger.LogWarning(e.Data); };
          _proc.BeginOutputReadLine(); _proc.BeginErrorReadLine();

          await WaitForExitAsync(_proc, stoppingToken);
          _logger.LogWarning("EngineGateway exited (PID {Pid}). Restarting in {Delay} ms...", _proc?.Id, _opt.RestartDelayMs);
          await Task.Delay(_opt.RestartDelayMs, stoppingToken);
        }
        catch (TaskCanceledException) { /* service stopping */ }
        catch (Exception ex)
        {
          _logger.LogError(ex, "Supervisor loop error; retry soon");
          await Task.Delay(2000, stoppingToken);
        }
      }
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
      try
      {
        if (_proc != null && !_proc.HasExited)
        {
          _logger.LogInformation("Stopping EngineGateway (PID {Pid})", _proc.Id);
          _proc.Kill(entireProcessTree: true);
          await Task.Delay(400, cancellationToken);
        }
      }
      catch { }
      await base.StopAsync(cancellationToken);
    }

    private static Task WaitForExitAsync(Process p, CancellationToken ct)
    {
      var tcs = new TaskCompletionSource();
      p.EnableRaisingEvents = true;
      p.Exited += (_, __) => tcs.TrySetResult();
      if (p.HasExited) tcs.TrySetResult();
      ct.Register(() => tcs.TrySetCanceled());
      return tcs.Task;
    }
  }
}'''
    
    with open(prog_file, 'w', encoding='utf-8') as f:
        f.write(prog_content)
    print(f"Created Program.cs: {prog_file}")
    
    # appsettings.json
    appset_file = os.path.join(svc_root, "appsettings.json")
    appset_content = '''{
  "Gateway": {
    "Port": 59120,
    "RestartDelayMs": 1500,
    "PythonExe": "C:/ProgramData/VoiceStudio/pyenv/Scripts/python.exe",
    "GatewayPy": "C:/ProgramData/VoiceStudio/workers/ops/engine_gateway.py"
  }
}'''
    
    with open(appset_file, 'w', encoding='utf-8') as f:
        f.write(appset_content)
    print(f"Created appsettings.json: {appset_file}")
    
    # Install script
    install_script = os.path.join(scripts_dir, "Install-EngineGatewayService.ps1")
    install_content = '''param(
  [string]$BuildConfig = "Release",
  [string]$ServiceName = "VoiceStudio.EngineGateway",
  [string]$DisplayName = "VoiceStudio Engine Gateway",
  [string]$Description = "Persistent router for VoiceStudio engines (XTTS/OpenVoice/CosyVoice/Coqui) on 127.0.0.1:59120"
)
$ErrorActionPreference='Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$proj = Join-Path $root "Services\\EngineGateway.ServiceHost\\EngineGateway.ServiceHost.csproj"
$bin  = Join-Path $root "out\\gateway_service\\$BuildConfig"
New-Item -ItemType Directory -Force -Path $bin | Out-Null

# Build
dotnet build $proj -c $BuildConfig -o $bin | Out-Null
$exe = Join-Path $bin "VoiceStudio.EngineGateway.ServiceHost.exe"
if(!(Test-Path $exe)){ throw "Build failed: $exe not found." }

# Copy to Program Files
$inst = "${env:ProgramFiles}\\VoiceStudio\\EngineGateway.Service"
New-Item -ItemType Directory -Force -Path $inst | Out-Null
Copy-Item "$bin\\*" $inst -Recurse -Force

# Create service (run as LocalService)
if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
  Write-Host "Service exists; stopping/updating..." -ForegroundColor Yellow
  sc.exe stop $ServiceName | Out-Null
  sc.exe delete $ServiceName | Out-Null
  Start-Sleep -Seconds 1
}
sc.exe create $ServiceName binPath= "\\"$inst\\VoiceStudio.EngineGateway.ServiceHost.exe\\"" start= auto obj= "NT AUTHORITY\\LocalService" DisplayName= "\\"$DisplayName\\"" | Out-Null
sc.exe description $ServiceName "$Description" | Out-Null

# Recovery: restart on failure
sc.exe failure $ServiceName reset= 86400 actions= restart/3000/restart/30000/restart/60000 | Out-Null

# Firewall allow localhost:59120 inbound (loopback)
if (-not (Get-NetFirewallRule -DisplayName "VoiceStudio EngineGateway 59120" -ErrorAction SilentlyContinue)) {
  New-NetFirewallRule -DisplayName "VoiceStudio EngineGateway 59120" -Direction Inbound -Protocol TCP -LocalPort 59120 -Action Allow -Program $exe | Out-Null
}

# Start service
sc.exe start $ServiceName | Out-Null
Start-Sleep -Seconds 2
sc.exe query $ServiceName

Write-Host "Installed & started $ServiceName. Logs: C:\\ProgramData\\VoiceStudio\\logs\\engine_gateway_service.log" -ForegroundColor Green'''
    
    with open(install_script, 'w', encoding='utf-8') as f:
        f.write(install_content)
    print(f"Created install script: {install_script}")
    
    # Uninstall script
    uninstall_script = os.path.join(scripts_dir, "Uninstall-EngineGatewayService.ps1")
    uninstall_content = '''param([string]$ServiceName = "VoiceStudio.EngineGateway")
$ErrorActionPreference='Stop'
if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
  sc.exe stop $ServiceName | Out-Null
  sc.exe delete $ServiceName | Out-Null
  Write-Host "Removed service $ServiceName" -ForegroundColor Green
} else {
  Write-Host "Service $ServiceName not found."
}'''
    
    with open(uninstall_script, 'w', encoding='utf-8') as f:
        f.write(uninstall_content)
    print(f"Created uninstall script: {uninstall_script}")
    
    # WiX fragment
    wxs_file = os.path.join(wix_dir, "Service_EngineGateway.wxs")
    wxs_content = '''<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Fragment>
    <DirectoryRef Id="ProgramFilesFolder">
      <Directory Id="INSTALLDIR" Name="VoiceStudio">
        <Directory Id="GatewayServiceDir" Name="EngineGateway.Service" />
      </Directory>
    </DirectoryRef>

    <ComponentGroup Id="CG_EngineGatewayService">
      <Component Id="CMP_GatewayExe" Directory="GatewayServiceDir" Guid="*">
        <File Id="F_GatewayExe" Source="$(var.EngineGatewayBin)\\VoiceStudio.EngineGateway.ServiceHost.exe" KeyPath="yes" />
        <ServiceInstall
          Id="SI_EngineGateway"
          Name="VoiceStudio.EngineGateway"
          DisplayName="VoiceStudio Engine Gateway"
          Description="Persistent router for VoiceStudio engines"
          Type="ownProcess"
          Start="auto"
          Account="NT AUTHORITY\\LocalService"
          ErrorControl="normal" />
        <ServiceControl Id="SC_EngineGateway" Name="VoiceStudio.EngineGateway" Start="install" Stop="uninstall" Remove="uninstall" Wait="yes" />
      </Component>
    </ComponentGroup>
  </Fragment>
</Wix>'''
    
    with open(wxs_file, 'w', encoding='utf-8') as f:
        f.write(wxs_content)
    print(f"Created WiX fragment: {wxs_file}")
    
    # Update start_dev_stack.ps1 to check for service
    start_dev_script = os.path.join(tools_dir, "start_dev_stack.ps1")
    if os.path.exists(start_dev_script):
        with open(start_dev_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "EngineGateway service detected" not in content:
            service_check = '''# Skip engine-gateway python if service present
if((Get-Service -Name 'VoiceStudio.EngineGateway' -ErrorAction SilentlyContinue)){
  Write-Host 'EngineGateway service detected; skipping dev-start for gateway.' -ForegroundColor Yellow
} else {
  powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\\start_engine_gateway.ps1" | Out-Null
}'''
            content = service_check + "\n" + content
            
            with open(start_dev_script, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated start_dev_stack.ps1 with service check")
    
    print("\n" + "="*60)
    print("ENGINE GATEWAY SERVICE CREATION COMPLETE")
    print("="*60)
    print(f"Service Project: {svc_root}")
    print(f"Install Script: {install_script}")
    print(f"Uninstall Script: {uninstall_script}")
    print(f"WiX Fragment: {wxs_file}")
    print("\nNext steps:")
    print("1. Run: dotnet build Services\\EngineGateway.ServiceHost\\EngineGateway.ServiceHost.csproj")
    print("2. Run: scripts\\Install-EngineGatewayService.ps1")
    print("3. Service will auto-start and manage the Python engine gateway")

if __name__ == "__main__":
    create_engine_gateway_service()
