# Cursor Operational Ruleset for VoiceStudio Project
## Complete Guidelines and Standards

**Version:** 2.1  
**Last Updated:** 2025  
**Purpose:** Definitive operational rules and guidelines for Cursor AI when working on VoiceStudio  
**Includes:** Legacy directory integration and migration guidelines

---

## 📍 Project Roots & Scope

### Active Project Root (Authoritative)
- **`E:\VoiceStudio`** - **ONLY** place where new code and edits are made
- This is the **authoritative, active project directory**
- All modifications, creations, and updates happen here
- This is the **primary working directory**

### Archive / Reference Only (Read-Only)
- **`C:\VoiceStudio`** - Read-only reference (if present)
- **`C:\OldVoiceStudio`** - Read-only reference (if present)
- These directories are **archive/reference only**

### Cursor MUST:

1. **Treat `E:\VoiceStudio` as the ONLY place for changes:**
   - All new code goes here
   - All edits happen here
   - All file creation happens here
   - This is the authoritative source

2. **Treat `C:\VoiceStudio` and `C:\OldVoiceStudio` as read-only reference:**
   - ✅ **MAY** open and read files there
   - ✅ **MAY** reference code/patterns from there
   - ✅ **MAY** use as inspiration or reference
   - ❌ **MAY NOT** modify or create files there
   - ❌ **MAY NOT** bulk copy directories from there into `E:\VoiceStudio`
   - ❌ **MAY NOT** write to these directories

3. **Smart Reference Usage:**
   - When referencing legacy code:
     - Read and understand the pattern
     - Recreate/adapt in `E:\VoiceStudio` (not copy)
     - Ensure compatibility with new architecture
     - Update to match current standards

4. **Migration Approach:**
   - If importing from reference directories:
     - Read the file/pattern
     - Create new version in `E:\VoiceStudio`
     - Update to match current architecture
     - Verify compatibility
     - Do not bulk copy

---

## 🎯 General Principles

### Precision & Professionalism
- **Maintain a high standard of quality** in every deliverable
- All outputs should be **meticulously aligned** with the project's premium-grade vision
- Ensure an **advanced, feature-rich, and information-dense UI**
- No shortcuts or simplifications that compromise quality

### Iterative Process
- Break tasks into manageable **"blocks"** (typically 50 blocks per cycle)
- Each block should be:
  - **Self-contained**
  - **Clearly defined**
  - **Executable by Cursor without ambiguity**
- Provide feedback after each block for the next iteration

### Compatibility First
- Always ensure code, components, or configurations comply with **"UltraClone Governance"** standards
- Verify **pinned dependencies and architecture** before making changes
- If unsure about a new dependency or update, **perform a compatibility check**
- Reference `TECHNICAL_STACK_SPECIFICATION.md` for version requirements

### Non-Destructive Changes
- Ensure the system is **not broken by any change**
- Each modification should be:
  - **Incremental**
  - **Reversible if needed**
- Test after each change to verify functionality

### Avoid Over-Simplification
- Adhere strictly to the **"Full-Fidelity Mode"** directive
- Keep every UI element, functionality, and interaction **as complex and sophisticated as possible**
- **Do NOT simplify** unless explicitly requested
- Reference `GLOBAL_GUARDRAILS.md` for anti-simplification rules

### Follow the Master Plan
- All tasks, UI components, backend features, and integrations must align with the **VoiceStudio Master Plan**
- Do not deviate from the plan unless explicitly instructed by the overseer
- Reference `PHASE_ROADMAP_COMPLETE.md` for phase structure

### Legacy Directory Integration
- **Active Project (`E:\VoiceStudio`)**: Contains all active code, configurations, and components
- **Reference Directories (`C:\VoiceStudio`, `C:\OldVoiceStudio`)**: Read-only reference, may contain important configurations, models, user data, scripts, or components
- **Smart Integration**: Intelligently reference patterns from read-only directories, then recreate/adapt in active project
- **No Bulk Copying**: Never bulk copy directories from reference to active project
- **No Redundancy**: Check if items already exist in active project before recreating from reference
- **Version Control**: Be cautious with legacy plugins/dependencies; update to match latest standards when recreating

---

## 🎨 VoiceStudio Project Guidelines for Cursor

### User Interface (UI) Design

#### Premium, Complex UI
- Construct the UI using the **Porcelain Light UI framework**
- Incorporate **advanced, modular components**
- Implement **dockable panels** and **layers of information**
- Maintain **dense, professional, studio-grade** interface

