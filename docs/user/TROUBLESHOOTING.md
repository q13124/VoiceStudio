# VoiceStudio Troubleshooting

Common issues and solutions.

---

## Backend Won't Start

**Symptoms**: Status bar shows "Disconnected" or "Connecting..."; main window loads but no backend.

**Solutions**:
1. Check that port 8000 is not in use by another application.
2. Ensure Python 3.9+ is installed and in PATH (if using external Python).
3. Check logs: `%LOCALAPPDATA%\VoiceStudio\logs\` or `.buildlogs/`.
4. Restart VoiceStudio. If bundled Python is corrupted, reinstall.

---

## Engine Initialization Fails

**Symptoms**: "Engine unavailable" or synthesis/transcription fails with engine error.

**Solutions**:
1. **Model not downloaded**: First use of an engine may require model download. Wait for completion or check network.
2. **GPU/CUDA**: If GPU is required but unavailable, some engines fall back to CPU (slower). Check Diagnostics → GPU status.
3. **Memory**: Large models need sufficient RAM/VRAM. Close other applications.
4. **Path**: Ensure `VOICESTUDIO_MODELS_PATH` points to a writable directory (if set).

---

## GPU Detection Issues

**Symptoms**: Synthesis is slow; GPU not detected.

**Solutions**:
1. Update graphics drivers to the latest version.
2. For NVIDIA: Ensure CUDA-compatible driver (see [CUDA_COMPATIBILITY_AUDIT.md](../reports/CUDA_COMPATIBILITY_AUDIT.md)).
3. Check Diagnostics panel → GPU status.
4. Some engines work CPU-only; performance may be reduced.

---

## Log Locations

| Location | Purpose |
|----------|---------|
| `%LOCALAPPDATA%\VoiceStudio\logs\` | Application logs |
| `.buildlogs\` | Build and verification logs |
| `.audit\` | Audit trail (if enabled) |

---

## Diagnostic Panel Usage

1. Open **Diagnostics** panel (bottom region).
2. Click **Check Health** to run system diagnostics.
3. Review checks: environment, resources, dependencies, paths, services, network, model drift.
4. Use **Logs** tab to filter and search logs.
5. Use **Traces** tab for request tracing.

---

## Plugin Issues

**Plugin fails to load**:
- Check plugin manifest and permissions.
- View Plugin Gallery → Installed → Details for errors.
- Ensure plugin is compatible with your VoiceStudio version.

**Plugin crashes**:
- Plugins run in a sandbox; crashes are isolated.
- Check Diagnostics → Logs for plugin-related errors.
- Disable or uninstall the plugin if unstable.

---

## Reinstall / Reset

If all else fails:
1. Uninstall via Windows Settings → Apps.
2. Optionally delete `%LOCALAPPDATA%\VoiceStudio\` to reset user data (backs up first).
3. Reinstall from the installer.

---

## Getting Help

- Check [USER_MANUAL.md](USER_MANUAL.md) for detailed feature documentation.
- Review [RELEASE_NOTES_v1.0.2.md](../release/RELEASE_NOTES_v1.0.2.md) for known issues.
- Open an issue on the project repository with logs and steps to reproduce.
