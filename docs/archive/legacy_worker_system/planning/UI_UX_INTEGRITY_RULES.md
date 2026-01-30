# UI/UX Integrity Rules
## VoiceStudio Quantum+ - Design Language Preservation

**Last Updated:** 2025-01-27  
**Purpose:** Ensure all UI work preserves the original approved design and maintains professional DAW-grade standards.

---

## 🎨 Core Design Principles

**VoiceStudio's interface is a professional, information-dense DAW-style dashboard. All UI work must preserve this design.**

---

## ✅ Required Rules

### 1. WinUI 3 Native Only

**MANDATORY:**
- ✅ Use only WinUI 3 controls and XAML
- ✅ Native Windows application (no web technologies)
- ✅ Full native performance and integration

**PROHIBITED:**
- ❌ React, Electron, webviews, or other frameworks
- ❌ Cross-platform widgets
- ❌ Web-based components
- ❌ Framework migrations

**Rationale:** The app must remain a full native Windows application with optimal performance and Windows integration.

---

### 2. Docked, Modular Panels

**MANDATORY:**
- ✅ Follow approved layout: panels must be dockable
- ✅ Panels must be resizable and rearrangeable
- ✅ Main window uses central waveform view with collapsible side panels
- ✅ PanelHost system for all panels
- ✅ 3-column + nav + bottom deck layout maintained

**Layout Structure:**
```
3-Row Grid:
├── Row 0: Top Command Deck
├── Row 1: Main Workspace (4-Column Grid)
│   ├── Column 0: Nav Rail (64px)
│   ├── Column 1: LeftPanelHost (20% width)
│   ├── Column 2: CenterPanelHost (55% width)
│   └── Column 3: RightPanelHost (25% width)
└── Row 2: Status Bar (26px)
```

**PROHIBITED:**
- ❌ Fixed, non-dockable panels
- ❌ Merged panels
- ❌ Simplified layouts
- ❌ Reduced panel count

---

### 3. Design Consistency

**MANDATORY:**
- ✅ Apply established theme and components (fonts, colors, icons)
- ✅ Use DesignTokens.xaml for ALL styling
- ✅ Maintain clarity and consistency
- ✅ Consistent fonts and spacings
- ✅ Uniform look & feel
- ✅ Visual hierarchy matches style guidelines
- ✅ Feedback cues match style guidelines

**Design Token Usage:**
- `VSQ.*` resources from DesignTokens.xaml
- No hardcoded colors, typography, or spacing
- Consistent corner radius, shadows, borders
- Theme-aware styling

**PROHIBITED:**
- ❌ Hardcoded colors or values
- ❌ Inconsistent styling
- ❌ Random color schemes
- ❌ Mixed design languages

---

### 4. Premium Details

**MANDATORY:**
- ✅ High-quality polish (subtle animations)
- ✅ No generic stock imagery
- ✅ Consistent alignments
- ✅ Smooth transitions on panel toggles
- ✅ All interface elements follow color palette
- ✅ Typography rules followed
- ✅ Professional DAW-grade appearance

**Premium Features:**
- Smooth animations and transitions
- Polished micro-interactions
- Consistent visual feedback
- Professional spacing and alignment
- High-quality icons and graphics

**PROHIBITED:**
- ❌ Generic, unpolished UI
- ❌ Inconsistent animations
- ❌ Poor alignment or spacing
- ❌ Stock imagery
- ❌ Unprofessional appearance

---

## 🚨 Violation Detection

### UI Change Violations

**Overseer Must Reject:**
- UI changes violating WinUI 3 native requirement
- Layout changes reducing dockability
- Design inconsistencies
- Hardcoded styling values
- Reduced premium polish
- Framework migrations

**Rejection Process:**
1. Overseer detects violation
2. Overseer rejects change
3. Worker must correct before merging
4. Overseer verifies correction

---

## 🔍 Design Validation Process

### Overseer Validation Steps

1. **Pixel-Perfect Check:**
   - Compare UI against approved design spec
   - Verify pixel-accuracy of all elements
   - Check colors, fonts, icons, layouts

2. **Design Language Check:**
   - Verify WinUI 3 native compliance
   - Check dockable panel system
   - Validate design token usage
   - Confirm premium polish

3. **Layout Check:**
   - Verify 3-column + nav + bottom deck
   - Check panel docking functionality
   - Validate panel resizing
   - Confirm information density

4. **Consistency Check:**
   - Verify consistent styling
   - Check design token usage
   - Validate theme application
   - Confirm visual hierarchy

---

## 📋 UI Work Checklist

**Before Submitting UI Changes:**

- [ ] Uses WinUI 3 native controls only
- [ ] Maintains dockable panel system
- [ ] Uses DesignTokens.xaml for all styling
- [ ] Preserves 3-column + nav + bottom deck layout
- [ ] Maintains information density
- [ ] Applies premium polish
- [ ] Follows design language consistently
- [ ] No hardcoded values
- [ ] Pixel-accurate to design spec
- [ ] Professional DAW-grade appearance

---

## 🎯 Design Spec Reference

**Key Documents:**
- `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` - Master spec
- `UI_IMPLEMENTATION_SPEC.md` - UI specification
- `DesignTokens.xaml` - Design token definitions
- `MAINWINDOW_STRUCTURE.md` - Layout structure

---

## 📚 Related Documents

- `GUARDRAILS.md` - General development guardrails
- `CURSOR_GUARDRAILS.md` - Cursor-specific rules
- `OVERSEER_SYSTEM_PROMPT_V2.md` - Overseer validation process
- `BRAINSTORMER_PROTOCOL.md` - Idea generation rules

---

**All UI work must preserve the professional DAW-grade design. Any violations must be corrected before merging.**

