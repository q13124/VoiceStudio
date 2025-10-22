# Unify architecture & ops

1) Move legacy configs:
   - `python tools/migrate_configs.py`
2) Router:
   - Import `UltraClone.EngineService.routing.engine_router.EngineRouter` in TTS path.
3) Dashboard:
   - `tools\run_dashboard.ps1`
4) Launcher:
   - `python tools\voicestudio_launcher.py --mode dev --services engine,orchestrator`
5) DB:
   - `alembic revision -m "init"` then `alembic upgrade head`
6) CI:
   - Push to trigger GitHub Actions.