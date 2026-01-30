# Preflight Reference

**Scope**: Operator-readable readiness; all local-first roots and tools checked. Non-blocking and fast (readiness only).

**Endpoint**: `GET /api/health/preflight`  
**Default URL**: `http://localhost:8001/api/health/preflight`  
**Port**: Backend default port **8001** (see `scripts/backend/start_backend.ps1`).

**Validates**:
- `projects_root`, `cache_root`, `model_root` (storage roots)
- `audio_registry_dir`, `jobs_root` (artifact and job persistence)
- `engine_config` (model_paths.base vs model_root)
- `xtts_v2`, `sovits_svc` (engine deps/assets; no auto-download). For `sovits_svc`, also reports `inference_command_configured` (true when `infer_command` or `SOVITS_SVC_INFER_COMMAND` is set).
- `ffmpeg` (VOICESTUDIO_FFMPEG_PATH or PATH)
- `plugins_dir` (optional; plugin host readiness)

**Proof**: `curl http://localhost:8001/api/health/preflight` after `.\scripts\backend\start_backend.ps1 -CoquiTosAgreed`.

**Plugin host**: Backend calls `load_all_plugins(app)` at startup (see `backend/api/main.py`). C# `PluginLoader` owns UI-hosted plugins; backend loader owns API-hosted plugins under `plugins/`. Preflight reports `plugins_dir` ok/path; it does not run heavy plugin init.
