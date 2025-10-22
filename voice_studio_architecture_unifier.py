#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Architecture Unification System
Unified launcher, configs, router, dashboard, plugin registry, and operations
"""

import os
import json
import subprocess
from pathlib import Path


class VoiceStudioArchitectureUnifier:
    def __init__(self):
        self.repo_path = Path("C:/Users/Tyler/VoiceStudio")
        self.tools_path = self.repo_path / "tools"
        self.config_path = self.repo_path / "config"
        self.common_path = self.repo_path / "common"
        self.svc_path = self.repo_path / "UltraClone.EngineService"
        self.routing_path = self.svc_path / "routing"
        self.plugins_path = self.repo_path / "plugins"
        self.plugreg_path = self.plugins_path / "registry"
        self.db_path = self.repo_path / "db"
        self.alembic_path = self.db_path / "alembic"
        self.vers_path = self.alembic_path / "versions"
        self.tests_path = self.repo_path / "tests"
        self.ghwf_path = self.repo_path / ".github" / "workflows"
        self.monitor_path = self.repo_path / "monitor"
        self.tele_path = self.monitor_path / "telemetry"

    def create_directories(self):
        """Create all necessary directories"""
        dirs = [
            self.tools_path,
            self.config_path,
            self.common_path,
            self.routing_path,
            self.plugreg_path,
            self.db_path,
            self.alembic_path,
            self.vers_path,
            self.tests_path,
            self.ghwf_path,
            self.monitor_path,
            self.tele_path,
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

        print("Architecture directories created successfully")

    def create_unified_launcher(self):
        """Create unified launcher for dev/prod modes"""
        launcher_content = '''#!/usr/bin/env python
# tools/voicestudio_launcher.py
"""
Single entry for dev/prod:
  python tools/voicestudio_launcher.py --mode dev
  python tools/voicestudio_launcher.py --mode prod --services assistant,orchestrator,engine
  python tools/voicestudio_launcher.py --health-check
