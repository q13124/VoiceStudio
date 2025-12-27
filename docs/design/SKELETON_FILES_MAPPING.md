# Skeleton Files Mapping
## Complete File-by-File Integration Reference

**Purpose:** Quick reference for mapping skeleton files to existing codebase structure

---

## 📁 CORE INFRASTRUCTURE

### PanelRegistry.cs
- **Skeleton:** `core/PanelRegistry.cs`
- **Existing:** `src/VoiceStudio.Core/Panels/PanelRegistry.cs`
- **Action:** MERGE
- **Changes:**
  - Add `PanelTier` enum
  - Extend `PanelDescriptor` with: `Category`, `Tier`, `IconKey`, `IsPlugin`
  - Add `CreateDefault()` method
  - Register 9 advanced panels
  - **PRESERVE** existing 6 core panel registrations

### IBackendClient.cs
- **Skeleton:** `core/IBackendClient.cs`
- **Existing:** `src/VoiceStudio.Core/Services/IBackendClient.cs`
- **Action:** EXTEND
- **Changes:**
  - Add new methods: `TrainStartAsync`, `TtsSynthesizeAsync`, `SpectrogramGenerateAsync`, `LexiconListAsync`, `LexiconUpsertAsync`, `VoiceEmbeddingsAsync`, `MixAnalyzeAsync`, `StyleExtractAsync`, `VoiceBlendPreviewAsync`
  - Add new events: `TrainProgress`, `SpectrogramUpdated`, `LogReceived`, `MixSuggestionReady`
  - **PRESERVE** all existing methods and events

### ThemeManager.cs
- **Skeleton:** `core/ThemeManager.cs`
- **Target:** `src/VoiceStudio.App/Services/ThemeManager.cs`
- **Action:** CREATE NEW
- **Namespace:** `VoiceStudio.App.Services`
- **Enhancements:** Add runtime theme switching (see PANEL_IMPLEMENTATION_GUIDE.md)

### PanelTemplateSelector.cs
- **Skeleton:** `core/PanelTemplateSelector.cs`
- **Target:** `src/VoiceStudio.App/Controls/PanelTemplateSelector.cs`
- **Action:** CREATE NEW
- **Namespace:** `VoiceStudio.App.Controls`
- **Usage:** Wire in App.xaml or MainWindow.xaml resources

---

## 📱 VIEWMODELS (9 Advanced Panels)

All ViewModels follow this pattern:
- **Skeleton Location:** `ui/ViewModels/Panels/{PanelName}PanelViewModel.cs`
- **Target Location:** `src/VoiceStudio.App/ViewModels/Panels/{PanelName}PanelViewModel.cs`
- **Action:** CREATE NEW
- **Namespace:** `VoiceStudio.App.ViewModels.Panels`
- **Requirements:**
  - Implement `IPanelView` interface
  - Use `ObservableObject` from CommunityToolkit.Mvvm
  - Inject `IBackendClient` via constructor
  - Use `[ObservableProperty]` for properties
  - Use `RelayCommand` for commands

### Files:
1. `TextSpeechEditorPanelViewModel.cs`
2. `ProsodyPanelViewModel.cs`
3. `SpatialStagePanelViewModel.cs`
4. `MixAssistantPanelViewModel.cs`
5. `StyleTransferPanelViewModel.cs`
6. `EmbeddingExplorerPanelViewModel.cs`
7. `AssistantPanelViewModel.cs`
8. `LexiconPanelViewModel.cs`
9. `VoiceMorphPanelViewModel.cs`

---

## 🎨 VIEWS (9 Advanced Panels)

All Views follow this pattern:
- **Skeleton Location:** `ui/Views/Panels/{PanelName}View.xaml` + `.xaml.cs`
- **Target Location:** `src/VoiceStudio.App/Views/Panels/{PanelName}View.xaml` + `.xaml.cs`
- **Action:** CREATE NEW
- **Namespace:** `VoiceStudio.App.Views.Panels`
- **Requirements:**
  - Use `UserControl` as root
  - Use design tokens (VSQ.*) - no hardcoded values
  - Code-behind only contains `InitializeComponent()` and `DataContext` assignment
  - No logic in code-behind

