# Operations Runbook

**Phase 7 Sprint 4**  
**VoiceStudio Quantum+**

## Startup Sequence

1. **Backend**: `uvicorn backend.api.main:app --host 0.0.0.0 --port 8000`
2. **App**: Launches WinUI 3; connects to `http://localhost:8000`
3. **Engines**: Loaded on first use; manifests in `engines/*.json`

## Health Checks

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health/` | Full health (database, GPU, engines, plugins) |
| `GET /api/health/simple` | Fast liveness |
| `GET /api/health/ready` | Readiness (critical checks only) |
| `GET /metrics` | Prometheus metrics |

## Troubleshooting

### Backend won't start

- Check port 8000 is free: `netstat -an | findstr 8000`
- Verify Python 3.11: `python --version`
- Check `VOICESTUDIO_MODELS_PATH` exists and is writable

### Synthesis fails

- Check engine manifest: `engines/*/engine.manifest.json`
- Verify model path in manifest
- Check `.buildlogs/` for trace files

### Plugin install fails

- Verify catalog URL: `VOICESTUDIO_PLUGIN_CATALOG_URL`
- Check `~/.voicestudio/plugins/` is writable
- Review plugin signature verification

## Backup and Restore

- **User data**: `~/.voicestudio/` (profiles, projects, API keys, plugins)
- **Models**: `VOICESTUDIO_MODELS_PATH` (default: `~/.voicestudio/models`)
- Use Backup/Restore panel or `POST /api/backup` for full backup

## Engine Management

- Engine manifests: `engines/*/engine.manifest.json`
- Preflight: `GET /api/engines/preflight`
- Health: `GET /api/health/` includes engine status

## Log Locations

| Log | Path |
|-----|------|
| Structured | `~/.voicestudio/logs/voicestudio.log` |
| Build logs | `.buildlogs/voicestudio.json` |
| Traces | `.buildlogs/traces/` |

## Security

- API keys: `~/.voicestudio/data/api_keys.json` (encrypted)
- Secrets: `backend/security/secrets_vault.py`
- Incident response: `docs/security/INCIDENT_RESPONSE_PLAYBOOK.md`
