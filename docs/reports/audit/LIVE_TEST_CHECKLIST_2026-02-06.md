# VoiceStudio v1.0.1 Live Test Checklist

> **Test Date**: 2026-02-06
> **Tester**: _______________
> **Environment**: Windows _____ | RAM: _____ GB | GPU: _____
> **Version**: v1.0.1

---

## Phase 1: Pre-Test Preparation

### 1.1 Environment Verification

| Check | Status | Notes |
|-------|--------|-------|
| Windows 10 22H2 or Windows 11 23H2 | [ ] PASS / [ ] FAIL | |
| 16GB+ RAM available | [ ] PASS / [ ] FAIL | |
| NVIDIA GPU with 8GB+ VRAM (or CPU fallback) | [ ] PASS / [ ] FAIL | |
| Admin rights available | [ ] PASS / [ ] FAIL | |

### 1.2 Required Files

| File | Exists | Size |
|------|--------|------|
| `installer/Output/VoiceStudio-Setup-v1.0.0.exe` | [ ] YES / [ ] NO | ~61 MB |
| `installer/Output/VoiceStudio-Setup-v1.0.1.exe` | [ ] YES / [ ] NO | ~64 MB |

### 1.3 Model Preparation

| Model Type | Path | Status |
|------------|------|--------|
| RVC HuBERT | `%PROGRAMDATA%\VoiceStudio\models\rvc\hubert\` | [ ] READY / [ ] MISSING |
| RVC Model (.pth) | `%PROGRAMDATA%\VoiceStudio\models\rvc\*.pth` | [ ] READY / [ ] MISSING |
| So-VITS Checkpoint | `models/checkpoints/MyVoiceProj/model.pth` | [ ] READY / [ ] MISSING |
| So-VITS Config | `models/checkpoints/MyVoiceProj/config.json` | [ ] READY / [ ] MISSING |

### 1.4 Test Assets

| Asset | Prepared | Count/Details |
|-------|----------|---------------|
| Sample text sentences | [ ] YES / [ ] NO | _____ sentences |
| WAV files for conversion | [ ] YES / [ ] NO | _____ files |
| Reference voice samples | [ ] YES / [ ] NO | _____ samples |

**Phase 1 Result**: [ ] PASS / [ ] FAIL / [ ] PARTIAL

---

## Phase 2: Installation and Upgrade Testing

**Owner**: Release Engineer (Role 6)

### 2.1 Fresh Installation

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 2.1.1 | Run `VoiceStudio-Setup-v1.0.1.exe` | Installer launches | [ ] PASS / [ ] FAIL | |
| 2.1.2 | Verify .NET 8 check | Prerequisite detected or prompted | [ ] PASS / [ ] FAIL | |
| 2.1.3 | Verify WinAppSDK check | Prerequisite detected or prompted | [ ] PASS / [ ] FAIL | |
| 2.1.4 | Complete installation | No errors, completes successfully | [ ] PASS / [ ] FAIL | |
| 2.1.5 | Check Start Menu | "VoiceStudio" appears | [ ] PASS / [ ] FAIL | |
| 2.1.6 | Check Programs and Features | Listed correctly | [ ] PASS / [ ] FAIL | |
| 2.1.7 | Verify install path | `C:\Program Files\VoiceStudio\` exists | [ ] PASS / [ ] FAIL | |

**Log**: `C:\logs\voicestudio_install_1.0.1.log`

### 2.2 Silent Installation

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 2.2.1 | Uninstall previous version | Clean state | [ ] PASS / [ ] FAIL | |
| 2.2.2 | Run silent install command | No UI appears | [ ] PASS / [ ] FAIL | |
| 2.2.3 | Verify log file created | Log exists and shows success | [ ] PASS / [ ] FAIL | |
| 2.2.4 | Verify installation complete | App installed correctly | [ ] PASS / [ ] FAIL | |

**Command Used**:
```powershell
Start-Process -FilePath ".\VoiceStudio-Setup-v1.0.1.exe" `
  -ArgumentList "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-", `
  "/DIR=`"C:\Program Files\VoiceStudio`"", `
  "/LOG=`"C:\logs\voicestudio_silent_install.log`"" -Wait
```

