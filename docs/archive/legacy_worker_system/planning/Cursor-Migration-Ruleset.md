# Cursor Migration Ruleset for VoiceStudio
## Workspace Setup and Porting Guidelines

**Version:** 1.0  
**Last Updated:** 2025  
**Purpose:** Definitive rules for porting code from reference directory to active project

---

## 🎯 Workspace Setup

### Active Repository (Authoritative)
- **`E:\VoiceStudio`** - **ONLY** place where code is written
- This is the **active, authoritative project directory**
- All modifications, creations, and updates happen here
- This is the **primary working directory**

### Reference Repository (Read-Only)
- **`C:\VoiceStudio`** - **Read-only reference** (if present)
- **`C:\OldVoiceStudio`** - **Read-only reference** (if present)
- These directories are **archive/reference only**

### Cursor MUST:

1. **Set workspace to `E:\VoiceStudio`** when opening Cursor
2. **Treat `E:\VoiceStudio` as the ONLY place for changes:**
   - All new code goes here
   - All edits happen here
   - All file creation happens here
   - This is the authoritative source

3. **Treat `C:\VoiceStudio` and `C:\OldVoiceStudio` as read-only reference:**
   - ✅ **MAY** open and read files there
   - ✅ **MAY** reference code/patterns from there
   - ✅ **MAY** use as inspiration or reference
   - ❌ **MAY NOT** modify or create files there
   - ❌ **MAY NOT** bulk copy directories from there into `E:\VoiceStudio`
   - ❌ **MAY NOT** write to these directories

---

## 📋 PORT Command Workflow

When you receive a **PORT:** command, follow this workflow:

### Format
```
PORT: [Module Name]
Source: C:\VoiceStudio\[path]
Target: E:\VoiceStudio\[path]
```

### Steps

1. **Read Source File(s)**
   - Open and read the source file(s) from `C:\VoiceStudio`
   - Understand the code structure, patterns, and functionality
   - Note any dependencies or external references

2. **Analyze Architecture Compatibility**
   - Check against current architecture in `docs\design\VoiceStudio-Architecture.md`
   - Verify compatibility with new structure
   - Identify what needs to be adapted

3. **Implement Adapted Module**
   - Create new file(s) in `E:\VoiceStudio` (not copy)
   - Adapt to current architecture:
     - Update import paths
     - Remove legacy UI coupling
     - Follow new engine protocol
     - Use current design patterns
   - Ensure no legacy paths or dependencies

4. **Add Tests (if applicable)**
   - Create CLI test under `E:\VoiceStudio\app\cli\[module]_test.py`
   - Verify functionality works in new architecture

5. **Update Migration Log**
   - Log the migration in `docs\governance\Migration-Log.md`
   - Include:
     - Source path
     - Target path
     - Date
     - Changes made
     - Compatibility notes

---

## 🔄 Migration Principles

### No Bulk Copying
- **Never bulk copy** directories from reference to active project
- **Read and recreate** patterns instead
- Maintain active project structure

### Adaptation, Not Copying
- **Read** the pattern from reference directory
- **Understand** the functionality
- **Recreate** in active project with updates:
  - Update to match current architecture
  - Remove legacy dependencies
  - Use current design patterns
  - Follow new protocols

### One Copy Per Module
- Keep disk usage "one copy per module" on E (plus original on C)
- Not a full cloned repo
- Only port what's needed, when needed

### Architecture Compliance
- All ported code must match current architecture
- No legacy paths
- No legacy UI coupling
- Follow engine protocols
- Use current design patterns

---

## 📁 Example Porting Scenarios

### Example 1: Port an Engine

**Command:**
```
PORT: XTTS Engine Wrapper
Source: C:\VoiceStudio\app\core\engines\xtts_engine.py
Target: E:\VoiceStudio\app\core\engines\xtts_engine.py
```

**Steps:**
1. Read `C:\VoiceStudio\app\core\engines\xtts_engine.py`
2. Adapt to engine protocol in new architecture
3. Remove legacy paths and UI coupling
4. Create `E:\VoiceStudio\app\core\engines\xtts_engine.py`
5. Add CLI test: `E:\VoiceStudio\app\cli\xtts_test.py`
6. Update `docs\governance\Migration-Log.md`

### Example 2: Port a UI Panel

**Command:**
```
PORT: Studio Panel
Reference only: C:\VoiceStudio\ui\studio_panel.py
Target: E:\VoiceStudio\app\ui\panels\studio_panel.py
```

**Steps:**
1. Read `C:\VoiceStudio\ui\studio_panel.py` for layout/feature reference
2. Rebuild using new PySide6/qfluentwidgets design
3. Use old file only as layout/feature reference
4. Create `E:\VoiceStudio\app\ui\panels\studio_panel.py`
5. Update `docs\governance\Migration-Log.md`

---

## 💾 Disk Space Management

### Large Assets Location
Since `C:` is cramped, put all large assets on `E:` or another data drive:

- **Models:** `E:\VoiceStudio_models\...`
- **Cache/Output:** `E:\VoiceStudio_data\...`
- **Temp Audio:** `E:\VoiceStudio_data\temp\...`

### Configuration
- Have new code on `E:\VoiceStudio` reference those paths
- Use config file that points to `E:` locations
- **Do NOT** reference `C:` paths in new code

### Old Models
- Leave old big models on `C:` for now
- Once everything important is running on `E:`, you can safely delete or archive old weight off `C:` to reclaim space

---

## ✅ Pre-Port Checklist

Before porting any module:

- [ ] Verify working in `E:\VoiceStudio` (active project)
- [ ] Read source file(s) from `C:\VoiceStudio` (reference)
- [ ] Understand current architecture from `docs\design\VoiceStudio-Architecture.md`
- [ ] Check compatibility with new structure
- [ ] Plan adaptation strategy
- [ ] Identify what needs updating
- [ ] Plan test approach
- [ ] Prepare migration log entry

---

## 📝 Migration Log Requirements

Each migration must be logged in `docs\governance\Migration-Log.md` with:

- **Date:** When migration occurred
- **Module Name:** What was ported
- **Source Path:** Original location in `C:\VoiceStudio`
- **Target Path:** New location in `E:\VoiceStudio`
- **Changes Made:** What was adapted/updated
- **Compatibility Notes:** Any compatibility issues or solutions
- **Tests Added:** Test files created
- **Status:** Complete / In Progress / Blocked

---

## 🚨 Critical Rules

1. **Never modify `C:\VoiceStudio`** - It's read-only reference
2. **Never bulk copy** - Always read and recreate
3. **Always adapt** - Don't copy blindly, update to match architecture
4. **Always log** - Document every migration
5. **Always test** - Verify functionality after porting
6. **One copy per module** - Keep disk usage efficient

---

## 📚 Reference Documents

- **Architecture:** `docs\design\VoiceStudio-Architecture.md`
- **Migration Log:** `docs\governance\Migration-Log.md`
- **Operational Ruleset:** `docs\design\CURSOR_OPERATIONAL_RULESET.md`
- **Technical Stack:** `docs\design\TECHNICAL_STACK_SPECIFICATION.md`

---

**This ruleset ensures clean, efficient migration from reference to active project while maintaining architecture compliance and disk efficiency.**