### Files:
1. `TextSpeechEditorView.xaml` + `.xaml.cs`
2. `ProsodyView.xaml` + `.xaml.cs`
3. `SpatialStageView.xaml` + `.xaml.cs`
4. `MixAssistantView.xaml` + `.xaml.cs`
5. `StyleTransferView.xaml` + `.xaml.cs`
6. `EmbeddingExplorerView.xaml` + `.xaml.cs`
7. `AssistantView.xaml` + `.xaml.cs`
8. `LexiconView.xaml` + `.xaml.cs`
9. `VoiceMorphView.xaml` + `.xaml.cs`

---

## 🔧 SERVICES

### CommandPaletteService.cs
- **Skeleton:** `services/CommandPaletteService.cs`
- **Existing:** May exist as `CommandRegistry.cs`
- **Action:** MERGE or CREATE
- **Target:** `src/VoiceStudio.App/Services/CommandPaletteService.cs`
- **Integration:** Wire to existing `CommandPalette` control

### PluginService.cs
- **Skeleton:** `services/PluginService.cs`
- **Existing:** May exist as `PluginManager.cs`
- **Action:** MERGE or CREATE
- **Target:** `src/VoiceStudio.App/Services/PluginService.cs`
- **Integration:** Merge with existing plugin system

### DiagnosticsService.cs
- **Skeleton:** `services/DiagnosticsService.cs`
- **Target:** `src/VoiceStudio.App/Services/DiagnosticsService.cs`
- **Action:** CREATE NEW
- **Integration:** Wire to existing `DiagnosticsView`

---

## 🐍 BACKEND (Python FastAPI)

### Directory Structure
Create if not exists:
```
backend/
  api/
    __init__.py
    main.py
    models.py
    routes/
      __init__.py
      asr.py
      edit.py
      tts.py
      analyze.py
      lexicon.py
      embedding.py
      mix.py
      style.py
      voice.py
    ws/
      __init__.py
      events.py
    requirements.txt
```

### Files to Create:

1. **main.py**
   - **Skeleton:** `backend/app/main.py`
   - **Target:** `backend/api/main.py`
   - **Action:** CREATE NEW
   - **Changes:** Update imports to match new structure

2. **models.py**
   - **Skeleton:** `backend/app/models.py`
   - **Target:** `backend/api/models.py`
   - **Action:** CREATE NEW
   - **Contains:** Pydantic models for all API requests/responses

3. **routes/asr.py**
   - **Skeleton:** `backend/app/routes/asr.py`
   - **Target:** `backend/api/routes/asr.py`
   - **Action:** CREATE NEW
   - **Endpoints:** `/api/asr/align`

4. **routes/edit.py**
   - **Skeleton:** `backend/app/routes/edit.py`
   - **Target:** `backend/api/routes/edit.py`
   - **Action:** CREATE NEW
   - **Endpoints:** `/api/edit/fillers`, `/api/edit/insert`

5. **routes/tts.py**
   - **Skeleton:** `backend/app/routes/tts.py`
   - **Target:** `backend/api/routes/tts.py`
   - **Action:** CREATE NEW
   - **Endpoints:** `/api/tts/synthesize`, `/api/tts/synthesize/prosody`, `/api/tts/synthesize/style`

6. **routes/analyze.py**
   - **Skeleton:** `backend/app/routes/analyze.py`
   - **Target:** `backend/api/routes/analyze.py`
   - **Action:** CREATE NEW
   - **Endpoints:** `/api/analyze/spectrogram`

7. **routes/lexicon.py**
   - **Skeleton:** `backend/app/routes/lexicon.py`
   - **Target:** `backend/api/routes/lexicon.py`
   - **Action:** CREATE NEW
   - **Endpoints:** `/api/lexicon/list`, `/api/lexicon/upsert`

8. **routes/embedding.py**
   - **Skeleton:** `backend/app/routes/embedding.py`
   - **Target:** `backend/api/routes/embedding.py`
   - **Action:** CREATE NEW
   - **Endpoints:** `/api/embedding/voices`, `/api/embedding/project`

