# VoiceStudio — Golden Path (Dev → Staging → Prod)

## Dev
1. Install CUDA/CuDNN + drivers; ensure `nvidia-smi` OK.
2. `pip install -e .[voice-cloning,dev,db]`
3. Consolidate configs: `python tools/migrate_configs.py`
4. Launch services: `python tools/voicestudio_launcher.py --mode dev --services engine,orchestrator`
5. Start dashboard: `powershell tools\run_dashboard.ps1`
6. Run plugin watcher (optional): `python tools\plugin_watcher.py`
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
4. Backups: `tools\backup_db.ps1 backup`
5. Compliance: watermark/policy toggles per profile.

## Engine Routing & Fallback
- Router picks engine by language/latency requirements; fallback: XTTS → OpenVoice → CosyVoice → Coqui.
- Failover is automatic via `engine_dispatch.py`.

## Plugins
- Add plugin folders under `plugins\{name}`.
- Edit `plugins\registry\registry.json`; dev watcher touches `.stamp` for UI hot-reload.

## Troubleshooting
- Dashboard shows service health and queues.
- Check `%ProgramData%\VoiceStudio\logs\` for JSON logs.
- Rebuild installer if antivirus quarantines the bundle; ensure WiX tools on PATH.