#### Panel & Module Design
- Ensure every panel is **fully detailed** with:
  - Tabs
  - Buttons
  - Sliders
  - Meters
  - Timelines
  - Menus
- No placeholder or simplified panels

#### Dark/Sci-Fi Modes
- Incorporate **Dark, Sci-Fi, and Light themes** as selectable options
- Panels should be **responsive to these modes**
- Follow a **consistent aesthetic** across all modes
- Reference `ThemeManager.cs` for theme switching

#### Tab Layouts & Workflows
- Implement the **tabbed navigation model** for General and Advanced modes
- Include screens:
  - Studio
  - Profiles
  - Library
  - Transcribe
  - Effects
  - Settings
  - Logs
- Reference `PanelStack` system for tabbed panels

#### Visual Consistency
- Ensure UI is **consistent in style and functionality** across all panels
- Take inspiration from:
  - **Adobe Photoshop** (dense, professional)
  - **FL Studio** (modular, tabbed)
  - **DaVinci Resolve** (advanced, information-dense)
- Use design tokens from `DesignTokens.xaml`

---

### Directory Structure

#### Active Project (`E:\VoiceStudio`)
- Contains **all active code, configurations, and essential components**
- This is where **all work happens**
- Authoritative source for the project
- All modifications and creations happen here

#### Reference Directories (`C:\VoiceStudio`, `C:\OldVoiceStudio`)
- Preserved as **read-only reference and archive**
- May contain:
  - Configuration files
  - User profiles
  - Model files (voice models, transcription models)
  - Custom scripts
  - UI components
  - Project-specific settings
- **READ-ONLY** - Never modify or create files here
- Use as **reference source** for patterns and inspiration
- **Do NOT bulk copy** from these directories

#### Smart Integration with Reference Directories

**Referencing Configurations & Profiles:**
- Intelligently **read** from `C:\VoiceStudio` or `C:\OldVoiceStudio` for:
  - Configuration file patterns
  - User profile structures
  - Model file locations/structures
- **Recreate** in `E:\VoiceStudio` when:
  - Item is verified to be needed
  - Item is compatible with new architecture
  - Item doesn't already exist in active project

**No Bulk Copying:**
- **Never bulk copy** directories from reference to active project
- **Read and recreate** patterns instead
- Maintain active project structure

**No Redundancy:**
- **Check first** if item already exists in `E:\VoiceStudio`
- Only recreate from reference when absolutely necessary
- Avoid duplicate configurations or files

**Migration of Custom Scripts:**
- If custom scripts from reference are useful:
  - **Read** the script from reference directory
  - **Recreate** in `E:\VoiceStudio` with updates
  - Update to match new architecture
  - Ensure no outdated dependencies are introduced
  - Verify compatibility with new plugin system

**Version Control:**
- Be cautious when referencing:
  - Plugin files
  - Dependency manifests
  - Outdated components
- If outdated or incompatible:
  - **Update to match latest standards** when recreating
  - Do not recreate deprecated versions
  - Verify against `TECHNICAL_STACK_SPECIFICATION.md`

### Backend Structure

#### Module-Based Backend
- Design backend to follow **plugin-based architecture**
- Ensure voice models, effects, and pipelines are **modular**
- Components should be **updatable independently**
- Reference plugin system documentation

#### Version Compatibility
- Always verify and update **pinned versions** before introducing new functionality
- Check compatibility with:
  - Python 3.10.15
  - Torch 2.2.2+cu121
  - Coqui TTS 0.27.2
  - Transformers 4.55.4
- Ensure **smooth integration** across updates
- Maintain **deterministic build**
- Reference `TECHNICAL_STACK_SPECIFICATION.md`
- **Backward Compatibility**: Before importing legacy plugins, check compatibility with fresh installation

---

### Task Flows & User Journeys

#### Advanced & Beginner Modes
- Implement task flows for **both beginner and advanced users**
- **Beginner mode:**
  - Guided through simplified steps
  - Clear instructions
  - Default settings
- **Advanced mode:**
  - Access to all settings
  - Fine-tuning controls
  - Expert features

#### Success Metrics
- Establish **key success metrics** for each task flow
- Ensure user interactions are **intuitive**
- Optimize **performance** for all flows
- Measure completion rates and user satisfaction

---

### Integration with AI/ML Models

#### AI-driven Enhancements
- Ensure AI models are **fully integrated** into backend and accessible via UI:
  - **XTTS v2** - Voice cloning
  - **Faster-Whisper** - Transcription
  - **RVC** - Real-time voice conversion
