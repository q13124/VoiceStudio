# Worker 2: UI/UX Polish + Legacy Audio + Image Engines
## VoiceStudio Quantum+ - Phase 6 & Phase 7 Specialist

**Role:** Frontend/User Experience + Legacy Audio + Image Engine Implementation  
**Timeline:** Phase 6: Complete ✅ + Phase 7: 12-15 days  
**Priority:** High  
**Status:** 🟢 Ready to Begin Phase 7

---

## 🆕 PHASE 7: ENGINE IMPLEMENTATION (CURRENT PRIORITY)

**YOU ARE RESPONSIBLE FOR IMPLEMENTING 18 ENGINES:**

### Legacy Audio Engines (5 engines - START IMMEDIATELY):
1. **MaryTTS** - Classic open-source multilingual TTS
2. **Festival/Flite** - Legacy TTS system
3. **eSpeak NG** - Compact multilingual TTS
4. **RHVoice** - Multilingual TTS with high-quality voices
5. **OpenVoice** - Quick cloning option (update if needed)

### Image Engines (13 engines - START IMMEDIATELY):
1. **SDXL ComfyUI** - Stable Diffusion XL via ComfyUI
2. **ComfyUI** - Node-based workflow engine
3. **AUTOMATIC1111 WebUI** - Popular Stable Diffusion WebUI
4. **SD.Next** - Advanced AUTOMATIC1111 fork
5. **InvokeAI** - Professional Stable Diffusion pipeline
6. **Fooocus** - Simplified quality-focused interface
7. **LocalAI** - Local inference server
8. **SDXL** - High-resolution Stable Diffusion XL
9. **Realistic Vision** - Photorealistic model
10. **OpenJourney** - Midjourney-style generation
11. **Stable Diffusion CPU-only** - CPU-only forks
12. **FastSD CPU** - Fast CPU-optimized inference
13. **Real-ESRGAN** - Image/video upscaling

### ⚠️ CRITICAL: Settings & Preferences System (MUST CREATE FIRST):

**Settings/Preferences System is MISSING and MUST be created:**

1. **SettingsView** - Comprehensive settings panel ⚠️ **MISSING**
   - Location: `src/VoiceStudio.App/Views/Panels/SettingsView.xaml`
   - Purpose: Application-wide settings and preferences
   - Categories:
     - General (Theme, Language, Auto-save, etc.)
     - Engine (Default engine, Quality settings)
     - Audio (Devices, Sample rate, Buffer size)
     - Timeline (Time format, Snap, Grid)
     - Backend (API URL, Timeout, Retry)
     - Performance (Caching, Threading, Memory)
     - Plugins (Plugin management)
     - MCP (MCP server configuration)
   - Backend: Integrate with `/api/settings/*`
   - Priority: **CRITICAL** - Do this FIRST

### ⚠️ CRITICAL: Missing UI Panels (MUST CREATE):

**3 UI Panels are MISSING and MUST be created:**

1. **ImageGenView** - Image generation panel ⚠️ **MISSING**
   - Location: `src/VoiceStudio.App/Views/Panels/ImageGenView.xaml`
   - Purpose: Interface for all 13 image generation engines
   - Features:
     - Engine selection dropdown
     - Prompt input (text-to-image)
     - Image input (image-to-image)
     - Parameter controls (CFG scale, steps, seed, etc.)
     - Preview area
     - Batch generation
     - Image gallery/history
   - Backend: Integrate with `/api/image/generate`

2. **VideoGenView** - Video generation panel ⚠️ **MISSING**
   - Location: `src/VoiceStudio.App/Views/Panels/VideoGenView.xaml`
   - Purpose: Interface for video generation engines (SVD, Deforum, etc.)
   - Features:
     - Engine selection dropdown
     - Image input (for image-to-video)
     - Text prompt (for text-to-video)
     - Parameter controls
     - Preview area
     - Video timeline preview
     - Batch generation
   - Backend: Integrate with `/api/video/generate`

