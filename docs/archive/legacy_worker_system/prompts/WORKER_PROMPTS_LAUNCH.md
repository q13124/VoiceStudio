# Worker Agent Prompts - Launch Instructions
## Overseer-Generated Prompts for 6 Worker Instances

**Date:** 2025-01-28  
**Overseer:** VoiceStudio Quantum+ Architect  
**Project:** E:\VoiceStudio  
**Phase:** Foundation & Migration (Phase 0)

---

## 🎯 STRUCTURED TASK LISTS - READ THIS FIRST

**Before starting work, read your worker's structured task list:**

- **Worker 1:** `docs/governance/overseer/WORKER_1_STRUCTURED_TASK_LIST_2025-01-28.md`
- **Worker 2:** `docs/governance/overseer/WORKER_2_STRUCTURED_TASK_LIST_2025-01-28.md`
- **Worker 3:** `docs/governance/overseer/WORKER_3_STRUCTURED_TASK_LIST_2025-01-28.md`

**Master Index:** `docs/governance/overseer/STRUCTURED_TASK_LISTS_INDEX_2025-01-28.md`

**These lists provide clear, sequential tasks so you know what to do next without asking after every task completion.**

---

---

## 🚦 CRITICAL GUARDRAILS (All Workers Must Follow)

**These rules are NON-NEGOTIABLE. Enforce them at every step:**

```
Do NOT simplify the UI layout or collapse panels.
Keep the 3-column + nav + bottom deck layout and PanelHost controls.
Do NOT merge Views and ViewModels. Each panel = .xaml + .xaml.cs + ViewModel.cs.
Do NOT remove placeholder areas (waveform, spectrogram, analyzers, macros, logs).
Use DesignTokens.xaml for all colors/typography; no hardcoded values.
Treat this as a professional DAW-grade app, not a demo or toy.
```

**Violation Detection:**
- Merged View/ViewModel files → REVERT
- PanelHost replaced with Grid → REVERT
- Reduced panel count → REVERT
- Hardcoded colors → REVERT
- Simplified layout → REVERT

---

## 👷 Worker 1: Engine & Backend Foundation

### Your Mission

Update the XTTS Engine to use the correct protocol system and ensure it's production-ready.

### Tasks

1. **Review Current XTTS Engine**
   - File: `E:\VoiceStudio\app\core\engines\xtts_engine.py`
   - Verify it uses `EngineProtocol` from `app\core\engines\protocols.py`
   - Check: Does it properly inherit from `EngineProtocol`?

2. **Update if Needed**
   - If it uses `base.py`, update to use `protocols.py`
   - Ensure `super().__init__(device=device, gpu=gpu)` is called
   - Verify all abstract methods are implemented

3. **Review Source Reference** (Read-Only)
   - Reference: `C:\VoiceStudio\app\core\engines\xtts_engine.py`
   - Compare logic and ensure all useful functionality is included
   - Note any missing features

4. **Test Engine**
   - Run: `python app\cli\xtts_test.py`
   - Verify engine initializes correctly
   - Test synthesis if possible

5. **Update Migration Log**
   - File: `docs\governance\Migration-Log.md`
   - Mark XTTS Engine as complete
   - Note any adaptations made

### Deliverables

- ✅ XTTS engine uses `protocols.py` correctly
- ✅ Engine inherits from `EngineProtocol` properly
- ✅ All abstract methods implemented
- ✅ CLI test passes
- ✅ Migration log updated

### Reference Documents

- `docs\governance\PORT_TASKS_BATCH_1.md` - Task details
- `app\core\engines\protocols.py` - Protocol definition
- `docs\design\VoiceStudio-Architecture.md` - Architecture guide

---

## 👷 Worker 2: Audio Utilities Port

### Your Mission

Port audio utility functions from C:\VoiceStudio to E:\VoiceStudio with proper testing.

### Tasks

1. **Inspect Source** (Read-Only)
   - File: `C:\VoiceStudio\app\core\audio\audio_utils.py`
   - Identify useful functions:
     - `normalize_lufs()` - LUFS normalization
     - `detect_silence()` - Silence detection
     - `resample_audio()` - Audio resampling
     - `convert_format()` - Format conversion
     - Any other audio processing utilities

2. **Port Functions**
   - Target: `E:\VoiceStudio\app\core\audio\audio_utils.py`
   - Update imports to match new structure
   - Remove old UI references
   - Update paths to use `E:\VoiceStudio_data\...` for temp files
   - Ensure compatibility with:
     - Librosa 0.11.0
     - SoundFile 0.12.1
     - NumPy 1.26.4
     - pyloudnorm 0.1.1

