# Cursor Workspace Setup for VoiceStudio
## Quick Start Guide

**When you open Cursor, set the workspace to `E:\VoiceStudio` and read this document first.**

---

## 🎯 Workspace Configuration

### Active Repository (Authoritative)
- **`E:\VoiceStudio`** - **ONLY** place where code is written
- Set this as your Cursor workspace
- All modifications, creations, and updates happen here

### Reference Repository (Read-Only)
- **`C:\VoiceStudio`** - Read-only reference (if present)
- **`C:\OldVoiceStudio`** - Read-only reference (if present)
- These are **archive/reference only** - do not modify

---

## 📋 Initial Setup Message for Cursor

When opening Cursor, paste this message:

```
VoiceStudio workspace setup

Active repo: E:\VoiceStudio (this is the only place you should write code).

Old repo for reference only: C:\VoiceStudio (read-only, do not modify or bulk-copy).

Use the latest architecture & roadmap in:
- docs\design\VoiceStudio-Architecture.md
- docs\governance\Cursor-Migration-Ruleset.md

When I say PORT: ..., you will:
1. Read the source file(s) from C:\VoiceStudio
2. Implement a new adapted module under E:\VoiceStudio that matches the current architecture
3. Log the migration in docs\governance\Migration-Log.md
```

---

## 🔄 PORT Command Format

When you receive a PORT command, follow this format:

```
PORT: [Module Name]
Source: C:\VoiceStudio\[path]
Target: E:\VoiceStudio\[path]
```

### Example 1: Port an Engine

```
PORT: XTTS Engine Wrapper
Source: C:\VoiceStudio\app\core\engines\xtts_engine.py
Target: E:\VoiceStudio\app\core\engines\xtts_engine.py
```

**What Cursor should do:**
1. Read `C:\VoiceStudio\app\core\engines\xtts_engine.py`
2. Adapt to engine protocol in new architecture
3. Remove legacy paths and UI coupling
4. Create `E:\VoiceStudio\app\core\engines\xtts_engine.py`
5. Add CLI test: `E:\VoiceStudio\app\cli\xtts_test.py`
6. Update `docs\governance\Migration-Log.md`

### Example 2: Port a UI Panel

```
PORT: Studio Panel
Reference only: C:\VoiceStudio\ui\studio_panel.py
Target: E:\VoiceStudio\app\ui\panels\studio_panel.py
```

**What Cursor should do:**
1. Read `C:\VoiceStudio\ui\studio_panel.py` for layout/feature reference
2. Rebuild using new PySide6/qfluentwidgets design
3. Use old file only as layout/feature reference
4. Create `E:\VoiceStudio\app\ui\panels\studio_panel.py`
5. Update `docs\governance\Migration-Log.md`

---

## 📚 Key Documents

### Must Read First
1. **`docs\governance\Cursor-Migration-Ruleset.md`** - Migration rules and workflow
2. **`docs\design\VoiceStudio-Architecture.md`** - Current architecture
3. **`docs\governance\Migration-Log.md`** - Track all migrations

### Reference Documents
- **`docs\design\CURSOR_OPERATIONAL_RULESET.md`** - Complete operational rules
- **`docs\design\TECHNICAL_STACK_SPECIFICATION.md`** - Version requirements
- **`docs\design\PANEL_IMPLEMENTATION_GUIDE.md`** - Panel development guide

---

## 🚨 Critical Rules

1. **Never modify `C:\VoiceStudio`** - It's read-only reference
2. **Never bulk copy** - Always read and recreate
3. **Always adapt** - Don't copy blindly, update to match architecture
4. **Always log** - Document every migration in Migration-Log.md
5. **Always test** - Verify functionality after porting
6. **One copy per module** - Keep disk usage efficient

---

## 💾 Disk Space Management

### Large Assets Location
- **Models:** `E:\VoiceStudio_models\...`
- **Cache/Output:** `E:\VoiceStudio_data\...`
- **Temp Audio:** `E:\VoiceStudio_data\temp\...`

### Configuration
- New code on `E:\VoiceStudio` references `E:` paths
- Use config file that points to `E:` locations
- **Do NOT** reference `C:` paths in new code

---

## ✅ Quick Checklist

Before starting work:

- [ ] Workspace set to `E:\VoiceStudio`
- [ ] Read `Cursor-Migration-Ruleset.md`
- [ ] Read `VoiceStudio-Architecture.md`
- [ ] Understand read-only nature of `C:\VoiceStudio`
- [ ] Ready to receive PORT commands

---

**This workspace setup ensures clean, efficient development with proper separation between active and reference code.**