"""
import argparse, subprocess, sys, os, json, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG = os.path.join(ROOT, "config", "voicestudio.config.json")
ENG = os.path.join(ROOT, "config", "engines.config.json")
DEP = os.path.join(ROOT, "config", "deployment.config.json")

def load(p):
    with open(p,"r",encoding="utf-8") as f: return json.load(f)

def health():
    # best-effort: ping service health endpoints (customize)
    import urllib.request
    urls = [
        "http://127.0.0.1:5188/health",
        "http://127.0.0.1:5188/engines",
    ]
    ok = True
    for u in urls:
        try:
            with urllib.request.urlopen(u, timeout=3) as r:
                if r.status!=200: ok=False
        except Exception:
            ok=False
    print("healthy" if ok else "unhealthy")
    return 0 if ok else 1

def start_dev(svcs):
    # Dev: start orchestrator & engine in-tree; UI manually via dotnet run if needed
    env = os.environ.copy()
    dep = load(DEP)
    port = dep.get("service_port", 5188)
    cmds=[]
    if "engine" in svcs:
        cmds.append([sys.executable, os.path.join(dep.get("programdata","C:/ProgramData/VoiceStudio"), "workers","worker_router.py"), "serve", f"--port={port}"])
    if "orchestrator" in svcs:
        cmds.append([sys.executable, os.path.join(ROOT,"tools","orchestrator_stub.py"), "--port", str(port+1)])
    procs = [subprocess.Popen(c) for c in cmds]
    try:
        for p in procs: p.wait()
    finally:
        for p in procs:
            if p.poll() is None: p.terminate()

def start_prod():
    # Prod: rely on installed Windows Service + UI
    print("Starting Windows Service (VoiceStudio.Engine)...")
    subprocess.run(["sc","start","VoiceStudio.Engine"], check=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dev","prod"], default="dev")
    ap.add_argument("--services", default="engine,orchestrator")
    ap.add_argument("--health-check", action="store_true")
    args = ap.parse_args()
    if args.health_check:
        sys.exit(health())
    if args.mode=="dev":
        svcs = [s.strip() for s in args.services.split(",") if s.strip()]
        return start_dev(svcs)
    else:
        return start_prod()

if __name__=="__main__":
    sys.exit(main())'''

        launcher_path = self.tools_path / "voicestudio_launcher.py"
        with open(launcher_path, "w", encoding="utf-8") as f:
            f.write(launcher_content)

        print(f"Created Unified Launcher: {launcher_path}")

    def create_config_files(self):
        """Create consolidated configuration files"""
        # Main VoiceStudio config
        vs_config = {
            "$schema": "https://example.com/voicestudio.schema.json",
            "programdata": "C:/ProgramData/VoiceStudio",
            "service_port": 5188,
            "ui": {"theme": "dark", "language": "en-US"},
            "logging": {"level": "Information", "json": True},
            "features": {"plugin_hot_reload": True, "dashboard_default": True},
        }

        vs_config_path = self.config_path / "voicestudio.config.json"
        with open(vs_config_path, "w", encoding="utf-8") as f:
            json.dump(vs_config, f, indent=2)

        print(f"Created VoiceStudio Config: {vs_config_path}")

        # Engines config
        engines_config = {
            "$schema": "https://example.com/engines.schema.json",
            "routing_policy": {
                "prefer": {
                    "en": "xtts",
                    "ja": "cosyvoice2",
                    "zh": "cosyvoice2",
                    "multi": "openvoice",
                },
                "fallback": ["xtts", "openvoice", "cosyvoice2", "coqui"],
            },
            "xtts": {
                "provider": "local",
                "model_dir": "%ProgramData%/VoiceStudio/models/xtts",
            },
            "openvoice": {
                "provider": "local",
                "model_dir": "%ProgramData%/VoiceStudio/models/openvoice",
            },
            "cosyvoice2": {
                "provider": "local",
                "model_dir": "%ProgramData%/VoiceStudio/models/cosyvoice2",
            },
            "coqui": {
                "provider": "local",
                "model_dir": "%ProgramData%/VoiceStudio/models/coqui",
            },
            "whisper": {
                "provider": "local",
                "model_dir": "%ProgramData%/VoiceStudio/models/whisper",
            },
            "pyannote": {
                "provider": "local",
                "model_dir": "%ProgramData%/VoiceStudio/models/pyannote",
            },
        }

        engines_config_path = self.config_path / "engines.config.json"
        with open(engines_config_path, "w", encoding="utf-8") as f:
            json.dump(engines_config, f, indent=2)

        print(f"Created Engines Config: {engines_config_path}")

        # Deployment config
        deployment_config = {
            "$schema": "https://example.com/deployment.schema.json",
            "environment": "dev",
            "service_port": 5188,
            "gpu": {"allow_mixed_precision": True, "min_free_mb": 512},
            "paths": {
                "programdata": "C:/ProgramData/VoiceStudio",
                "logs": "C:/ProgramData/VoiceStudio/logs",
                "telemetry": "C:/ProgramData/VoiceStudio/telemetry",
            },
        }

        deployment_config_path = self.config_path / "deployment.config.json"
        with open(deployment_config_path, "w", encoding="utf-8") as f:
            json.dump(deployment_config, f, indent=2)

        print(f"Created Deployment Config: {deployment_config_path}")

    def create_config_migrator(self):
        """Create config migration tool"""
        migrator_content = """# tools/migrate_configs.py — merges legacy configs into 3 canonical files.
import json, os, glob, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG = os.path.join(ROOT,"config")
LEGACY = os.path.join(CFG,"legacy")
os.makedirs(LEGACY, exist_ok=True)
def load(path):
    try:
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    except Exception: return {}
agg = {}
for f in glob.glob(os.path.join(CFG,"*.json")):
    if os.path.basename(f) in ("voicestudio.config.json","engines.config.json","deployment.config.json"):
        continue
    base=os.path.basename(f)
    agg[base]=load(f)
    os.replace(f, os.path.join(LEGACY, base))