3. **Create Tests**
   - File: `E:\VoiceStudio\app\core\audio\test_audio_utils.py`
   - Include 2-3 basic tests:
     - Test LUFS normalization
     - Test silence detection
     - Test format conversion (if applicable)
   - Use pytest or unittest framework

4. **Update Migration Log**
   - File: `docs\governance\Migration-Log.md`
   - Add entry for Audio Utilities
   - Mark as complete
   - Note functions ported

### Deliverables

- ✅ `audio_utils.py` with ported functions
- ✅ `test_audio_utils.py` with 2-3 tests
- ✅ All imports match new structure
- ✅ No legacy UI references
- ✅ Tests pass
- ✅ Migration log updated

### Reference Documents

- `docs\governance\PORT_TASKS_BATCH_1.md` - Task details
- `docs\design\TECHNICAL_STACK_SPECIFICATION.md` - Dependency versions

---

## 👷 Worker 3: Panel Discovery & Registry

### Your Mission

Ensure all panels are discovered and properly registered in the panel system.

### Tasks

1. **Run Panel Discovery**
   - Script: `.\tools\Find-AllPanels.ps1`
   - Verify it finds all panels in E:\VoiceStudio
   - Check output: `app\core\PanelRegistry.Auto.cs`

2. **Verify Panel Count**
   - Current: 38 panels registered
   - Expected: Should find all XAML files
   - If panels are missing, investigate why

3. **Check Panel Registry**
   - File: `app\core\PanelRegistry.Auto.cs`
   - Verify all discovered panels are listed
   - Check for duplicates or missing entries

4. **Run Verification**
   - Script: `python app\cli\verify_panels.py`
   - Fix any discrepancies found
   - Ensure all panels can be loaded

5. **Update Documentation**
   - File: `docs\governance\MIGRATION_STATUS.md`
   - Update panel count if changed
   - Note any issues found

### Deliverables

- ✅ Panel discovery script run successfully
- ✅ All panels found and registered
- ✅ Panel registry updated
- ✅ Verification passes
- ✅ Documentation updated

### Reference Documents

- `tools\Find-AllPanels.ps1` - Discovery script
- `app\cli\verify_panels.py` - Verification tool
- `docs\governance\PANEL_DISCOVERY_QUICK_REF.md` - Quick reference

---

## 👷 Worker 4: Backend API Skeleton

### Your Mission

Create the FastAPI backend skeleton with core endpoints and structure.

### Tasks