### 2.3 Upgrade Path

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 2.3.1 | Install v1.0.0 | Clean install succeeds | [ ] PASS / [ ] FAIL | |
| 2.3.2 | Create test project | Project saved | [ ] PASS / [ ] FAIL | |
| 2.3.3 | Run v1.0.1 installer | Upgrade detected | [ ] PASS / [ ] FAIL | |
| 2.3.4 | Verify settings preserved | `%LOCALAPPDATA%\VoiceStudio\` intact | [ ] PASS / [ ] FAIL | |
| 2.3.5 | Verify project accessible | Previous project opens | [ ] PASS / [ ] FAIL | |

### 2.4 Rollback

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 2.4.1 | Uninstall v1.0.1 | Uninstall completes | [ ] PASS / [ ] FAIL | |
| 2.4.2 | Install v1.0.0 | Rollback install succeeds | [ ] PASS / [ ] FAIL | |
| 2.4.3 | Launch application | App starts without crash | [ ] PASS / [ ] FAIL | |
| 2.4.4 | Verify project accessible | Previous project still opens | [ ] PASS / [ ] FAIL | |

**Phase 2 Result**: [ ] PASS / [ ] FAIL / [ ] PARTIAL
**Issues Found**: _______________

---

## Phase 3: Runtime Launch and Navigation

**Owner**: UI Engineer (Role 3)

### 3.1 Initial Launch

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 3.1.1 | Launch from Start Menu | Main window appears | [ ] PASS / [ ] FAIL | |
| 3.1.2 | Check crash logs | No new crash logs | [ ] PASS / [ ] FAIL | |
| 3.1.3 | Verify boot marker | `boot_latest.json` exists | [ ] PASS / [ ] FAIL | |
| 3.1.4 | Measure startup time | < 10 seconds | [ ] PASS / [ ] FAIL | _____ seconds |

**Crash Log Path**: `%LOCALAPPDATA%\VoiceStudio\crashes\`

### 3.2 NavRail Navigation (8 Buttons)

| Button | Tooltip | Target Panel | Loads Correctly | Region Correct |
|--------|---------|--------------|-----------------|----------------|
| NavStudio | Studio | TimelineView | [ ] PASS / [ ] FAIL | Center |
| NavProfiles | Profiles | ProfilesView | [ ] PASS / [ ] FAIL | Left |
| NavLibrary | Library | LibraryView | [ ] PASS / [ ] FAIL | Left |
| NavEffects | Effects | EffectsMixerView | [ ] PASS / [ ] FAIL | Right |
| NavTrain | Train | TrainingView | [ ] PASS / [ ] FAIL | Left |
| NavAnalyze | Analyze | AnalyzerView | [ ] PASS / [ ] FAIL | Right |
| NavSettings | Settings | SettingsView | [ ] PASS / [ ] FAIL | Right |
| NavLogs | Logs | DiagnosticsView | [ ] PASS / [ ] FAIL | Bottom |

**UI Grid Verification**:
| Component | Expected | Status |
|-----------|----------|--------|
| Command Deck | 48px height | [ ] PASS / [ ] FAIL |
| Main Workspace | Flexible (*) | [ ] PASS / [ ] FAIL |
| Status Bar | 26px height | [ ] PASS / [ ] FAIL |
| NavRail | 64px width | [ ] PASS / [ ] FAIL |

### 3.3 Menu Bar (8 Menus)

| Menu | Items Tested | All Clickable | Status |
|------|--------------|---------------|--------|
| File | New, Open, Save, Recent, Exit | [ ] YES / [ ] NO | [ ] PASS / [ ] FAIL |
| Edit | Undo, Redo | [ ] YES / [ ] NO | [ ] PASS / [ ] FAIL |
| View | Toggle Mini Timeline, Global Search | [ ] YES / [ ] NO | [ ] PASS / [ ] FAIL |
| Modules | All 8 panels | [ ] YES / [ ] NO | [ ] PASS / [ ] FAIL |
| Playback | Play/Pause, Stop, Record | [ ] YES / [ ] NO | [ ] PASS / [ ] FAIL |
| Tools | Customize, Updates, Shortcuts | [ ] YES / [ ] NO | [ ] PASS / [ ] FAIL |
| AI | AI Mixing, Ensemble Synthesis | [ ] YES / [ ] NO | [ ] PASS / [ ] FAIL |
| Help | Documentation, About | [ ] YES / [ ] NO | [ ] PASS / [ ] FAIL |

**About Dialog Version**: v_______________

**Phase 3 Result**: [ ] PASS / [ ] FAIL / [ ] PARTIAL
**Issues Found**: _______________

---

## Phase 4: Voice Synthesis and Cloning

**Owner**: Engine Engineer (Role 5)

### 4.1 Voice Synthesis Test

| Step | Action | Expected | Status | Measurement |
|------|--------|----------|--------|-------------|
| 4.1.1 | Open Voice Synthesis panel | Panel loads | [ ] PASS / [ ] FAIL | |
| 4.1.2 | Select voice profile | Dropdown works | [ ] PASS / [ ] FAIL | Profile: _____ |
| 4.1.3 | Select engine (xtts_v2) | Engine selected | [ ] PASS / [ ] FAIL | |
| 4.1.4 | Enter test text | Text accepted | [ ] PASS / [ ] FAIL | _____ words |
| 4.1.5 | Click Synthesize | Audio generates | [ ] PASS / [ ] FAIL | Duration: _____ s |
| 4.1.6 | Playback audio | Audio plays | [ ] PASS / [ ] FAIL | |
| 4.1.7 | Check MOS score | >= 3.5/5.0 | [ ] PASS / [ ] FAIL | Score: _____/5.0 |
| 4.1.8 | Check Similarity | >= 70% | [ ] PASS / [ ] FAIL | _____% |
| 4.1.9 | Check Naturalness | Displays % | [ ] PASS / [ ] FAIL | _____% |
| 4.1.10 | Check Quality Color | Green/Orange/Red | [ ] PASS / [ ] FAIL | Color: _____ |

### 4.2 Voice Cloning Wizard (4 Steps)

| Step | Action | Expected | Status | Notes |
|------|--------|----------|--------|-------|
| **Step 1: Upload** |
| 4.2.1 | Browse audio files | File picker opens | [ ] PASS / [ ] FAIL | |
| 4.2.2 | Select reference audio | Files added | [ ] PASS / [ ] FAIL | _____ files |
| 4.2.3 | Click Validate | Validation passes | [ ] PASS / [ ] FAIL | |
| **Step 2: Configure** |
| 4.2.4 | Enter profile name | Name accepted | [ ] PASS / [ ] FAIL | Name: _____ |
| 4.2.5 | Select engine | Engine dropdown works | [ ] PASS / [ ] FAIL | Engine: _____ |
| 4.2.6 | Select quality mode | Mode selected | [ ] PASS / [ ] FAIL | Mode: _____ |
| **Step 3: Process** |
| 4.2.7 | Start processing | Progress bar appears | [ ] PASS / [ ] FAIL | |
| 4.2.8 | Wait for completion | Status shows complete | [ ] PASS / [ ] FAIL | Duration: _____ |
| **Step 4: Review** |
| 4.2.9 | View quality metrics | Metrics displayed | [ ] PASS / [ ] FAIL | |
| 4.2.10 | Play test audio | Audio plays | [ ] PASS / [ ] FAIL | |
| 4.2.11 | Click Finalize | Profile created | [ ] PASS / [ ] FAIL | |
| 4.2.12 | Restart app | App restarts | [ ] PASS / [ ] FAIL | |
| 4.2.13 | Verify profile persists | Profile still exists | [ ] PASS / [ ] FAIL | VS-0021 |

**Phase 4 Result**: [ ] PASS / [ ] FAIL / [ ] PARTIAL
**Issues Found**: _______________

---

## Phase 5: RVC and So-VITS-SVC Voice Conversion

**Owner**: Engine Engineer (Role 5) + Core Platform (Role 4)

### 5.1 So-VITS-SVC Configuration

| Check | Status | Notes |
|-------|--------|-------|
| `model.pth` exists | [ ] PASS / [ ] FAIL | Path: _____ |
| `config.json` exists | [ ] PASS / [ ] FAIL | Path: _____ |
| `SOVITS_SVC_INFER_COMMAND` set (if needed) | [ ] PASS / [ ] N/A | |

### 5.2 So-VITS-SVC Conversion

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 5.2.1 | Run proof script | Script executes | [ ] PASS / [ ] FAIL | |
| 5.2.2 | Check conversion output | Audio file created | [ ] PASS / [ ] FAIL | |
| 5.2.3 | Listen to output | Audio intelligible | [ ] PASS / [ ] FAIL | |
| 5.2.4 | HTTP 424 guard test | 424 returned when model missing | [ ] PASS / [ ] FAIL | |

**Proof Script Command**:
```powershell
python scripts/sovits_svc_conversion_proof.py `
  --checkpoint-path "models/checkpoints/MyVoiceProj/model.pth" `
  --config-path "models/checkpoints/MyVoiceProj/config.json"