# naive merge (extend as needed)
vs=json.load(open(os.path.join(CFG,"voicestudio.config.json"),"r",encoding="utf-8"))
eng=json.load(open(os.path.join(CFG,"engines.config.json"),"r",encoding="utf-8"))
dep=json.load(open(os.path.join(CFG,"deployment.config.json"),"r",encoding="utf-8"))
vs["legacy_merge"]={"files":list(agg.keys())}
json.dump(vs, open(os.path.join(CFG,"voicestudio.config.json"),"w",encoding="utf-8"), indent=2)
json.dump(eng, open(os.path.join(CFG,"engines.config.json"),"w",encoding="utf-8"), indent=2)
json.dump(dep, open(os.path.join(CFG,"deployment.config.json"),"w",encoding="utf-8"), indent=2)
print("Legacy configs moved to config/legacy and canonical files refreshed.")"""

        migrator_path = self.tools_path / "migrate_configs.py"
        with open(migrator_path, "w", encoding="utf-8") as f:
            f.write(migrator_content)

        print(f"Created Config Migrator: {migrator_path}")

    def create_engine_router(self):
        """Create engine routing system"""
        router_content = """# UltraClone.EngineService/routing/engine_router.py
# Selects best engine by language, quality, speed; provides fallback & A/B hooks.
import json, os