3. **VideoEditView** - Video editing panel ⚠️ **MISSING**
   - Location: `src/VoiceStudio.App/Views/Panels/VideoEditView.xaml`
   - Purpose: Interface for video editing engines (MoviePy, FFmpeg AI)
   - Features:
     - Video timeline editor
     - Clip trimming/splitting
     - Effect application
     - Transition controls
     - Export options
   - Backend: Integrate with `/api/video/edit`

**Priority Order:**
1. **FIRST:** Create 3 missing UI panels (ImageGenView, VideoGenView, VideoEditView)
2. **THEN:** Continue with engine implementations

### Implementation Requirements (100% COMPLETE - NO STUBS):

**For Each Engine:**
1. Create `app/core/engines/{engine_id}_engine.py`
2. Inherit from `EngineProtocol` (see `app/core/engines/protocols.py`)
3. Implement ALL methods (NO stubs/placeholders/TODOs)
4. Create backend API endpoints
5. Create UI panels for image generation (ImageGenView)
6. Test engine individually
7. Update documentation

**Timeline:** 12-15 days for all 18 engines

**See:** `docs/governance/ENGINE_IMPLEMENTATION_PLAN.md` for complete details

---

## 🎯 Your Mission (Phase 6 - Already Complete ✅)

You are responsible for polishing VoiceStudio's user interface, ensuring consistency, accessibility, and a smooth user experience. Your work enhances the user experience and makes the application production-ready.

**Phase 6 Status:** ✅ **COMPLETE** - All UI/UX polish tasks done

**Success Criteria:**
- ✅ All panels visually consistent (VSQ.* design tokens)
- ✅ All operations show loading states
- ✅ Full keyboard navigation works
- ✅ Screen reader compatible (tested with Narrator)
- ✅ Smooth animations and transitions
- ✅ User-friendly error messages and empty states

---

## 📋 Task Breakdown

### Day 1: UI Consistency Review

**Goal:** Ensure all panels use design tokens consistently

**Tasks:**

1. **Review All Panels for Design Token Consistency**
   - Check all 6 core panels (ProfilesView, TimelineView, EffectsMixerView, AnalyzerView, MacroView, DiagnosticsView)
   - Verify all use `VSQ.*` resources from DesignTokens.xaml
   - Document any hardcoded values found
   - Create checklist of panels reviewed

2. **Ensure Consistent Spacing and Typography**
   - Verify consistent margins/padding (use VSQ.Spacing.*)
   - Verify consistent font sizes (use VSQ.FontSize.*)
   - Verify consistent line heights
   - Ensure proper text hierarchy

3. **Verify All Panels Use DesignTokens.xaml**
   - Check that all XAML files merge DesignTokens.xaml
   - Verify no local ResourceDictionaries override tokens
   - Ensure App.xaml merges DesignTokens.xaml globally

4. **Fix Any Hardcoded Colors/Values**
   - Replace hardcoded colors with VSQ.* brushes
   - Replace hardcoded sizes with VSQ.* values
   - Replace hardcoded spacing with VSQ.Spacing.*
   - Document any exceptions (if absolutely necessary)

5. **Ensure Consistent Button Styles**
   - All buttons use consistent styling
   - Primary/secondary button styles consistent
   - Icon buttons consistent
   - Toggle buttons consistent

6. **Ensure Consistent Panel Headers**
   - All panels have consistent header styling
   - Header height consistent (32px per spec)
   - Header actions (close, minimize) consistent
   - Panel titles use consistent typography

**Deliverable:** UI consistency report, all hardcoded values fixed

**Files to Review:**
- `src/VoiceStudio.App/Views/Panels/*.xaml` (All panel XAML)
- `src/VoiceStudio.App/Resources/DesignTokens.xaml`
- `src/VoiceStudio.App/App.xaml` (Verify DesignTokens merge)

---

### Day 2: Loading States & Progress Indicators