```

### 5.3 RVC Conversion

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 5.3.1 | Verify RVC model exists | Model present | [ ] PASS / [ ] FAIL | |
| 5.3.2 | Navigate to RVC panel | Panel loads | [ ] PASS / [ ] FAIL | |
| 5.3.3 | Select source audio | Audio selected | [ ] PASS / [ ] FAIL | |
| 5.3.4 | Select target model | Model selected | [ ] PASS / [ ] FAIL | |
| 5.3.5 | Execute conversion | Conversion completes | [ ] PASS / [ ] FAIL | Duration: _____ |
| 5.3.6 | Listen to output | Audio quality acceptable | [ ] PASS / [ ] FAIL | |
| 5.3.7 | Check VRAM usage | Within limits (< 8GB) | [ ] PASS / [ ] FAIL | Used: _____ GB |

**Phase 5 Result**: [ ] PASS / [ ] FAIL / [ ] PARTIAL
**Issues Found**: _______________

---

## Phase 6: Performance Profiling

**Owner**: Core Platform (Role 4)

### 6.1 UI Virtualization

| Step | Action | Expected | Status | Measurement |
|------|--------|----------|--------|-------------|
| 6.1.1 | Create project with 500+ clips | Project created | [ ] PASS / [ ] FAIL | _____ clips |
| 6.1.2 | Navigate to Library | Library loads | [ ] PASS / [ ] FAIL | |
| 6.1.3 | Scroll rapidly through list | Smooth scrolling | [ ] PASS / [ ] FAIL | |
| 6.1.4 | Monitor CPU usage | < 50% during scroll | [ ] PASS / [ ] FAIL | _____% |
| 6.1.5 | Monitor memory | Stable (no growth) | [ ] PASS / [ ] FAIL | _____ MB |
| 6.1.6 | Incremental loading | 50-item pages | [ ] PASS / [ ] FAIL | |

### 6.2 Deferred Initialization

| Step | Action | Expected | Status | Measurement |
|------|--------|----------|--------|-------------|
| 6.2.1 | Cold start app | Window appears first | [ ] PASS / [ ] FAIL | |
| 6.2.2 | Measure startup time | < 5 seconds to window | [ ] PASS / [ ] FAIL | _____ seconds |
| 6.2.3 | Background services init | Init after window visible | [ ] PASS / [ ] FAIL | |

### 6.3 Response Cache

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 6.3.1 | Make GET to `/api/engines` | Response returned | [ ] PASS / [ ] FAIL | |
| 6.3.2 | Make same GET again | `X-Cache: HIT` header | [ ] PASS / [ ] FAIL | |
| 6.3.3 | Check cache stats | Stats available | [ ] PASS / [ ] FAIL | Hit rate: _____% |

### 6.4 SLO Dashboard

| SLO | Target | Measured | Status |
|-----|--------|----------|--------|
| Synthesis Latency P95 | < 2.0s | _____ s | [ ] PASS / [ ] FAIL |
| API Availability | >= 99.5% | _____% | [ ] PASS / [ ] FAIL |
| Transcription Accuracy | >= 95% | _____% | [ ] PASS / [ ] FAIL |
| Engine Error Rate | < 1% | _____% | [ ] PASS / [ ] FAIL |
| Request Throughput | >= 10 req/s | _____ req/s | [ ] PASS / [ ] FAIL |

**SLO Export Test**: [ ] PASS / [ ] FAIL (Endpoint: `/api/v1/diagnostics/slo/export`)

**Phase 6 Result**: [ ] PASS / [ ] FAIL / [ ] PARTIAL
**Issues Found**: _______________

---

## Phase 7: Error Recovery and Data Safety

**Owner**: Core Platform (Role 4) + Release Engineer (Role 6)

### 7.1 Crash Recovery

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 7.1.1 | Create project with unsaved changes | Changes pending | [ ] PASS / [ ] FAIL | |
| 7.1.2 | Force kill: `taskkill /F /IM VoiceStudio.App.exe` | App terminated | [ ] PASS / [ ] FAIL | |
| 7.1.3 | Check crash marker | `.crash_marker` exists | [ ] PASS / [ ] FAIL | |
| 7.1.4 | Restart application | Recovery prompt appears | [ ] PASS / [ ] FAIL | |
| 7.1.5 | Accept recovery | Session state restored | [ ] PASS / [ ] FAIL | |
| 7.1.6 | Verify unsaved changes | Changes recovered | [ ] PASS / [ ] FAIL | |

**Recovery Paths**:
- Session: `%LOCALAPPDATA%\VoiceStudio\Recovery\session.json`
- Marker: `%LOCALAPPDATA%\VoiceStudio\Recovery\.crash_marker`

### 7.2 Circuit Breaker

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 7.2.1 | Trigger engine failure | First failure recorded | [ ] PASS / [ ] FAIL | |
| 7.2.2 | Make 3+ failing requests | Circuit opens | [ ] PASS / [ ] FAIL | |
| 7.2.3 | Verify fast fail | Immediate error (no timeout) | [ ] PASS / [ ] FAIL | |
| 7.2.4 | Wait 60 seconds | Recovery timeout | [ ] PASS / [ ] FAIL | |
| 7.2.5 | Make request | Circuit half-open | [ ] PASS / [ ] FAIL | |
| 7.2.6 | Successful request | Circuit closes | [ ] PASS / [ ] FAIL | |
| 7.2.7 | Verify fallback chain | Alternative engine used | [ ] PASS / [ ] FAIL | |

### 7.3 Data Backup

| Step | Action | Expected | Status | Evidence |
|------|--------|----------|--------|----------|
| 7.3.1 | Trigger manual backup | Backup created | [ ] PASS / [ ] FAIL | |
| 7.3.2 | Verify backup file | ZIP exists | [ ] PASS / [ ] FAIL | Path: _____ |
| 7.3.3 | Verify manifest.json | Manifest in ZIP | [ ] PASS / [ ] FAIL | |
| 7.3.4 | Restore from backup | Restore completes | [ ] PASS / [ ] FAIL | |
| 7.3.5 | Verify data integrity | Data restored correctly | [ ] PASS / [ ] FAIL | |

**Backup Path**: `%LOCALAPPDATA%\VoiceStudio\Backups\backup_*.zip`

**Phase 7 Result**: [ ] PASS / [ ] FAIL / [ ] PARTIAL
**Issues Found**: _______________

---

## Summary

### Phase Results

| Phase | Description | Result | Issues |
|-------|-------------|--------|--------|
| 1 | Pre-Test Preparation | [ ] PASS / [ ] FAIL / [ ] PARTIAL | |
| 2 | Installation/Upgrade | [ ] PASS / [ ] FAIL / [ ] PARTIAL | |
| 3 | Navigation/Menu | [ ] PASS / [ ] FAIL / [ ] PARTIAL | |
| 4 | Voice Synthesis | [ ] PASS / [ ] FAIL / [ ] PARTIAL | |
| 5 | Voice Conversion | [ ] PASS / [ ] FAIL / [ ] PARTIAL | |
| 6 | Performance | [ ] PASS / [ ] FAIL / [ ] PARTIAL | |
| 7 | Error Recovery | [ ] PASS / [ ] FAIL / [ ] PARTIAL | |

### Overall Verdict

**[ ] FULL PASS** - All phases passed, ready for production
**[ ] PASS WITH CONDITIONS** - Minor issues, acceptable for release
**[ ] FAIL** - Blocking issues require fixes before release

### Issues Log

| ID | Phase | Severity | Description | Status |
|----|-------|----------|-------------|--------|
| | | | | |
| | | | | |
| | | | | |

### Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Tester | | | |
| Release Engineer | | | |
| Overseer | | | |

---

## Code Analysis Evidence (Pre-Test)

All phases have been code-analyzed to verify structural implementation. Runtime testing by human testers required.

### Evidence Documents

| Phase | Evidence Document | Analysis Status |
|-------|-------------------|-----------------|
| 1 | [PHASE1_TEST_ENVIRONMENT_2026-02-06.md](PHASE1_TEST_ENVIRONMENT_2026-02-06.md) | ✅ COMPLETE |
| 2 | [PHASE2_INSTALLATION_EVIDENCE_2026-02-06.md](PHASE2_INSTALLATION_EVIDENCE_2026-02-06.md) | ✅ COMPLETE |
| 3 | [PHASE3_NAVIGATION_EVIDENCE_2026-02-06.md](PHASE3_NAVIGATION_EVIDENCE_2026-02-06.md) | ✅ COMPLETE |
| 4 | [PHASE4_SYNTHESIS_EVIDENCE_2026-02-06.md](PHASE4_SYNTHESIS_EVIDENCE_2026-02-06.md) | ✅ COMPLETE |
| 5 | [PHASE5_CONVERSION_EVIDENCE_2026-02-06.md](PHASE5_CONVERSION_EVIDENCE_2026-02-06.md) | ✅ COMPLETE |
| 6 | [PHASE6_PERFORMANCE_EVIDENCE_2026-02-06.md](PHASE6_PERFORMANCE_EVIDENCE_2026-02-06.md) | ✅ COMPLETE |
| 7 | [PHASE7_RECOVERY_EVIDENCE_2026-02-06.md](PHASE7_RECOVERY_EVIDENCE_2026-02-06.md) | ✅ COMPLETE |

### Test Assets Created

| Asset | Location |
|-------|----------|
| Sample Sentences | `docs/reports/audit/test_assets/sample_sentences.txt` |
| Model Placeholder | `models/checkpoints/MyVoiceProj/config.json` |

### Code Analysis Summary

- **Phase 1**: Environment verified, installer files confirmed, model directory created
- **Phase 2**: Inno Setup scripts analyzed, prerequisite detection logic verified
- **Phase 3**: NavRail 8 buttons + 8 menu bar items confirmed in XAML/code-behind
- **Phase 4**: Synthesis UI, 4-step cloning wizard, quality metrics verified
- **Phase 5**: RVC/So-VITS engines, HTTP 424 guard, proof script verified
- **Phase 6**: Virtualization, deferred init, response cache, SLO dashboard verified
- **Phase 7**: Crash recovery, circuit breaker, data backup services verified

---

*Generated: 2026-02-06*
*Template Version: 1.0*
*Code Analysis Completed: 2026-02-06*
