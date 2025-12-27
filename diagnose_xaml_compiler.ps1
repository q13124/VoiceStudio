# XAML Compiler Diagnostic Script
# Captures file operations and compiler behavior

param(
  [switch]$CheckTimestamps,
  [switch]$TestMinimal,
  [switch]$FullDiagnostic
)

$ErrorActionPreference = "Continue"

Write-Host "=== XAML Compiler Diagnostic Script ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check file timestamps
if ($CheckTimestamps -or $FullDiagnostic) {
  Write-Host "1. Checking file timestamps..." -ForegroundColor Yellow
  $objDir = "src\VoiceStudio.App\obj\x64\Debug\net8.0-windows10.0.19041.0"
    
  $gicsFiles = Get-ChildItem -Path $objDir -Filter "*.g.i.cs" -Recurse | Select-Object -First 5
  $gcsFiles = Get-ChildItem -Path $objDir -Filter "*.g.cs" -Recurse | Select-Object -First 5
    
  Write-Host "`n.g.i.cs files (Pass 1 output):" -ForegroundColor Cyan
  $gicsFiles | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Length) bytes, Modified: $($_.LastWriteTime)" -ForegroundColor $(if ($_.Length -gt 0) { "Green" } else { "Red" })
  }
    
  Write-Host "`n.g.cs files (Pass 2 output):" -ForegroundColor Cyan
  $gcsFiles | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Length) bytes, Modified: $($_.LastWriteTime)" -ForegroundColor $(if ($_.Length -gt 0) { "Green" } else { "Red" })
  }
    
  # Compare timestamps
  $appGics = Get-Item "$objDir\App.g.i.cs" -ErrorAction SilentlyContinue
  $appGcs = Get-Item "$objDir\App.g.cs" -ErrorAction SilentlyContinue
    
  if ($appGics -and $appGcs) {
    $timeDiff = ($appGcs.LastWriteTime - $appGics.LastWriteTime).TotalSeconds
    Write-Host "`nTimestamp Analysis:" -ForegroundColor Cyan
    Write-Host "  App.g.i.cs: $($appGics.LastWriteTime)" -ForegroundColor Gray
    Write-Host "  App.g.cs:   $($appGcs.LastWriteTime)" -ForegroundColor Gray
    Write-Host "  Difference: $([Math]::Round($timeDiff, 2)) seconds" -ForegroundColor $(if ($timeDiff -lt 1) { "Yellow" } else { "Green" })
        
    if ($timeDiff -lt 1 -and $appGcs.Length -eq 0) {
      Write-Host "  ⚠️  Files created simultaneously but .g.cs is empty - likely Pass 2 failure" -ForegroundColor Red
    }
  }
}

# 2. Test minimal XAML compilation
if ($TestMinimal -or $FullDiagnostic) {
  Write-Host "`n2. Testing minimal XAML compilation..." -ForegroundColor Yellow
    
  $testDir = "temp\xaml_test"
  if (-not (Test-Path $testDir)) {
    New-Item -ItemType Directory -Path $testDir -Force | Out-Null
  }
    
  # Create minimal test XAML
  $testXaml = @"
<Page x:Class="TestApp.TestPage"
      xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
      xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <Grid>
        <TextBlock Text="Test"/>
    </Grid>
</Page>
"@
    
  $testXamlPath = "$testDir\TestPage.xaml"
  $testXaml | Out-File -FilePath $testXamlPath -Encoding UTF8 -Force
    
  Write-Host "  Created test XAML: $testXamlPath" -ForegroundColor Green
  Write-Host "  Note: Full test requires creating input.json - skipping for now" -ForegroundColor Yellow
}

# 3. Check compiler executable details
if ($FullDiagnostic) {
  Write-Host "`n3. Compiler executable details..." -ForegroundColor Yellow
    
  $xcPath = "C:\Users\Tyler\.nuget\packages\microsoft.windowsappsdk.winui\1.8.251105000\tools\net472\XamlCompiler.exe"
    
  if (Test-Path $xcPath) {
    $fileInfo = Get-Item $xcPath
    $versionInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($xcPath)
        
    Write-Host "  Path: $xcPath" -ForegroundColor Gray
    Write-Host "  Size: $($fileInfo.Length) bytes" -ForegroundColor Gray
    Write-Host "  Version: $($versionInfo.FileVersion)" -ForegroundColor Gray
    Write-Host "  Product: $($versionInfo.ProductName)" -ForegroundColor Gray
    Write-Host "  Modified: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
  }
}

# 4. Check input.json structure
if ($FullDiagnostic) {
  Write-Host "`n4. Checking input.json structure..." -ForegroundColor Yellow
    
  $inputJson = "src\VoiceStudio.App\obj\x64\Debug\net8.0-windows10.0.19041.0\input.json"
    
  if (Test-Path $inputJson) {
    try {
      $json = Get-Content $inputJson -Raw | ConvertFrom-Json
            
      Write-Host "  XamlFiles: $($json.XamlFiles.Count)" -ForegroundColor Gray
      Write-Host "  ReferenceAssemblies: $($json.ReferenceAssemblies.Count)" -ForegroundColor Gray
      Write-Host "  OutputPath: $($json.OutputPath)" -ForegroundColor Gray
            
      # Check for missing files
      $missingFiles = @()
      foreach ($xamlFile in $json.XamlFiles) {
        if (-not (Test-Path $xamlFile)) {
          $missingFiles += $xamlFile
        }
      }
            
      if ($missingFiles.Count -gt 0) {
        Write-Host "  ⚠️  Found $($missingFiles.Count) missing XAML files!" -ForegroundColor Red
        $missingFiles | Select-Object -First 5 | ForEach-Object {
          Write-Host "    - $_" -ForegroundColor Red
        }
      }
      else {
        Write-Host "  ✅ All XAML files exist" -ForegroundColor Green
      }
    }
    catch {
      Write-Host "  ❌ Error parsing input.json: $_" -ForegroundColor Red
    }
  }
}

# 5. Check output.json for errors
if ($FullDiagnostic) {
  Write-Host "`n5. Checking output.json for errors..." -ForegroundColor Yellow
    
  $outputJson = "src\VoiceStudio.App\obj\x64\Debug\net8.0-windows10.0.19041.0\output.json"
    
  if (Test-Path $outputJson) {
    try {
      $json = Get-Content $outputJson -Raw | ConvertFrom-Json
            
      Write-Host "  GeneratedCodeFiles: $($json.GeneratedCodeFiles.Count)" -ForegroundColor Gray
            
      # Check MSBuildLogEntries for errors
      if ($json.MSBuildLogEntries) {
        $errors = $json.MSBuildLogEntries | Where-Object { $_.ErrorCode -ne $null }
        if ($errors) {
          Write-Host "  ⚠️  Found $($errors.Count) errors in log entries!" -ForegroundColor Red
          $errors | Select-Object -First 5 | ForEach-Object {
            Write-Host "    ErrorCode: $($_.ErrorCode), Message: $($_.Message)" -ForegroundColor Red
          }
        }
        else {
          Write-Host "  ✅ No errors in log entries" -ForegroundColor Green
        }
      }
    }
    catch {
      Write-Host "  ❌ Error parsing output.json: $_" -ForegroundColor Red
    }
  }
}

Write-Host "`n=== Diagnostic Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run Process Monitor during build to capture file operations" -ForegroundColor White
Write-Host "2. Check if files are written then cleared (antivirus?)" -ForegroundColor White
Write-Host "3. Try compiling a single XAML file to isolate the issue" -ForegroundColor White
Write-Host "4. Check for WinUI SDK 1.8.251105000 known issues" -ForegroundColor White