**Goal:** Add loading feedback to all async operations

**Tasks:**

1. **Add Loading Animations to All Async Operations**
   - Voice synthesis operations
   - Profile loading/saving
   - Project loading/saving
   - Audio file loading
   - Engine initialization
   - Backend API calls

2. **Add Progress Indicators for Long-Running Tasks**
   - Training progress (already has WebSocket, enhance UI)
   - Batch processing progress
   - Audio processing progress
   - File upload/download progress
   - Model loading progress

3. **Add Loading States to Prevent Duplicate Operations**
   - Disable buttons during async operations
   - Show loading spinner on buttons
   - Prevent multiple clicks
   - Add cancellation support where appropriate

4. **Implement Skeleton Screens for Data Loading**
   - Profile list loading skeleton
   - Timeline loading skeleton
   - Project list loading skeleton
   - Use subtle animations for skeleton screens

5. **Add Progress Bars for Synthesis/Training/Batch Jobs**
   - Voice synthesis progress (if supported by engine)
   - Training progress (enhance existing)
   - Batch job progress (enhance existing)
   - Show percentage and estimated time remaining

**Deliverable:** Loading states on all async operations

**Key Files to Modify:**
- `src/VoiceStudio.App/Views/Panels/ProfilesViewModel.cs`
- `src/VoiceStudio.App/Views/Panels/TimelineViewModel.cs`
- `src/VoiceStudio.App/Views/Panels/VoiceSynthesisView.xaml`
- `src/VoiceStudio.App/Controls/` (Create loading controls if needed)

---

### Day 3: Tooltips & Help System

**Goal:** Add helpful tooltips and contextual help

**Tasks:**

1. **Add Tooltips to All Interactive Elements**
   - Buttons (what they do)
   - Input fields (format requirements, examples)
   - Sliders/controls (what they control)
   - Icons (what they represent)
   - Complex controls (how to use)

2. **Create Help Text for Complex Features**
   - Voice synthesis parameters
   - Quality metrics explanation
   - Mixer routing
   - Macro editor
   - Effects chain

3. **Add Contextual Help Buttons**
   - Add "?" help buttons to complex panels
   - Show help overlay on click
   - Link to documentation
   - Show feature explanations

4. **Implement Help Overlay System**
   - Create HelpOverlay control
   - Show contextual help for current panel
   - Highlight relevant UI elements
   - Dismissible with Escape key

5. **Add Keyboard Shortcut Hints**
   - Show keyboard shortcuts in tooltips
   - Add keyboard shortcut legend
   - Show shortcuts in Command Palette
   - Document common shortcuts

**Deliverable:** Complete tooltip and help system

**Key Files to Modify:**
- All panel XAML files (add ToolTip properties)
- `src/VoiceStudio.App/Controls/HelpOverlay.xaml` (Create if needed)
- `src/VoiceStudio.App/Resources/HelpText.xaml` (Create resource file)

---

### Day 4: Keyboard Navigation & Shortcuts

**Goal:** Full keyboard accessibility

**Tasks:**

1. **Add Keyboard Navigation Support**
   - Tab navigation works through all controls
   - Arrow keys navigate lists/grids
   - Enter activates buttons/links
   - Escape closes dialogs/overlays
   - Focus visible on all focusable elements

2. **Implement Keyboard Shortcuts System**
   - Create KeyboardShortcuts service
   - Register shortcuts for common actions
   - Show shortcuts in UI (tooltips, menu)
   - Support modifier keys (Ctrl, Alt, Shift)

3. **Add Ctrl+P for Command Palette**
   - Verify Command Palette works (if implemented)
   - Add keyboard shortcut
   - Test opening/closing
   - Ensure focus management works

4. **Add Ctrl+S for Save Operations**
   - Save current project
   - Save current profile
   - Show save dialog if needed
   - Show save confirmation