- Support both **real-time** and **batch processing**
- Reference `ENGINE_RECOMMENDATIONS.md`

#### Advanced Features Integration (Legacy Migration)

**Voice Cloning & Transcription Models:**
- If models exist in `C:\VoiceStudio` or `C:\OldVoiceStudio`:
  - **Read** model metadata and structure from reference directory
  - **Reference** model locations (do not copy unless explicitly needed)
  - If recreating model references in active project:
    - Verify model format compatibility
    - Update paths to point to reference location or recreate in active project
    - Ensure compatibility with new architecture

**AI Enhancements:**
- Any advanced ML pipelines from reference directories:
  - **Read** the pipeline structure
  - **Review** for compatibility
  - **Recreate** in active project if necessary
  - Examples: RL-based tuning, auto-tuning models
  - Ensure compatibility with new architecture

#### Offline-first Approach
- Maintain **offline functionality** for all AI processes
- Ensure **no data is transmitted** without user consent
- All processing should work **without internet connection**
- Cache models locally

---

### UI Elements and Custom Components

#### UI Panel Transfer (Reference Integration)
- If custom UI panels, layouts, or components exist in `C:\VoiceStudio` or `C:\OldVoiceStudio`:
  - **Read** the panel structure from reference directory
  - **Recreate** in `E:\VoiceStudio` if they fit updated modular UI system
  - Review for compatibility before recreating
  - Recreate custom widgets, themes, or density settings if compatible
  - **Do NOT copy** - always recreate with updates

#### Element Remapping
- For any recreated elements that have changed:
  - **Remap or adjust references** to maintain functionality
  - Ensure no errors in active project
  - Update to match new architecture patterns
  - Verify design token compatibility

### Cross-Screen Flows

#### Flow Continuity
- Implement **smooth and coherent transitions** between screens
- Examples:
  - Library → Studio
  - Profiles → Settings
  - Transcribe → Effects
- Users should **quickly access features** without confusion
- Maintain context across navigation

#### Task Flows & User Journeys (Reference Integration)
- In active `E:\VoiceStudio` project:
  - Ensure both beginner and advanced workflows are configured
  - Reference workflows may need revalidation for current architecture
- **Profiles and Configuration Recreation:**
  - If user profiles, audio effects presets, or project-specific settings exist in `C:\VoiceStudio` or `C:\OldVoiceStudio`:
    - **Read** the structure from reference directory
    - **Recreate** carefully in active project
    - Ensure no loss of data integrity
    - Verify compatibility with new architecture
    - **Do NOT copy** - recreate with updates

#### Error States & Guardrails
- Implement **clear error states** and recovery options
- If a feature fails:
  - Display **user-friendly message**
  - Provide **resolution path**
  - Log error for debugging
- Never leave user in broken state
- **Legacy File Errors:**
  - If errors in legacy files (outdated configs, corrupted files, missing dependencies):
    - Report in clear, actionable format
    - Provide recommendations for resolution
    - Do not import broken files

---

### Plugin System

#### Plugin Development
- Follow plugin system with **signed .ucpkg files** for each component
- Ensure **compatibility** with main architecture
- **Isolate plugins** in subprocesses
- Ensure **seamless loading/unloading**
- Reference plugin API documentation

#### Plugin Management (Legacy Integration)

**Backward Compatibility:**
- Before referencing any legacy plugins or effects from `C:\VoiceStudio` or `C:\OldVoiceStudio`:
  - Read and understand the plugin structure
  - Check for compatibility with active project
  - Ensure no deprecated plugins are recreated
  - Verify against current plugin API
  - Recreate in `E:\VoiceStudio` with updates

**Plugin Verification:**
- Use plugin verification system to confirm:
  - Pulled plugins are still valid
  - Plugins haven't been corrupted
  - Plugins aren't redundant with newer versions
- Reject incompatible or outdated plugins

**Version Updates:**
- If legacy plugin is outdated:
  - Update to match latest standards
  - Do not import deprecated versions
  - Maintain compatibility with new architecture

#### CLI Integration
- Ensure CLI commands are **fully functional**:
  - `list_voices()`
  - `synthesize()`
  - Other commands as specified
- Integrate **smoothly with UI components**
- Maintain consistency between CLI and UI

---

### Diagnostics & Debugging

#### Comprehensive Logging
- All actions must be **logged in a structured manner**:
  - Error messages
  - Performance metrics
  - User actions
  - System events
- Logs should be **easily accessible** from Logs tab
- Support filtering and search