1. **Review Current Backend**
   - Directory: `E:\VoiceStudio\backend\api\`
   - Check existing structure
   - Review: `main.py`, `models.py`, `routes\`

2. **Implement Core Endpoints**
   - `/api/health` - Health check endpoint
   - `/api/profiles` - Voice profile management (GET, POST)
   - `/api/projects` - Project management (GET, POST, PUT)
   - `/api/audio/synthesize` - Audio synthesis (POST)
   - `/api/audio/analyze` - Audio analysis (POST)

3. **Create Backend Client Interface** (C#)
   - File: `src\VoiceStudio.Core\Services\IBackendClient.cs`
   - Define interface methods matching endpoints
   - Include async methods for all operations

4. **Implement Backend Client** (C#)
   - File: `src\VoiceStudio.App\Services\BackendClient.cs`
   - Use HttpClient for HTTP requests
   - Implement IBackendClient interface
   - Add error handling and retry logic

5. **Wire UI to Backend**
   - Update `ProfilesViewModel.cs` to use IBackendClient
   - Update `DiagnosticsViewModel.cs` to call `/api/health`
   - Test connection (backend may not be running yet)

### Deliverables

- ✅ FastAPI skeleton with core endpoints
- ✅ IBackendClient interface defined
- ✅ BackendClient implementation
- ✅ UI ViewModels wired to backend client
- ✅ Error handling implemented

### Reference Documents

- `docs\design\PHASE_ROADMAP_COMPLETE.md` - Phase 5 details
- `backend\api\main.py` - Existing structure
- `docs\design\ARCHITECTURE_DATA_FLOW.md` - Data flow patterns

---

## 👷 Worker 5: Workspace Migration Preparation

### Your Mission

Prepare and verify the workspace migration system is ready to execute.

### Tasks

1. **Review Migration Script**
   - File: `tools\VS_MigrateToE.ps1`
   - Verify script logic is correct
   - Check for any syntax errors

2. **Test Prerequisites**
   - Run: `.\tools\Test-Migration.ps1`
   - Verify:
     - Source exists: `C:\VoiceStudio`
     - Destination ready: `E:\VoiceStudio`
     - Disk space sufficient
     - Python available
     - Robocopy available

3. **Dry-Run Migration**
   - Run: `.\tools\VS_MigrateToE.ps1 -ListOnly`
   - Review what would be copied
   - Check for any issues

4. **Prepare Migration Checklist**
   - Review: `docs\governance\POST_MIGRATION_CHECKS.md`
   - Ensure all verification steps are clear
   - Prepare rollback plan if needed

5. **Document Migration Readiness**
   - Update: `docs\governance\MIGRATION_READY.md`
   - Mark system as ready or note blockers
   - List any prerequisites needed

### Deliverables

- ✅ Migration script reviewed and verified
- ✅ Prerequisites checked
- ✅ Dry-run completed
- ✅ Migration checklist prepared
- ✅ System marked as ready (or blockers documented)

### Reference Documents

- `tools\VS_MigrateToE.ps1` - Migration script
- `docs\governance\WORKSPACE_MIGRATION_GUIDE.md` - Migration guide
- `docs\governance\POST_MIGRATION_CHECKS.md` - Verification steps

---

## 👷 Worker 6: Documentation & Status Updates

### Your Mission

Ensure all documentation is current and accurately reflects project status.

### Tasks

1. **Update Development Roadmap**
   - File: `docs\governance\DEVELOPMENT_ROADMAP.md`
   - Update current status based on worker progress
   - Mark completed tasks
   - Update next priorities

2. **Review Migration Log**
   - File: `docs\governance\Migration-Log.md`
   - Ensure all entries are accurate
   - Update status for completed tasks
   - Add any new tasks discovered

3. **Update README**
   - File: `README.md`
   - Ensure links are correct
   - Update status section if needed
   - Verify all key documents are linked

4. **Create Status Summary**
   - File: `docs\governance\CURRENT_STATUS.md` (new)
   - Summarize:
     - What's complete
     - What's in progress
     - What's next
     - Any blockers

5. **Verify Documentation Consistency**
   - Check that all docs reference E:\VoiceStudio (not C:\)
   - Verify all paths are correct
   - Ensure no conflicting information

### Deliverables

- ✅ Development roadmap updated
- ✅ Migration log current
- ✅ README accurate
- ✅ Status summary created
- ✅ Documentation consistent

### Reference Documents

- `docs\governance\DEVELOPMENT_ROADMAP.md` - Main roadmap
- `docs\governance\Migration-Log.md` - Migration tracking
- `README.md` - Project overview

---

## 📋 Overseer Coordination

### Daily Check-In

All workers should report:
1. **Status:** Not Started / In Progress / Complete / Blocked
2. **Progress:** What was accomplished
3. **Blockers:** Any issues preventing progress
4. **Next Steps:** What's planned next

### Quality Checks

Overseer will verify:
- ✅ No simplifications introduced
- ✅ File structure maintained
- ✅ Design tokens used (no hardcoded values)
- ✅ Tests pass
- ✅ Documentation updated

### Violation Remediation

If simplifications detected:
```
Revert simplifications. This UI is intentionally complex. 
Restore PanelHost and separate panel Views/ViewModels according to spec. 
Do not merge or collapse.
```

---

## 🎯 Success Criteria

### Phase 0 Complete When:
- [ ] XTTS Engine updated and tested
- [ ] Audio Utilities ported and tested
- [ ] All panels discovered and registered
- [ ] Backend API skeleton created
- [ ] Migration system ready
- [ ] Documentation current

### Ready for Phase 1 When:
- All Phase 0 tasks complete
- No blockers
- Tests passing
- Documentation accurate

---

## 📚 Key Reference Documents

- **[DEVELOPMENT_ROADMAP.md](DEVELOPMENT_ROADMAP.md)** - Main development plan
- **[PORT_TASKS_BATCH_1.md](PORT_TASKS_BATCH_1.md)** - Migration tasks
- **[CURSOR_OPERATIONAL_RULESET.md](../design/CURSOR_OPERATIONAL_RULESET.md)** - Operational rules
- **[VoiceStudio-Architecture.md](../design/VoiceStudio-Architecture.md)** - System architecture

---

**Overseer Note:** These prompts are designed to kick off parallel work while maintaining quality and complexity. Each worker has clear, actionable tasks with specific deliverables. Report progress and blockers immediately.

**Let's build this professional studio application! 🚀**

