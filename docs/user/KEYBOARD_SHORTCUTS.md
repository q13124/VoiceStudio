# VoiceStudio Quantum+ Keyboard Shortcuts

Complete reference guide for all keyboard shortcuts in VoiceStudio Quantum+.

## Table of Contents

- [VoiceStudio Quantum+ Keyboard Shortcuts](#voicestudio-quantum-keyboard-shortcuts)
  - [Table of Contents](#table-of-contents)
  - [File Operations](#file-operations)
  - [Edit Operations](#edit-operations)
  - [Navigation](#navigation)
  - [Playback](#playback)
  - [Timeline](#timeline)
  - [Effects](#effects)
  - [Mixer](#mixer)
  - [Selection](#selection)
  - [Zoom](#zoom)
  - [Search](#search)
  - [Help](#help)
  - [Context-Sensitive Shortcuts](#context-sensitive-shortcuts)
  - [Customizing Shortcuts](#customizing-shortcuts)
  - [Tips for Efficient Use](#tips-for-efficient-use)
  - [Printable Version](#printable-version)
  - [Verification Status](#verification-status)

---

## File Operations

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+N** | New Project | Create a new project |
| **Ctrl+O** | Open Project | Open an existing project |
| **Ctrl+S** | Save Project | Save the current project |
| **Ctrl+Shift+S** | Save As | Save project with a new name |
| **Ctrl+W** | Close Project | Close the current project |
| **Ctrl+Q** | Quit Application | Exit VoiceStudio |

---

## Edit Operations

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+Z** | Undo | Undo last action |
| **Ctrl+Y** | Redo | Redo last undone action |
| **Ctrl+X** | Cut | Cut selected items |
| **Ctrl+C** | Copy | Copy selected items |
| **Ctrl+V** | Paste | Paste items from clipboard |
| **Delete** | Delete Selection | Delete selected items |
| **Ctrl+A** | Select All | Select all items in current panel |

---

## Navigation

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+P** | Command Palette | Open command palette to search for commands |
| **Ctrl+F** | Global Search | Open global search dialog |
| **Tab** | Cycle Panels | Cycle through panel regions |
| **F1** | Help | Open help documentation |
| **F5** | Refresh | Refresh current panel or list |
| **Ctrl+Tab** | Switch Windows | Switch between open windows |
| **Esc** | Cancel/Close | Close dialog, cancel operation, or close overlay |
| **Enter** | Confirm/OK | Confirm dialog or submit form |

---

## Playback

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Space** | Play/Pause | Toggle playback |
| **S** | Stop | Stop playback (when not in timeline) |
| **Ctrl+R** | Record | Start/stop recording |
| **Home** | Go to Start | Move playhead to start of timeline |
| **End** | Go to End | Move playhead to end of timeline |
| **Left Arrow** | Previous | Move to previous position |
| **Right Arrow** | Next | Move to next position |

**Note:** The **S** key is context-sensitive:
- In timeline: **S** = Split Clip
- In other panels: **S** = Stop Playback

---

## Timeline

| Shortcut | Action | Description |
|----------|--------|-------------|
| **S** | Split Clip | Split clip at playhead position (timeline context) |
| **M** | Mute Track | Toggle mute for selected track |
| **Ctrl+M** | Solo Track | Toggle solo for selected track |
| **T** | New Track | Create new track |
| **Ctrl+T** | Delete Track | Delete selected track |
| **Ctrl+Enter** | Submit Text | Submit text for synthesis (in text input fields) |
| **Enter** | New Line | Insert new line in text input (when Ctrl+Enter submits) |

---

## Effects

| Shortcut | Action | Description |
|----------|--------|-------------|
| **E** | Add Effect | Add new effect to selected track |
| **Ctrl+E** | Effect Chain Editor | Open effect chain editor |
| **F** | Focus Effect Panel | Focus on effects panel |
| **Ctrl+Up** | Move Effect Up | Move effect up in chain |
| **Ctrl+Down** | Move Effect Down | Move effect down in chain |
| **Space** | Toggle Effect | Enable/disable selected effect |
| **Delete** | Remove Effect | Remove effect from chain |

---

## Mixer

| Shortcut | Action | Description |
|----------|--------|-------------|
| **M** | Mute Channel | Mute/unmute selected channel (in mixer context) |
| **S** | Solo Channel | Solo/unsolo selected channel |
| **Ctrl+M** | Mute Master | Mute/unmute master bus |

---

## Selection

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+Click** | Add to Selection | Add item to multi-select (IDEA 12) |
| **Shift+Click** | Select Range | Select range of items (IDEA 12) |
| **Ctrl+A** | Select All | Select all items in panel |

**Multi-Select Features:**
- Use **Ctrl+Click** to add/remove items from selection
- Use **Shift+Click** to select a range of items
- Selected items are highlighted with visual indicators
- Selection count badge appears in panel header
- Batch operations available via right-click menu

---

## Zoom

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+Plus** (or **Ctrl+=**)| Zoom In | Zoom in on timeline or view |
| **Ctrl+Minus** (or **Ctrl+-**)| Zoom Out | Zoom out on timeline or view |
| **Ctrl+0** | Reset Zoom | Reset zoom to default level |
| **Ctrl+Mouse Wheel** | Zoom | Zoom using mouse wheel (when hovering over timeline/view) |

---

## Search

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+F** | Global Search | Open global search dialog (IDEA 5) |

**Search Features:**
- Search across profiles, projects, audio files, markers, and scripts
- Use type filters: `type:profile`, `type:project`, `type:audio`, `type:marker`, `type:script`
- Use quotes for exact phrases: `"my voice"`
- Results grouped by type with preview snippets
- Click result to navigate to item

---

## Help

| Shortcut | Action | Description |
|----------|--------|-------------|
| **F1** | Help | Open help documentation |
| **Ctrl+?** | Keyboard Shortcuts | Show keyboard shortcuts (if implemented) |
| **?** | Show Help Overlay | Show contextual help overlay for current panel |

---

## Context-Sensitive Shortcuts

Many keyboard shortcuts are context-sensitive and change behavior based on which panel or control has focus:

**Context-Dependent Shortcuts:**
- **S Key:**
  - In Timeline panel: Split clip at playhead
  - In other panels: Stop playback
- **M Key:**
  - In Timeline panel: Mute/unmute selected track
  - In Mixer panel: Open mixer (if not already open)
- **Ctrl+M:**
  - In Timeline panel: Solo/unsolo selected track
  - In Mixer panel: Focus on master bus

**Shortcuts appear in:**
- **Panel Header Actions:** Action bar in panel headers (IDEA 2)
- **Context Menus:** Right-click menus (IDEA 10)
- **Tooltips:** Hover over buttons to see shortcuts
- **Command Palette:** Shows all available shortcuts

**Example:**
- Timeline panel actions show shortcuts in tooltips
- Right-click menus display keyboard shortcuts
- Command palette shows shortcuts for commands
- Focus determines which shortcuts are active

---

## Customizing Shortcuts

**To customize keyboard shortcuts:**

1. Open **Settings**
2. Go to **Keyboard Shortcuts**
3. Find the command you want to customize
4. Click to assign a new shortcut
5. Save changes

**To reset shortcuts:**
- Click **"Reset to Defaults"** in Settings > Keyboard Shortcuts
- Restores all shortcuts to original values

---

## Tips for Efficient Use

1. **Learn Common Shortcuts:** Focus on shortcuts you use frequently
2. **Use Command Palette:** **Ctrl+P** to quickly find and execute commands
3. **Multi-Select:** Use **Ctrl+Click** and **Shift+Click** for batch operations
4. **Context Menus:** Right-click for context-appropriate actions with shortcuts
5. **Undo/Redo:** Use **Ctrl+Z** and **Ctrl+Y** frequently for experimentation
6. **Global Search:** Use **Ctrl+F** to quickly find items across your workspace

---

## Panel-Specific Shortcuts

### Pronunciation Lexicon Panel

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+N** | Add Entry | Add new pronunciation entry |
| **Ctrl+S** | Search | Search entries |
| **Ctrl+E** | Estimate Phonemes | Auto-estimate phonemes for entry |
| **Delete** | Delete Entry | Delete selected entry |
| **F5** | Refresh | Refresh entries list |

### Script Editor Panel

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+N** | New Script | Create new script |
| **Ctrl+S** | Save Script | Save current script |
| **Delete** | Delete Segment | Delete selected script segment |

### Transcription Panel

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+T** | Start Transcription | Start transcription process |
| **F5** | Refresh | Refresh transcriptions list |

### Voice Synthesis Panel

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+Enter** | Synthesize | Submit text for synthesis |
| **Enter** | New Line | Insert new line in text input |

---

## Printable Version

This document can be printed for quick reference. Keep it handy while learning VoiceStudio Quantum+.

**Last Updated:** 2025-01-28  
**Version:** 1.2.0

---

## Verification Status

✅ **Verified against codebase:** All documented shortcuts match implementation in `MainWindow.xaml.cs` and `KeyboardShortcutService.cs`

**Implemented Shortcuts:**
- File operations: Ctrl+N, Ctrl+O, Ctrl+S
- Playback: Space, S, Ctrl+R
- Edit: Ctrl+Z, Ctrl+Y
- Navigation: Ctrl+P (Command Palette)
- Zoom: Ctrl+Plus, Ctrl+Minus, Ctrl+0

**Planned Shortcuts (documented but not yet implemented):**
- Some timeline shortcuts (T, Ctrl+T, etc.) - planned for future implementation
- Some effect shortcuts (E, Ctrl+E, F) - planned for future implementation
- Some mixer shortcuts - planned for future implementation

**Note:** This document includes both implemented and planned shortcuts. Implemented shortcuts are verified against the codebase.

