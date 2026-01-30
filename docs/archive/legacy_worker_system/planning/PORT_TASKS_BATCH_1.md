# PORT Tasks Batch 1 - First 3 Migration Tasks
## Detailed Instructions for Cursor

**Purpose:** Jump-start the migration process by porting useful parts from `C:\VoiceStudio` to `E:\VoiceStudio`

**Note:** After completing these 3 tasks, see `BULK_PANEL_MIGRATION_GUIDE.md` for migrating ~200 panels.

**Last Updated:** 2025

---

## 🎯 PORT Task 1: XTTS Engine

### Source
- **Path:** `C:\VoiceStudio\app\core\engines\xtts_engine.py`
- **Type:** Read-only reference

### Target
- **Path:** `E:\VoiceStudio\app\core\engines\xtts_engine.py`
- **Status:** ⚠️ Needs update to use `protocols.py` instead of `base.py`

### Cursor Tasks

1. **Read Source File**
   - Open `C:\VoiceStudio\app\core\engines\xtts_engine.py` (read-only)
   - Understand the logic, structure, and functionality
   - Note any useful patterns or implementations

2. **Check Current Implementation**
   - Review existing `E:\VoiceStudio\app\core\engines\xtts_engine.py`
   - Note: Currently uses `base.py` for `EngineProtocol`
   - **Update Required:** Use `app\core\engines\protocols.py` instead (create if needed)

3. **Implement/Update Engine**
   - Use the current `EngineProtocol` from `app\core\engines\protocols.py`
   - Reuse as much logic as possible from source
   - Update paths:
     - Remove any `C:` path references
     - Use `%PROGRAMDATA%\VoiceStudio\models` for model cache
     - Use `E:\VoiceStudio_data\...` for cache/output
   - Remove UI references (no WinUI 3 or old UI coupling)
   - Align with new architecture from `docs\design\VoiceStudio-Architecture.md`

4. **Create CLI Test Harness**
   - **File:** `E:\VoiceStudio\app\cli\xtts_test.py`
   - Use the new engine class to generate a sample WAV output
   - Test initialization, synthesis, and cleanup
   - Include command-line arguments for reference audio

5. **Update Migration Log**
   - Mark XTTS Engine as complete in `docs\governance\Migration-Log.md`
   - Note any adaptations made
   - Document test results

### Expected Deliverables
- ✅ Updated `xtts_engine.py` using `protocols.py`
- ✅ CLI test harness `xtts_test.py`
- ✅ Migration log entry updated
- ✅ Engine works with new architecture

---

## 🎯 PORT Task 2: Audio Utilities

### Source
- **Path:** `C:\VoiceStudio\app\core\audio\audio_utils.py`
- **Type:** Read-only reference

### Target
- **Path:** `E:\VoiceStudio\app\core\audio\audio_utils.py`
- **Status:** 📋 Pending

### Cursor Tasks

1. **Inspect Source File**
   - Open `C:\VoiceStudio\app\core\audio\audio_utils.py` (read-only)
   - Identify useful functions:
     - `normalize_lufs()` - LUFS normalization
     - `detect_silence()` - Silence detection
     - `resample_audio()` - Audio resampling
     - `convert_format()` - Format conversion
     - Any other audio processing utilities
   - Understand dependencies and imports

2. **Implement in New Structure**
   - Create `E:\VoiceStudio\app\core\audio\audio_utils.py`
   - Port useful functions with adaptations:
     - **Update imports:** Match new structure (no old UI paths)
     - **Remove UI references:** No WinUI 3 or old UI coupling
     - **Update paths:** Use `E:\VoiceStudio_data\...` for temp files
     - **Version compatibility:** Ensure compatible with:
       - Librosa 0.11.0
       - SoundFile 0.12.1
       - NumPy 1.26.4
       - pyloudnorm 0.1.1

3. **Create Test File**
   - **File:** `E:\VoiceStudio\app\core\audio\test_audio_utils.py`
   - Include 2-3 basic tests:
     - Test LUFS normalization
     - Test silence detection
     - Test format conversion (if applicable)
   - Use pytest or unittest framework
   - Create sample audio files for testing

4. **Update Migration Log**
   - Add entry in `docs\governance\Migration-Log.md`
   - Mark as complete [x]
   - Note functions ported and any adaptations

### Expected Deliverables
- ✅ `audio_utils.py` with ported functions
- ✅ `test_audio_utils.py` with 2-3 tests
- ✅ All imports match new structure
- ✅ No legacy UI references
- ✅ Migration log entry

### Useful Functions to Look For
- Audio I/O (load, save)
- Normalization (LUFS, peak)
- Silence detection/removal
- Resampling
- Format conversion
- Audio analysis (duration, sample rate, channels)
- Audio manipulation (trim, pad, mix)

---

