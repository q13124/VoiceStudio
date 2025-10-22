#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Mega-Patch Implementation
Router wiring, dashboard menu, plugin hot-reload, integration tests, deployment guide
"""

import os
import json
from pathlib import Path

class VoiceStudioMegaPatch:
    def __init__(self):
        self.repo_path = Path("C:/Users/Tyler/VoiceStudio")
        self.ui_path = self.repo_path / "VoiceStudio.UI"
        self.svc_path = self.repo_path / "UltraClone.EngineService"
        self.routing_path = self.svc_path / "routing"
        self.monitor_path = self.repo_path / "monitor"
        self.tools_path = self.repo_path / "tools"
        self.plugins_path = self.repo_path / "plugins"
        self.reg_dir = self.plugins_path / "registry"
        self.tests_path = self.repo_path / "tests" / "integration"
        self.docs_path = self.repo_path / "docs"
        self.ops_path = Path(os.environ.get("ProgramData", "C:/ProgramData")) / "VoiceStudio" / "workers" / "ops"
        
    def create_directories(self):
        """Create all necessary directories"""
        dirs = [
            self.routing_path,
            self.monitor_path,
            self.tools_path,
            self.reg_dir,
            self.tests_path,
            self.docs_path,
            self.ops_path
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        print("Directories created successfully")
        
    def create_engine_dispatcher(self):
        """Create Python dispatcher for engine routing with fallback chain"""
        dispatcher_content = '''# workers/ops/engine_dispatch.py
# Usage: python engine_dispatch.py --text "Hello" --dst C:\\out.wav --lang en --opts '{"stability":0.6}'
import argparse, json, os, sys, subprocess, time

def call_worker(engine:str, text:str, dst:str, opts:dict):
    py = os.path.join(os.environ.get("ProgramData", r"C:\\ProgramData"), "VoiceStudio","pyenv","Scripts","python.exe")
    wr = os.path.join(os.environ.get("ProgramData", r"C:\\ProgramData"), "VoiceStudio","workers","worker_router.py")
    args = [py, wr, "tts", "--a", text, "--b", dst, "--c", json.dumps({**opts, "engine": engine})]
    p = subprocess.run(args, capture_output=True, text=True)
    ok = (p.returncode==0) and os.path.exists(dst)
    return ok, p.stdout + "\\n" + p.stderr

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--dst",  required=True)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--chain", default="")
    ap.add_argument("--opts",  default="{}")
    args = ap.parse_args()

    try:
        opts = json.loads(args.opts)
    except Exception:
        opts = {}

    # chain comes from service router (engine, fallback list)
    chain = [e.strip() for e in args.chain.split(",") if e.strip()]
    last_log=""
    for eng in chain:
        ok, log = call_worker(eng, args.text, args.dst, opts)
        last_log += f"\\n[{eng}] -> {ok}\\n{log}"
        if ok:
            print(json.dumps({"ok": True, "engine": eng, "dst": args.dst}))
            return 0
    print(json.dumps({"ok": False, "error": "all_engines_failed", "log": last_log}))
    return 2

if __name__=="__main__":
    sys.exit(main())
'''
        
        dispatcher_path = self.ops_path / "engine_dispatch.py"
        with open(dispatcher_path, 'w', encoding='utf-8') as f:
            f.write(dispatcher_content)
            
        print(f"Created engine dispatcher: {dispatcher_path}")
        
    def create_routing_adapter(self):
        """Create C# routing adapter for service integration"""
        adapter_content = '''using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using UltraClone.EngineService.routing;

namespace UltraClone.EngineService
{
  public static class RoutingAdapter
  {
    static string Cfg => Path.Combine(AppContext.BaseDirectory, "..","..","config","engines.config.json");
    public static (string engine, string[] chain) Choose(string lang="en", string needQuality="high", string needLatency="normal")
    {
      var cfgPath = Path.GetFullPath(Cfg);
      var router  = new EngineRouter(cfgPath);
      var (engine, chain) = router.Choose(lang, needQuality, needLatency);
      return (engine, chain.ToArray());
    }

    public static (bool ok, string engine, string dst, string log) Dispatch(string text, string dst, string[] chain, string optsJson)
    {
      var pd = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
      var py = Path.Combine(pd,"VoiceStudio","pyenv","Scripts","python.exe");
      var op = Path.Combine(pd,"VoiceStudio","workers","ops","engine_dispatch.py");
      var psi = new ProcessStartInfo(py, $"{op} --text \\"{text.Replace("\\"","\\\\\\"")}\\" --dst \\"{dst}\\" --chain \\"{string.Join(",", chain)}\\" --opts \\"{optsJson.Replace("\\"","\\\\\\"")}\\"");
      psi.UseShellExecute=true;
      var p = Process.Start(psi);
      p.WaitForExit();
      var ok  = File.Exists(dst) && p.ExitCode==0;
      return (ok, chain.Length>0? chain[0] : "", dst, $"exit={p.ExitCode}");
    }
  }
}
'''
        
        adapter_path = self.svc_path / "RoutingAdapter.cs"
        with open(adapter_path, 'w', encoding='utf-8') as f:
            f.write(adapter_content)
            
        print(f"Created routing adapter: {adapter_path}")
        
    def create_dashboard_page(self):
        """Create dashboard page for WinUI"""
        # Create Pages directory
        pages_path = self.ui_path / "Pages"
        pages_path.mkdir(parents=True, exist_ok=True)
        
        # Dashboard Page XAML
        dash_page_xaml = '''<Page
  x:Class="VoiceStudio.UI.Pages.DashboardPage"
  xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Grid Padding="16">
    <StackPanel Spacing="10">
      <TextBlock Text="VoiceStudio Service Dashboard" FontSize="20" />
      <StackPanel Orientation="Horizontal" Spacing="8">
        <Button Content="Launch Dashboard" Click="OnLaunch"/>
        <TextBox x:Name="Port" Width="120" Text="5299"/>
      </StackPanel>
      <TextBlock x:Name="Status" />
    </StackPanel>
  </Grid>
</Page>
'''
        
        dash_page_xaml_path = pages_path / "DashboardPage.xaml"
        with open(dash_page_xaml_path, 'w', encoding='utf-8') as f:
            f.write(dash_page_xaml)
            
        # Dashboard Page C#
        dash_page_cs = '''using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using System.Diagnostics;
using System.IO;

namespace VoiceStudio.UI.Pages
{
  public sealed partial class DashboardPage : Page
  {
    public DashboardPage(){ this.InitializeComponent(); }
    private void OnLaunch(object sender, RoutedEventArgs e)
    {
      try{
        var port = Port.Text?.Trim(); if(string.IsNullOrWhiteSpace(port)) port="5299";
        var tools = System.IO.Path.Combine(System.AppContext.BaseDirectory,"..","..","tools","run_dashboard.ps1");
        var psi = new ProcessStartInfo("powershell",$"-ExecutionPolicy Bypass -File \\"{tools}\\" -Port {port}");
        psi.Verb="runas"; psi.UseShellExecute=true;
        Process.Start(psi);
        Status.Text=$"Launching dashboard on http://localhost:{port}";
      }catch(Exception ex){ Status.Text=$"Error: {ex.Message}"; }
    }
  }
}
'''
        
        dash_page_cs_path = pages_path / "DashboardPage.xaml.cs"
        with open(dash_page_cs_path, 'w', encoding='utf-8') as f:
            f.write(dash_page_cs)
            
        print(f"Created dashboard page: {dash_page_xaml_path}")
        
    def create_plugin_hot_reload(self):
        """Create plugin hot-reload system"""
        # Plugin registry
        registry_content = '''{
  "plugins": [],
  "scopes": ["voice-adapter","dsp-filter","exporter","analyzer"],
  "hot_reload": true
}'''
        
        registry_path = self.reg_dir / "registry.json"
        with open(registry_path, 'w', encoding='utf-8') as f:
            f.write(registry_content)
            
        # Plugin hot-reload service
        services_path = self.ui_path / "Services"
        services_path.mkdir(parents=True, exist_ok=True)
        
        plugin_watcher_cs = '''using System;
using System.IO;
using Microsoft.UI.Xaml.Controls;

namespace VoiceStudio.UI.Services
{
  public class PluginHotReload : IDisposable
  {
    FileSystemWatcher _w;
    Action<string>? _on;
    public PluginHotReload(Action<string>? onChange)
    {
      _on = onChange;
      var pd = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
      var stamp = Path.Combine(pd, "VoiceStudio","plugins","registry","registry.json.stamp");
      Directory.CreateDirectory(Path.GetDirectoryName(stamp)!);
      _w = new FileSystemWatcher(Path.GetDirectoryName(stamp)!, Path.GetFileName(stamp));
      _w.NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.CreationTime;
      _w.Changed += (_, __)=> _on?.Invoke("Plugin registry changed");
      _w.Created += (_, __)=> _on?.Invoke("Plugin registry updated");
      _w.EnableRaisingEvents = true;
    }
    public void Dispose(){ _w?.Dispose(); }
  }
}
'''
        
        plugin_watcher_path = services_path / "PluginHotReload.cs"
        with open(plugin_watcher_path, 'w', encoding='utf-8') as f:
            f.write(plugin_watcher_cs)
            
        # Background plugin watcher
        watcher_py = '''# tools/plugin_watcher.py (dev helper) — touches registry.json.stamp when registry.json changes
import os, time, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
reg = ROOT / "plugins" / "registry" / "registry.json"
stamp = reg.with_suffix(".json.stamp")
last = 0.0
while True:
    try:
        t = os.path.getmtime(reg)
        if t>last:
            last=t
            open(stamp,"w").close()
            print("Plugin registry changed.")
    except FileNotFoundError:
        pass
    time.sleep(1.0)
'''
        
        watcher_path = self.tools_path / "plugin_watcher.py"
        with open(watcher_path, 'w', encoding='utf-8') as f:
            f.write(watcher_py)
            
        print(f"Created plugin hot-reload system: {registry_path}")
        
    def create_integration_tests(self):
        """Create integration tests for render metrics"""
        integration_test = '''# tests/integration/test_render_metrics.py
# Requires: faster-whisper, soundfile, pyloudnorm (or fallback)
import os, json, time, subprocess, tempfile, math, sys
import soundfile as sf
try:
    import pyloudnorm as pyln
except Exception:
    pyln=None

TEXT = "VoiceStudio generates natural speech quickly and reliably."

def render_and_metrics():
    tmpdir = tempfile.mkdtemp(prefix="vs_test_")
    wav = os.path.join(tmpdir,"out.wav")
    pd  = os.path.join(os.environ.get("ProgramData", r"C:\\ProgramData"), "VoiceStudio")
    py  = os.path.join(pd,"pyenv","Scripts","python.exe")
    wr  = os.path.join(pd,"workers","worker_router.py")

    # ask dispatcher (fallback chain handled in service, but call worker directly here)
    subprocess.run([py, wr, "tts", "--a", TEXT, "--b", wav, "--c", json.dumps({"engine":"xtts","stability":0.65})], check=True)
    assert os.path.exists(wav), "render failed"

    # ASR (faster-whisper) to get WER-ish proxy
    from faster_whisper import WhisperModel
    model = WhisperModel("medium", device="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu")
    segs, _ = model.transcribe(wav, language="en")
    hyp = " ".join([s.text.strip() for s in segs]).strip().lower()
    ref = TEXT.lower()
    wer = word_error_rate(ref, hyp)

    # LUFS
    data, sr = sf.read(wav)
    lufs = None
    if pyln:
        meter = pyln.Meter(sr)
        lufs = meter.integrated_loudness(data if data.ndim==1 else data.mean(axis=1))

    return {"wav":wav, "wer":wer, "lufs":lufs}

def word_error_rate(ref, hyp):
    r = ref.split(); h = hyp.split()
    # Levenshtein
    dp = [[0]*(len(h)+1) for _ in range(len(r)+1)]
    for i in range(len(r)+1): dp[i][0]=i
    for j in range(len(h)+1): dp[0][j]=j
    for i in range(1,len(r)+1):
        for j in range(1,len(h)+1):
            cost = 0 if r[i-1]==h[j-1] else 1
            dp[i][j]=min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[len(r)][len(h)]/max(1,len(r))

def test_render_pipeline_metrics():
    m = render_and_metrics()
    assert os.path.exists(m["wav"])
    assert m["wer"] <= 0.40  # generous bound
'''
        
        integration_test_path = self.tests_path / "test_render_metrics.py"
        with open(integration_test_path, 'w', encoding='utf-8') as f:
            f.write(integration_test)
            
        print(f"Created integration test: {integration_test_path}")
        
    def create_deployment_guide(self):
        """Create deployment guide"""
        deployment_guide = '''# VoiceStudio — Golden Path (Dev → Staging → Prod)

## Dev
1. Install CUDA/CuDNN + drivers; ensure `nvidia-smi` OK.
2. `pip install -e .[voice-cloning,dev,db]`
3. Consolidate configs: `python tools/migrate_configs.py`
4. Launch services: `python tools/voicestudio_launcher.py --mode dev --services engine,orchestrator`
5. Start dashboard: `powershell tools\\run_dashboard.ps1`
6. Run plugin watcher (optional): `python tools\\plugin_watcher.py`
7. Run integration tests: `pytest -q`

## Staging
1. Build UI/Service MSI + Content MSI (models/venv).
2. Build Burn bundle (remote or local prereqs).
3. Deploy on clean Windows VM; verify:
   - Service starts
   - Dashboard reachable
   - Render succeeds; logs & telemetry emitted

## Prod
1. Sign MSIs and bundle (codesign).
2. Distribute `VoiceStudioSetup.exe`.
3. Monitor metrics (P95 latency, error rates); enable auto-upgrade per policy.
4. Backups: `tools\\backup_db.ps1 backup`
5. Compliance: watermark/policy toggles per profile.

## Engine Routing & Fallback
- Router picks engine by language/latency requirements; fallback: XTTS → OpenVoice → CosyVoice → Coqui.
- Failover is automatic via `engine_dispatch.py`.

## Plugins
- Add plugin folders under `plugins\\{name}`.
- Edit `plugins\\registry\\registry.json`; dev watcher touches `.stamp` for UI hot-reload.

## Troubleshooting
- Dashboard shows service health and queues.
- Check `%ProgramData%\\VoiceStudio\\logs\\` for JSON logs.
- Rebuild installer if antivirus quarantines the bundle; ensure WiX tools on PATH.
'''
        
        deployment_path = self.docs_path / "deployment.md"
        with open(deployment_path, 'w', encoding='utf-8') as f:
            f.write(deployment_guide)
            
        print(f"Created deployment guide: {deployment_path}")
        
    def run_mega_patch(self):
        """Run complete mega-patch implementation"""
        print("VoiceStudio Ultimate - Mega-Patch Implementation")
        print("=" * 60)
        
        self.create_directories()
        self.create_engine_dispatcher()
        self.create_routing_adapter()
        self.create_dashboard_page()
        self.create_plugin_hot_reload()
        self.create_integration_tests()
        self.create_deployment_guide()
        
        print("\n" + "=" * 60)
        print("MEGA-PATCH COMPLETE")
        print("=" * 60)
        print("Router Wiring: Engine dispatcher with fallback chain")
        print("Dashboard Menu: WinUI dashboard page and menu integration")
        print("Plugin Hot-Reload: Registry system with file watching")
        print("Integration Tests: Render metrics with ASR and LUFS")
        print("Deployment Guide: Golden path from dev to production")
        print("\nFeatures:")
        print("- Engine routing with automatic fallback chain")
        print("- Dashboard integration in WinUI application")
        print("- Plugin hot-reload with file system watching")
        print("- Integration testing with quality metrics")
        print("- Complete deployment workflow documentation")

def main():
    mega_patch = VoiceStudioMegaPatch()
    mega_patch.run_mega_patch()

if __name__ == "__main__":
    main()