5. **Add Escape to Close Dialogs**
   - All dialogs close with Escape
   - Cancel operations with Escape
   - Close help overlays with Escape
   - Close context menus with Escape

6. **Add Enter to Submit Forms**
   - Submit forms with Enter key
   - Activate primary button with Enter
   - Handle multi-line inputs (Shift+Enter for new line)

7. **Test Full Keyboard-Only Navigation**
   - Navigate entire application with keyboard only
   - Complete common workflows with keyboard only
   - Verify all functionality accessible
   - Document any limitations

**Deliverable:** Full keyboard navigation working

**Key Files to Modify:**
- `src/VoiceStudio.App/Services/KeyboardShortcutsService.cs` (Create)
- All panel XAML (ensure TabIndex set correctly)
- All dialogs (ensure Escape handling)

---

### Day 5: Accessibility Improvements

**Goal:** Make application accessible to all users

**Tasks:**

1. **Improve Screen Reader Support**
   - Add AutomationProperties.Name to all controls
   - Add AutomationProperties.HelpText where needed
   - Ensure proper control labeling
   - Test with Windows Narrator

2. **Add High Contrast Mode Support**
   - Test application in high contrast mode
   - Ensure all text is readable
   - Ensure all controls are visible
   - Adjust colors if needed (use system colors)

3. **Ensure Proper Focus Management**
   - Focus moves logically through UI
   - Focus visible on all focusable elements
   - Focus returns to correct element after dialogs
   - Focus trapped in dialogs

4. **Add ARIA Labels Where Needed**
   - Use AutomationProperties for WinUI 3
   - Label complex controls
   - Describe relationships between controls
   - Indicate state changes

5. **Test with Screen Reader (Narrator)**
   - Navigate entire application with Narrator
   - Verify all controls are announced correctly
   - Verify all actions are clear
   - Fix any issues found

6. **Verify Keyboard Navigation Works**
   - All functionality accessible via keyboard
   - No mouse-only operations
   - Logical tab order
   - Keyboard shortcuts work

**Deliverable:** Application accessible and tested

**Key Files to Modify:**
- All panel XAML (add AutomationProperties)
- `src/VoiceStudio.App/Helpers/AutomationHelper.cs` (Use existing or enhance)

---

### Day 6: Animations & Transitions

**Goal:** Smooth, polished animations

**Tasks:**

1. **Add Smooth Panel Transitions**
   - Panel show/hide animations
   - Panel swap animations
   - Use VSQ.Animation.Duration.* tokens
   - Ensure animations don't block UI

2. **Add Loading Animations**
   - Spinner animations
   - Progress bar animations
   - Skeleton screen animations
   - Smooth, non-distracting animations

3. **Add Hover Effects (Where Appropriate)**
   - Button hover effects
   - List item hover effects
   - Interactive element hover effects
   - Subtle, professional effects

4. **Add Focus Animations**
   - Focus ring animations
   - Focus transition animations
   - Smooth focus changes
   - Visible but not distracting

5. **Add Smooth State Transitions**
   - Button state transitions (normal, hover, pressed, disabled)
   - Panel state transitions (collapsed, expanded)
   - Control state transitions
   - Use VSQ.Animation.* tokens

6. **Ensure Animations Don't Impact Performance**
   - Test animations don't cause frame drops
   - Use GPU-accelerated animations
   - Disable animations on low-end devices (optional)
   - Optimize animation performance

**Deliverable:** Smooth animations throughout application

**Key Files to Modify:**
- `src/VoiceStudio.App/Resources/DesignTokens.xaml` (Animation tokens)
- All panel XAML (add transitions)
- `src/VoiceStudio.App/Controls/PanelHost.xaml` (Panel transitions)

---

### Day 7: Error Message Display & Empty States

**Goal:** Polished error handling and empty states

**Tasks:**

1. **Polish Error Message Display**
   - Consistent error message styling
   - Use error colors from DesignTokens
   - Show error icons
   - Make error messages actionable
   - Position error messages consistently