#### Migration Logs
- Keep **detailed log** of any reference or recreation activity involving `C:\VoiceStudio` or `C:\OldVoiceStudio`:
  - Which files were referenced
  - What patterns were recreated in `E:\VoiceStudio`
  - What configurations were updated
  - Changes made during recreation
  - Compatibility checks performed
  - Errors encountered and resolved

#### Health Monitoring
- Implement **real-time monitoring**:
  - GPU usage
  - CPU usage
  - RAM usage
- Ensure application runs **smoothly without bottlenecks**
- Display metrics in Diagnostics panel
- Alert on resource exhaustion
- **After Reference Recreation:**
  - Monitor for resource bottlenecks introduced by recreated components
  - Verify GPU, CPU, and RAM usage remain optimal
  - Run compatibility verification for potential conflicts

---

### Upgrades & Backward Compatibility

#### Semantic Versioning
- Follow **SemVer strictly** for every update
- Ensure **no breaking changes** without adequate versioning
- Provide **backward compatibility** to prevent regressions
- Document all version changes

#### Snapshot/Backup System
- Before any major upgrade, take **automatic snapshots** of system state
- Enable **quick rollback** in case of issues
- Store snapshots in user-accessible location
- Include project data, settings, and configurations

#### Preserve Existing Data (Reference Recreation)
- Before making any changes to system:
  - Ensure user data, models, and settings from reference directories are **safely referenced**
  - **Recreate** in active project (`E:\VoiceStudio`) when needed
  - **Back up** active project state before major changes
  - Verify data integrity after recreation

#### Snapshot Before Reference Recreation
- Automatically take **snapshot of active project's state** before any major recreation from reference
- Enable **rollback** if recreation causes issues
- Store snapshot with timestamp and recreation log reference

---

## 📋 Task Specifics for Cursor

### Block Generator
- Break down tasks into **50-block cycles**
- Each block should be:
  - **Testable**
  - **Incremental**
  - **Self-contained**
- After completing a block, **provide feedback** for next iteration
- Track progress in implementation status

### Execution Focus
- Stay focused on the **VoiceStudio Master Plan**
- Do not skip or ignore any detailed steps
- Only deviate if **explicitly stated in directives**
- Reference phase roadmap for current phase

### Guardrails Enforcement
- Before executing any change, verify if it violates:
  - Project's **architecture**
  - **Governance rules**
  - **Version compatibility**
  - **Module usage**
- Check against:
  - `GLOBAL_GUARDRAILS.md`
  - `TECHNICAL_STACK_SPECIFICATION.md`
  - `MEMORY_BANK.md`

---

## 🎨 UI/UX Enhancements

#### Advanced UI
- Implement **advanced, information-dense panels** for:
  - Transcription
  - Effects chains
  - Voice synthesis
  - Profile management
- No simplified or placeholder panels
- Reference `PANEL_IMPLEMENTATION_GUIDE.md`

#### Advanced UI Features (Reference Integration)
- **Read** advanced UI panels from reference directories if they fit new design:
  - Transcription editor
  - Effects chain
  - Timeline views
- **Recreate** in `E:\VoiceStudio` with updates
- Ensure modular UI is maintained
- Features must work seamlessly:
  - Tab layouts
  - Drag-and-drop panels
  - Split views

#### Tab Functionality
- Ensure tab functionality is preserved and works with:
  - Studio
  - Profiles
  - Library
  - Transcribe
  - Effects
  - Settings
  - Logs
- Verify tab functionality after UI recreation

#### Visual Feedback
- Ensure **real-time visual feedback**:
  - Spectrogram updates
  - Waveform visualizations
  - Progress indicators
  - Status updates
- For voice synthesis, voice cloning, and transcription tasks
- Use WebSocket for real-time updates

#### Task-Oriented Design
- Keep user flows **task-oriented**
- Minimize **unnecessary clicks or navigation**
- Still expose **all advanced controls** for power users
- Balance simplicity with power

---

## 🚨 Critical Rules (Non-Negotiable)

### Preservation Rules
1. **NEVER delete existing files** without explicit instruction
2. **NEVER remove existing functionality**
3. **NEVER remove existing data bindings**
4. **NEVER remove existing event handlers**
5. **NEVER replace existing code unnecessarily**

### Architecture Rules
1. **PanelHost is MANDATORY** - Never replace with raw Grids
2. **MVVM separation** - No logic in code-behind
3. **Design tokens** - No hardcoded colors/sizes
4. **PanelRegistry** - All panels must be registered
5. **IPanelView** - All ViewModels must implement interface