## 🎯 PORT Task 3: Studio Panel UI

### Source
- **Path:** `C:\VoiceStudio\ui\studio_panel.py`
- **Type:** Read-only reference

### Target
- **Path:** `E:\VoiceStudio\app\ui\panels\studio_panel.py`
- **Status:** 📋 Pending

### Cursor Tasks

1. **Inspect Source Panel**
   - Open `C:\VoiceStudio\ui\studio_panel.py` (read-only)
   - Understand:
     - **Controls:** What sliders, buttons, meters exist
     - **Layout:** Sections (input, output, effects, etc.)
     - **Functionality:** What the panel does
     - **Data bindings:** What data it displays/manipulates
   - Note: Use as **layout/feature reference only**

2. **Rebuild with PySide6 + qfluentwidgets**
   - **File:** `E:\VoiceStudio\app\ui\panels\studio_panel.py`
   - Follow UI design guidelines in `docs\design\VoiceStudio-Architecture.md`
   - Use PySide6 6.8.0.1 + qfluentwidgets 1.4.3
   - Implement:
     - **Docking system:** Use new docking conventions
     - **Theme support:** Use theme system (Dark/SciFi/Light)
     - **Color scheme:** Use design tokens, no hardcoded colors
     - **Layout:** Recreate layout with new components
   - **Do NOT copy** - rebuild with new architecture

3. **Wire into Main Window**
   - **Do NOT copy old window wiring**
   - Integrate with new panel system:
     - Register in `PanelRegistry`
     - Use `PanelHost` or `PanelStack`
     - Follow MVVM pattern
   - Ensure panel appears in correct region (Center or Left)

4. **Test Panel**
   - Create minimal app launch test
   - Verify:
     - Panel loads without errors
     - Controls are functional
     - Theme applies correctly
     - Docking works
   - Fix any issues found

5. **Update Migration Log**
   - Add entry in `docs\governance\Migration-Log.md`
   - Mark as complete [x]
   - Note UI framework used and adaptations

### Expected Deliverables
- ✅ `studio_panel.py` rebuilt with PySide6/qfluentwidgets
- ✅ Panel registered in PanelRegistry
- ✅ Panel wired into main window
- ✅ Panel loads and works correctly
- ✅ Migration log entry

### UI Framework Requirements
- **PySide6:** 6.8.0.1
- **qfluentwidgets:** 1.4.3
- **PySide6-Fluent-Widgets:** 1.6.6 (optional, for Fluent controls)
- Follow Fluent design system

---

## 📋 How Cursor Should Handle PORT Tasks

### General Workflow

1. **Read Source (Read-Only)**
   - Open file from `C:\VoiceStudio` (read-only reference)
   - Understand structure, logic, and functionality
   - Note useful patterns

2. **Rebuild in Active Project**
   - Create new file in `E:\VoiceStudio`
   - **Do NOT copy** - rebuild with adaptations:
     - Update to new architecture
     - Remove legacy dependencies
     - Update paths and configs
     - Use current design patterns

3. **Test After Migration**
   - Create tests (CLI or unit tests)
   - Verify functionality works
   - Fix any issues

4. **Log Migration**
   - Update `docs\governance\Migration-Log.md`
   - Mark checkbox as complete [x]
   - Note adaptations and status

### Critical Rules

- ✅ **Read from `C:\VoiceStudio`** (read-only)
- ✅ **Write to `E:\VoiceStudio`** (active project)
- ✅ **Adapt, don't copy** - update to new architecture
- ✅ **Test after migration** - verify functionality
- ✅ **Log everything** - document in Migration-Log.md
- ❌ **Never modify `C:\VoiceStudio`** - it's read-only
- ❌ **Never bulk copy** - always rebuild with updates

---

## ✅ Completion Checklist

After completing all 3 PORT tasks:

- [ ] XTTS Engine updated and tested
- [ ] Audio Utilities ported and tested
- [ ] Studio Panel UI rebuilt and integrated
- [ ] All migration log entries updated
- [ ] All tests pass
- [ ] No legacy dependencies
- [ ] All paths updated to use `E:` or `%PROGRAMDATA%`
- [ ] No UI coupling in engine/utilities

---

## 📚 Reference Documents

- **Migration Rules:** `docs\governance\Cursor-Migration-Ruleset.md`
- **Architecture:** `docs\design\VoiceStudio-Architecture.md`
- **Migration Log:** `docs\governance\Migration-Log.md`
- **Technical Stack:** `docs\design\TECHNICAL_STACK_SPECIFICATION.md`
- **Operational Ruleset:** `docs\design\CURSOR_OPERATIONAL_RULESET.md`

---

**These 3 PORT tasks will establish the foundation for migrating the rest of the codebase from `C:\VoiceStudio` to `E:\VoiceStudio`.**