2. **Add Empty States to All Panels**
   - ProfilesView: "No profiles yet" message
   - TimelineView: "No tracks yet" message
   - MacroView: "No macros yet" message
   - AnalyzerView: "No audio loaded" message
   - Add helpful hints for each empty state

3. **Add Onboarding Hints for First-Time Users**
   - Detect first-time use
   - Show helpful hints/tooltips
   - Guide users through key features
   - Dismissible hints

4. **Improve Drag-and-Drop Feedback**
   - Visual feedback during drag
   - Drop zone highlighting
   - Clear drop indicators
   - Smooth drag animations

5. **Add Visual Feedback for All Interactions**
   - Button press feedback
   - List item selection feedback
   - Control interaction feedback
   - Consistent feedback patterns

6. **Final UI Consistency Pass**
   - Review all panels one more time
   - Ensure everything is consistent
   - Fix any remaining inconsistencies
   - Verify design tokens used everywhere

**Deliverable:** Polished UI with consistent error handling and empty states

**Key Files to Modify:**
- All panel XAML (empty states, error messages)
- `src/VoiceStudio.App/Controls/EmptyStateControl.xaml` (Create if needed)
- `src/VoiceStudio.App/Controls/ErrorMessageControl.xaml` (Create if needed)

---

## 🛠️ Tools & Resources

### Design System:
- `src/VoiceStudio.App/Resources/DesignTokens.xaml` - All design tokens
- **`docs/design/MEMORY_BANK.md`** - **CRITICAL** - Read this daily! Contains UI guardrails (no simplification, PanelHost mandatory, etc.)
- **`docs/governance/`** - All governance docs (roadmaps, status, tracking)
- `docs/governance/OVERSEER_3_WORKER_OPTIMIZED_PLAN.md` - Overall plan
- `docs/governance/TASK_TRACKER_3_WORKERS.md` - **UPDATE DAILY** - Your progress tracking file

### Testing Tools:
- **Windows Narrator** - Screen reader testing
- **High Contrast Mode** - Accessibility testing
- **Keyboard Navigation** - Manual testing

### Code References:
- `src/VoiceStudio.App/Helpers/AutomationHelper.cs` - Automation helper
- `src/VoiceStudio.App/Controls/CommandPalette.xaml` - Command palette reference
- Existing panel implementations for patterns

---

## ⚠️ Critical Rules

1. **100% COMPLETE - NO STUBS OR PLACEHOLDERS**
   - ❌ **NEVER** create TODO comments or placeholder code
   - ❌ **NEVER** leave controls with "Placeholder" text or empty implementations
   - ❌ **NEVER** create bookmark stubs or "coming soon" UI elements
   - ❌ **NEVER** leave loading states as "// TODO: Add loading animation"
   - ✅ **ALWAYS** complete each task 100% before moving to the next
   - ✅ **ALWAYS** implement full functionality, not partial implementations
   - ✅ **ALWAYS** test your implementation before marking complete
   - **Rule:** If it's not 100% complete and tested, it's not done. Don't move on.

2. **ALWAYS use DesignTokens.xaml** - Never hardcode colors, sizes, or spacing
3. **Maintain MVVM separation** - Don't merge View/ViewModel files
4. **Keep PanelHost structure** - Never replace PanelHost with raw Grids
5. **Professional DAW-grade complexity** - Don't simplify the UI
6. **Test with Narrator** - Ensure screen reader compatibility
7. **Test keyboard navigation** - All functionality must be keyboard accessible

---

## 📊 Success Metrics

### UI Consistency:
- ✅ 100% of panels use VSQ.* design tokens
- ✅ Zero hardcoded colors/values
- ✅ Consistent spacing and typography
- ✅ Consistent button and panel styles

### User Experience:
- ✅ All async operations show loading states
- ✅ All interactive elements have tooltips
- ✅ Full keyboard navigation works
- ✅ Screen reader compatible (tested with Narrator)