### Simplification Rules
1. **Do NOT collapse panels** or merge layouts
2. **Do NOT merge Views and ViewModels**
3. **Do NOT replace PanelHost** with raw Grids
4. **Do NOT remove placeholder areas** (they're future controls)
5. **Do NOT simplify UI** for "speed" or "convenience"

---

## 📚 Reference Documents

### Must Read Before Starting
1. **MEMORY_BANK.md** - Critical information
2. **GLOBAL_GUARDRAILS.md** - Anti-simplification rules
3. **TECHNICAL_STACK_SPECIFICATION.md** - Version requirements
4. **CURSOR_MASTER_INSTRUCTIONS.md** - Integration guide

### Implementation Guides
1. **PANEL_IMPLEMENTATION_GUIDE.md** - Panel development
2. **SKELETON_INTEGRATION_GUIDE.md** - Integration process
3. **PHASE_ROADMAP_COMPLETE.md** - Phase structure

### Architecture
1. **VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md** - Master spec
2. **../architecture/Part6_State_Data.md** - Data flow
3. **ENGINE_RECOMMENDATIONS.md** - Backend engines

---

## ✅ Pre-Execution Checklist

Before executing any task, verify:

- [ ] Read relevant documentation
- [ ] Check version compatibility
- [ ] Verify no guardrail violations
- [ ] Ensure non-destructive approach
- [ ] Plan incremental changes
- [ ] Prepare rollback strategy
- [ ] Check against master plan
- [ ] Verify theme/density compatibility
- [ ] Ensure MVVM compliance
- [ ] Check design token usage

### Reference Directory Integration Checklist

Before referencing from `C:\VoiceStudio` or `C:\OldVoiceStudio`:

- [ ] Verify working in active project (`E:\VoiceStudio`)
- [ ] Check if item already exists in `E:\VoiceStudio`
- [ ] Read and understand pattern from reference directory
- [ ] Verify compatibility with new architecture
- [ ] Check version compatibility
- [ ] Verify no deprecated dependencies
- [ ] Take snapshot of active project state
- [ ] Plan recreation path (not copy)
- [ ] Prepare rollback strategy
- [ ] Recreate in `E:\VoiceStudio` with updates
- [ ] Document recreation in log
- [ ] Verify data integrity after recreation
- [ ] Monitor resource usage after recreation
- [ ] Run compatibility verification
- [ ] **Never modify or create files in reference directories**

---

## 🔄 Workflow Process

### 1. Task Receipt
- Read task carefully
- Identify relevant documentation
- Check against guardrails
- Plan execution approach

### 2. Execution
- Break into 50-block cycles
- Execute incrementally
- Test after each block
- Verify non-destructive
- Check compatibility
- **If referencing from read-only directories:**
  - Verify working in `E:\VoiceStudio` (active project)
  - Check item doesn't already exist in active project
  - Read pattern from reference directory
  - Verify compatibility first
  - Take snapshot before recreation
  - Recreate incrementally in active project
  - Test after each recreation
  - Log all recreation activities
  - **Never modify reference directories**

### 3. Verification
- Test functionality
- Verify UI consistency
- Check performance
- Validate against spec
- Document changes
- **If reference recreation:**
  - Verify data integrity
  - Check resource usage
  - Run compatibility verification
  - Test all recreated features
  - Verify no conflicts
  - Confirm all work is in `E:\VoiceStudio`

### 4. Feedback
- Report completion
- Note any issues
- Suggest next steps
- Update documentation if needed

---

## 💡 Key Reminders

1. **Quality over speed** - Premium-grade output always
2. **Complexity is required** - Do not simplify
3. **Compatibility first** - Check versions always
4. **Non-destructive** - Incremental, reversible changes
5. **Follow the plan** - Master plan is the guide
6. **Preserve existing** - Never break what works
7. **Document everything** - Clear, structured logs
8. **Test thoroughly** - Verify after each change

---

## 🎯 Success Criteria

A task is successful when:

- ✅ All functionality works as specified
- ✅ UI is complex and information-dense
- ✅ No existing functionality broken
- ✅ Version compatibility maintained
- ✅ Performance within budget
- ✅ Code follows MVVM pattern
- ✅ Design tokens used correctly
- ✅ Documentation updated
- ✅ Tests pass
- ✅ User experience is smooth

---

**This ruleset is the definitive guide for all Cursor operations on VoiceStudio. Always refer to this document when making decisions or executing tasks.**

