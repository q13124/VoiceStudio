# VoiceStudio VM Lifecycle Test Procedure

**Purpose**: Validate installer and application lifecycle on clean Windows 10/11 VMs before promoting release candidates to GA.

**Prerequisites**:
- Clean Windows 10 (22H2+) or Windows 11 VM
- 8 GB RAM minimum, 16 GB recommended
- 50 GB free disk
- Network access for optional model downloads

---

## 1. Fresh Install

1. Copy `VoiceStudio-Setup-v1.0.2.exe` (or current RC) to VM
2. Run installer with default options
3. **Verify**: Install completes without errors; shortcut created on Desktop/Start Menu
4. **Verify**: `%ProgramFiles%\VoiceStudio\` (or chosen path) contains:
   - `VoiceStudio.App.exe`
   - `Runtime\` (Python, FFmpeg if bundled)
   - Supporting DLLs and config

---

## 2. First Launch and Backend Health

1. Launch VoiceStudio from shortcut
2. **Verify**: Main window opens within 30 seconds
3. **Verify**: Backend process starts (check Task Manager for `python.exe` or `uvicorn`)
4. **Verify**: Status bar shows "Connected" or health indicator green
5. Optional: Open `http://localhost:8000/health` in browser — expect 200 JSON response

---

## 3. Basic Workflow

1. **Import audio**: File → Import Audio (or drag WAV/MP3)
2. **Verify**: File appears in Library
3. **Transcribe**: Select asset → Transcribe (or Transcribe panel)
4. **Verify**: Transcription completes or shows clear error (e.g., model not downloaded)
5. **Synthesize**: Open Voice Synthesis panel → Select profile → Synthesize
6. **Verify**: Synthesis completes or shows clear error
7. **Export**: Export to WAV/MP3
8. **Verify**: Output file created

---

## 4. Upgrade from Previous Version

1. Install previous version (e.g., v1.0.1 or v1.0.2-rc1)
2. Create a test project, add assets, save
3. Run new installer over existing install
4. **Verify**: Upgrade completes; no "already installed" block
5. Launch application
6. **Verify**: Previous project opens; settings preserved
7. **Verify**: No data loss in `%LOCALAPPDATA%\VoiceStudio\`

---

## 5. Uninstall and Clean Removal

1. Windows Settings → Apps → VoiceStudio → Uninstall
2. **Verify**: Uninstall completes without errors
3. **Verify**: `%ProgramFiles%\VoiceStudio\` removed (or chosen install path)
4. **Verify**: `%LOCALAPPDATA%\VoiceStudio\` retained (user data preserved)
5. Optional: Run installer again — fresh install should succeed

---

## Pass Criteria

| Step | Criterion |
|------|-----------|
| 1 | Install completes, files present |
| 2 | Main window opens, backend health OK |
| 3 | Import, transcribe, synthesize, export (or clear error) |
| 4 | Upgrade succeeds, data preserved |
| 5 | Uninstall clean, reinstall possible |

---

## Evidence Capture

For release sign-off, capture:
- Screenshot of main window after first launch
- Screenshot of `http://localhost:8000/health` response (or equivalent)
- Log excerpt from `%LOCALAPPDATA%\VoiceStudio\logs\` if any errors
- Installer size and checksum (optional)

---

## References

- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)
- [INSTALLER_PREPARATION.md](INSTALLER_PREPARATION.md)
- [QUALITY_LEDGER.md](../../Recovery%20Plan/QUALITY_LEDGER.md)