class EngineRouter:
    def __init__(self, engines_cfg_path):
        with open(engines_cfg_path,"r",encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.policy = self.cfg.get("routing_policy", {})

    def choose(self, lang="en", need_quality="high", need_latency="normal"):
        prefer = self.policy.get("prefer", {})
        primary = prefer.get(lang, prefer.get("multi","xtts"))
        chain = [primary]+[e for e in self.policy.get("fallback",[]) if e!=primary]
        # simple latency-based tweak
        if need_latency=="ultra":
            chain = [e for e in chain if e in ("openvoice","xtts")] + [e for e in chain if e not in ("openvoice","xtts")]
        return chain[0], chain

# Example usage inside your TTS endpoint: router.choose(lang)"""

        router_path = self.routing_path / "engine_router.py"
        with open(router_path, "w", encoding="utf-8") as f:
            f.write(router_content)

        print(f"Created Engine Router: {router_path}")

    def create_dashboard_runner(self):
        """Create dashboard runner script"""
        dashboard_content = """# tools/run_dashboard.ps1
param([int]$Port=5299)
$ErrorActionPreference='Stop'
$root = Split-Path $PSCommandPath -Parent
$dash = Join-Path (Split-Path $root -Parent) "monitor\\service_health_dashboard_enhanced.py"
if(!(Test-Path $dash)){ throw "Dashboard not found: $dash" }
$py = Join-Path $env:ProgramData "VoiceStudio\\pyenv\\Scripts\\python.exe"
& $py $dash --port $Port"""

        dashboard_path = self.tools_path / "run_dashboard.ps1"
        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(dashboard_content)

        print(f"Created Dashboard Runner: {dashboard_path}")

    def create_plugin_registry(self):
        """Create plugin registry system"""
        registry_content = {
            "plugins": [],
            "scopes": ["voice-adapter", "dsp-filter", "exporter", "analyzer"],
            "hot_reload": True,
        }

        registry_path = self.plugreg_path / "registry.json"
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(registry_content, f, indent=2)

        print(f"Created Plugin Registry: {registry_path}")

        # Plugin watcher
        watcher_content = """# tools/plugin_watcher.py — reloads registry on change; signals UI via file touch/websocket
import os, time, json, pathlib
REG = os.path.join(pathlib.Path(__file__).resolve().parents[1], "plugins","registry","registry.json")
STAMP = REG + ".stamp"
def main():
    last = 0
    while True:
        try:
            t = os.path.getmtime(REG)
            if t>last:
                last=t
                open(STAMP,"w").close()
                print("Plugin registry changed; stamp touched.")
        except Exception: pass
        time.sleep(1.0)
if __name__=="__main__":
    main()"""

        watcher_path = self.tools_path / "plugin_watcher.py"
        with open(watcher_path, "w", encoding="utf-8") as f:
            f.write(watcher_content)

        print(f"Created Plugin Watcher: {watcher_path}")

    def create_common_errors(self):
        """Create common error definitions"""
        errors_content = """# common/errors.py
class VoiceStudioError(Exception): pass
class EngineNotAvailableError(VoiceStudioError): pass
class AudioProcessingError(VoiceStudioError): pass
class PolicyViolationError(VoiceStudioError): pass"""

        errors_path = self.common_path / "errors.py"
        with open(errors_path, "w", encoding="utf-8") as f:
            f.write(errors_content)

        print(f"Created Common Errors: {errors_path}")

    def create_database_system(self):
        """Create Alembic database system"""
        # alembic.ini
        alembic_ini = """[alembic]
script_location = db/alembic
sqlalchemy.url = sqlite:///voicestudio.db"""

        alembic_ini_path = self.db_path / "alembic.ini"
        with open(alembic_ini_path, "w", encoding="utf-8") as f:
            f.write(alembic_ini)

        print(f"Created Alembic Config: {alembic_ini_path}")

        # env.py
        env_content = """from alembic import context
from sqlalchemy import engine_from_config, pool
config = context.config
target_metadata = None
def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"), literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.', poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()"""

        env_path = self.alembic_path / "env.py"
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)

        print(f"Created Alembic Env: {env_path}")

        # Versions README
        versions_readme = """# db/alembic/versions/README.md
# Create a migration:
#   alembic revision -m "init tables"
# Apply:
#   alembic upgrade head"""

        versions_readme_path = self.vers_path / "README.md"
        with open(versions_readme_path, "w", encoding="utf-8") as f:
            f.write(versions_readme)

        print(f"Created Versions README: {versions_readme_path}")

        # Backup utility
        backup_content = """# tools/backup_db.ps1 — quick backup/restore
param([ValidateSet("backup","restore")][string]$Mode="backup",[string]$Path="voicestudio.db")
$ErrorActionPreference='Stop'
$pd = Join-Path $env:ProgramData "VoiceStudio"
$src = Join-Path $pd $Path
$bak = Join-Path $pd ("backup_"+(Get-Date -Format yyyyMMdd_HHmmss)+"_"+$Path)
if($Mode -eq "backup"){ Copy-Item $src $bak -Force; Write-Host "Backup -> $bak" }
else { Copy-Item $Path $src -Force; Write-Host "Restored $Path -> $src" }"""

        backup_path = self.tools_path / "backup_db.ps1"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(backup_content)

        print(f"Created DB Backup Utility: {backup_path}")

    def create_pyproject_toml(self):
        """Create pyproject.toml with optional dependencies"""
        pyproject_content = """[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "voicestudio"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.29",
  "pydantic>=2.6",
  "python-dotenv>=1.0",
  "loguru>=0.7"
]

[project.optional-dependencies]
voice-cloning = [
  "torch>=2.4.0",
  "torchaudio>=2.4.0",
  "nvidia-ml-py3",
  "soundfile",
  "onnxruntime-gpu>=1.18.0",
  "faster-whisper>=1.0.0",
  "pyannote-audio>=3.3"
]
services = ["requests","websockets"]
dev = ["pytest","pytest-asyncio","mypy","ruff","httpx","coverage","pytest-benchmark"]
db = ["SQLAlchemy>=2.0","alembic>=1.13"]"""

        pyproject_path = self.repo_path / "pyproject.toml"
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(pyproject_content)

        print(f"Created PyProject TOML: {pyproject_path}")

    def create_tests_and_ci(self):
        """Create test suite and CI configuration"""
        # Test router
        test_content = """# tests/test_router.py
from UltraClone.EngineService.routing.engine_router import EngineRouter
import os, json
def test_choose_en_xtts(tmp_path):
    cfg = tmp_path/"eng.json"
    cfg.write_text(json.dumps({"routing_policy":{"prefer":{"en":"xtts"},"fallback":["openvoice","cosyvoice2","coqui"]}}))
    r=EngineRouter(str(cfg))
    e,chain = r.choose("en")
    assert e=="xtts" and "openvoice" in chain"""

        test_path = self.tests_path / "test_router.py"
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_content)

        print(f"Created Test Suite: {test_path}")

        # CI workflow
        ci_content = """# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.10" }
      - name: Install project
        run: |
          python -m pip install -U pip
          pip install -e .[dev,db]
      - name: Run tests
        run: |
          pytest -q"""

        ci_path = self.ghwf_path / "ci.yml"
        with open(ci_path, "w", encoding="utf-8") as f:
            f.write(ci_content)

        print(f"Created CI Workflow: {ci_path}")

    def create_telemetry_system(self):
        """Create telemetry and monitoring system"""
        metrics_schema = {
            "session_id": "guid",
            "ts_iso": "2025-01-01T12:00:00Z",
            "event": "render_done|error|queue_enqueue|gpu_sample",
            "engine": "xtts|openvoice|cosyvoice2|coqui",
            "latency_ms": 0,
            "vram_used_mb": 0,
            "error": None,
        }

        metrics_path = self.tele_path / "metrics_schema.json"
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics_schema, f, indent=2)

        print(f"Created Telemetry Schema: {metrics_path}")

    def create_architecture_task(self):
        """Create architecture task documentation"""
        task_content = """# Unify architecture & ops

1) Move legacy configs:
   - `python tools/migrate_configs.py`
2) Router:
   - Import `UltraClone.EngineService.routing.engine_router.EngineRouter` in TTS path.
3) Dashboard:
   - `tools\\run_dashboard.ps1`
4) Launcher:
   - `python tools\\voicestudio_launcher.py --mode dev --services engine,orchestrator`
5) DB:
   - `alembic revision -m "init"` then `alembic upgrade head`
6) CI:
   - Push to trigger GitHub Actions."""

        task_dir = self.repo_path / ".cursor" / "tasks"
        task_dir.mkdir(parents=True, exist_ok=True)

        task_path = task_dir / "unify-architecture.md"
        with open(task_path, "w", encoding="utf-8") as f:
            f.write(task_content)

        print(f"Created Architecture Task: {task_path}")

    def run_complete_unification(self):
        """Run complete architecture unification"""
        print("VoiceStudio Ultimate - Architecture Unification System")
        print("=" * 60)

        self.create_directories()
        self.create_unified_launcher()
        self.create_config_files()
        self.create_config_migrator()
        self.create_engine_router()
        self.create_dashboard_runner()
        self.create_plugin_registry()
        self.create_common_errors()
        self.create_database_system()
        self.create_pyproject_toml()
        self.create_tests_and_ci()
        self.create_telemetry_system()
        self.create_architecture_task()

        print("\n" + "=" * 60)
        print("ARCHITECTURE UNIFICATION COMPLETE")
        print("=" * 60)
        print("Unified Launcher: Created")
        print("Config Consolidation: Created")
        print("Engine Router: Created")
        print("Dashboard Runner: Created")
        print("Plugin Registry: Created")
        print("Database System: Created")
        print("Test Suite: Created")
        print("CI Pipeline: Created")
        print("Telemetry System: Created")
        print("\nNext steps:")
        print("1. Run: python tools/migrate_configs.py")
        print("2. Test: python tools/voicestudio_launcher.py --health-check")
        print("3. Start: python tools/voicestudio_launcher.py --mode dev")


def main():
    unifier = VoiceStudioArchitectureUnifier()
    unifier.run_complete_unification()


if __name__ == "__main__":
    main()