9. **routes/mix.py**
   - **Skeleton:** `backend/app/routes/mix.py`
   - **Target:** `backend/api/routes/mix.py`
   - **Action:** CREATE NEW
   - **Endpoints:** `/api/mix/analyze`, `/api/mix/apply`

10. **routes/style.py**
    - **Skeleton:** `backend/app/routes/style.py`
    - **Target:** `backend/api/routes/style.py`
    - **Action:** CREATE NEW
    - **Endpoints:** `/api/style/extract`

11. **routes/voice.py**
    - **Skeleton:** `backend/app/routes/voice.py`
    - **Target:** `backend/api/routes/voice.py`
    - **Action:** CREATE NEW
    - **Endpoints:** `/api/voice/blend/preview`, `/api/voice/blend/save`, `/api/voice/morph/render`

12. **ws/events.py**
    - **Skeleton:** `backend/app/ws/events.py`
    - **Target:** `backend/api/ws/events.py`
    - **Action:** CREATE NEW
    - **WebSocket:** `/ws/events` endpoint

13. **requirements.txt**
    - **Skeleton:** `backend/requirements.txt`
    - **Target:** `backend/api/requirements.txt`
    - **Action:** CREATE NEW
    - **Contains:** FastAPI and dependencies

---

## 📝 TESTS

### Test Documentation
- **Skeleton:** `tests/*.md`
- **Target:** `tests/*.md` or `docs/tests/*.md`
- **Action:** CREATE NEW

**Files:**
1. `perf_budgets.md` - Performance budgets
2. `ui_bindings.md` - UI binding checks
3. `abx_protocol.md` - ABX testing protocol

---

## 🎨 RESOURCES

### DesignTokens.xaml
- **Skeleton:** `ui/Resources/DesignTokens.xaml`
- **Existing:** `src/VoiceStudio.App/Resources/DesignTokens.xaml`
- **Action:** MERGE
- **Changes:**
  - Add new brushes: `VSQ.Panel`, `VSQ.AccentAlt`, `VSQ.SubtleText`
  - Add icon keys: `Icon.EditText`, `Icon.Prosody`, etc.
  - **PRESERVE** all existing tokens

---

## 📋 QUICK INTEGRATION CHECKLIST

### Phase 1: Core Infrastructure
- [ ] Merge PanelRegistry (add PanelTier, extend PanelDescriptor, register 9 panels)
- [ ] Extend IBackendClient (add new methods and events)
- [ ] Create ThemeManager
- [ ] Create PanelTemplateSelector
- [ ] Merge DesignTokens (add new tokens and icon keys)

### Phase 2: Advanced Panels
- [ ] Create 9 ViewModels (with IPanelView implementation)
- [ ] Create 9 Views (XAML + code-behind)
- [ ] Update namespaces to match existing structure
- [ ] Wire IBackendClient dependency injection
- [ ] Register all panels in PanelRegistry

### Phase 3: Services
- [ ] Create/merge CommandPaletteService
- [ ] Create/merge PluginService
- [ ] Create DiagnosticsService
- [ ] Integrate with existing controls

### Phase 4: Backend
- [ ] Create backend directory structure
- [ ] Create all route files
- [ ] Create models.py
- [ ] Create main.py
- [ ] Create WebSocket events.py
- [ ] Create requirements.txt

### Phase 5: MainWindow Integration
- [ ] Enhance MainWindow to support PanelStack
- [ ] Create/enhance MainWindowViewModel
- [ ] Wire Command Palette (Ctrl+P)
- [ ] Wire PanelTemplateSelector

### Phase 6: Tests
- [ ] Add test documentation
- [ ] Document performance budgets
- [ ] Document UI binding checks
- [ ] Document ABX protocol

### Phase 7: Verification
- [ ] Solution compiles
- [ ] All existing functionality preserved
- [ ] All new panels accessible
- [ ] Backend routes return placeholder data
- [ ] Design tokens resolve
- [ ] Command Palette works

---

## 🔗 REFERENCE

- `SKELETON_INTEGRATION_GUIDE.md` - Detailed integration guide
- `PANEL_IMPLEMENTATION_GUIDE.md` - Panel implementation patterns
- `INNOVATIVE_ADVANCED_PANELS_CATALOG.md` - Advanced panels catalog