### Polish:
- ✅ Smooth animations and transitions
- ✅ User-friendly error messages
- ✅ Helpful empty states
- ✅ Professional, polished appearance

---

## 🔄 Coordination with Other Workers

### With Worker 1 (Performance):
- Coordinate on loading states (Worker 1 may add async operations)
- Share error message styling patterns
- Ensure UI polish doesn't impact performance

### With Worker 3 (Documentation):
- Provide UI screenshots for documentation
- Document keyboard shortcuts
- Document accessibility features

---

## 📝 Daily Checklist

**End of Each Day:**
- [ ] **Read Memory Bank** - Check `docs/design/MEMORY_BANK.md` for architecture rules (especially UI guardrails)
- [ ] **Commit all changes** - Use descriptive commit messages (e.g., "Worker 2: Add loading states to ProfilesView")
- [ ] **Update Task Tracker** - Update `docs/governance/TASK_TRACKER_3_WORKERS.md` with your daily progress
- [ ] **Update Status File** - Create/update `docs/governance/WORKER_2_STATUS.md` with detailed progress
- [ ] **Test changes** - Verify changes don't break existing functionality
- [ ] **Verify design tokens** - Ensure no hardcoded colors/values (use VSQ.* tokens only)
- [ ] **Test keyboard navigation** - Verify keyboard navigation still works
- [ ] **Share progress** - Update overseer with completion status

### Task Tracker Update Format:
```markdown
### Day [N] ([Date])
**Worker 2:**
- Task: [Task name]
- Status: 🚧 In Progress / ✅ Complete / ⏸️ Blocked
- Progress: [X]%
- Notes: [What was accomplished, panels reviewed, any issues]
```

### Status File Location:
- **Task Tracker:** `docs/governance/TASK_TRACKER_3_WORKERS.md`
- **Worker Status:** `docs/governance/WORKER_2_STATUS.md` (create if doesn't exist)
- **Memory Bank:** `docs/design/MEMORY_BANK.md` (read daily - CRITICAL for UI rules)

---

## 🚨 If You Get Stuck

1. **Check Memory Bank FIRST** - `docs/design/MEMORY_BANK.md` for UI guardrails (CRITICAL - read daily!)
2. **Check 100% Complete Rule** - `docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md` - NO stubs or placeholders!
3. **Check Task Tracker** - `docs/governance/TASK_TRACKER_3_WORKERS.md` - See what others are doing
4. **Review DesignTokens** - See available tokens in DesignTokens.xaml
5. **Look at Existing Panels** - Use as reference for patterns
6. **Ask Overseer** - Don't spend more than 2 hours stuck
7. **Document Issues** - Add blockers to task tracker and create issue notes
8. **Update Status** - Always update your status file when blocked

**Remember:** Even if stuck, don't create stubs. Complete what you can, document what you can't.

---

## 🎨 Design Token Reference

**Common Tokens to Use:**
- `VSQ.Text.PrimaryBrush` - Primary text color
- `VSQ.Text.SecondaryBrush` - Secondary text color
- `VSQ.Accent.CyanBrush` - Accent color
- `VSQ.Panel.BackgroundBrush` - Panel background
- `VSQ.Panel.BorderBrush` - Panel border
- `VSQ.FontSize.Body` - Body text size
- `VSQ.FontSize.Title` - Title text size
- `VSQ.Spacing.Small` - Small spacing
- `VSQ.Spacing.Medium` - Medium spacing
- `VSQ.Animation.Duration.Fast` - Fast animation
- `VSQ.Animation.Duration.Medium` - Medium animation

**Never hardcode these values!**

---

---

**Status:** 🟢 Ready to Begin Phase 7  
**Start Date:** [To be set by Overseer]  
**Target Completion:** 12-15 days (Phase 7 engines)

**Remember:** Your work makes the application feel polished and professional. Attention to detail and consistency are key. Test as you go, especially keyboard navigation and screen reader compatibility!

