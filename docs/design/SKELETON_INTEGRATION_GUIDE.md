# VoiceStudio Quantum Skeleton Integration Guide
## Merging Skeleton Implementation with Existing Codebase

**Version:** 1.0  
**Based on:** VoiceStudio-Quantum-Skeleton.zip  
**Purpose:** Step-by-step guide to integrate skeleton code with existing VoiceStudio codebase

---

## 🎯 INTEGRATION OVERVIEW

The skeleton contains:
- **9 Advanced Panel ViewModels** (ready to integrate)
- **9 Advanced Panel Views** (XAML skeletons)
- **Backend FastAPI routes** (Python)
- **Core infrastructure** (PanelRegistry, IBackendClient, ThemeManager)
- **Services** (CommandPaletteService, PluginService, DiagnosticsService)
- **Tests** (performance budgets, UI bindings, ABX protocol)

**Integration Strategy:** Merge skeleton code into existing structure while preserving all existing functionality.

---

## 📁 STRUCTURE MAPPING

### Skeleton Structure → Existing Structure

| Skeleton Location | Existing Location | Action |
|-------------------|-------------------|--------|
| `core/PanelRegistry.cs` | `src/VoiceStudio.Core/Panels/PanelRegistry.cs` | **MERGE** - Add skeleton enhancements to existing |
| `core/IBackendClient.cs` | `src/VoiceStudio.Core/Services/IBackendClient.cs` | **MERGE** - Extend existing interface |
| `core/ThemeManager.cs` | `src/VoiceStudio.App/Services/ThemeManager.cs` | **ADD** - New file (create if doesn't exist) |
| `core/PanelTemplateSelector.cs` | `src/VoiceStudio.App/Controls/PanelTemplateSelector.cs` | **ADD** - New file |
| `ui/ViewModels/Panels/*.cs` | `src/VoiceStudio.App/ViewModels/Panels/*.cs` | **ADD** - 9 new ViewModels |
| `ui/Views/Panels/*.xaml` | `src/VoiceStudio.App/Views/Panels/*.xaml` | **ADD** - 9 new Views |
| `services/CommandPaletteService.cs` | `src/VoiceStudio.App/Services/CommandPaletteService.cs` | **MERGE** - Enhance existing |
| `services/PluginService.cs` | `src/VoiceStudio.App/Services/PluginService.cs` | **MERGE** - Enhance existing |
| `services/DiagnosticsService.cs` | `src/VoiceStudio.App/Services/DiagnosticsService.cs` | **ADD** - New file |
| `backend/app/*.py` | `backend/api/*.py` | **ADD** - New backend routes |
| `tests/*.md` | `tests/*.md` | **ADD** - New test documentation |

---

## 🔄 STEP-BY-STEP INTEGRATION

### Step 1: Merge PanelRegistry

**Skeleton:** `core/PanelRegistry.cs`  
**Existing:** `src/VoiceStudio.Core/Panels/PanelRegistry.cs`

**Actions:**
1. Read existing `PanelRegistry.cs`
2. Add `PanelTier` enum from skeleton (if not present)
3. Extend `PanelDescriptor` with skeleton properties:
   - `Category` (string)
   - `Tier` (PanelTier)
   - `IconKey` (string)
   - `IsPlugin` (bool)
4. Add `CreateDefault()` method from skeleton
5. Register all 9 advanced panels from skeleton
6. **PRESERVE** existing panel registrations

**Integration Pattern:**
```csharp
// Existing PanelRegistry.cs
public sealed class PanelRegistry : IPanelRegistry
{
    // ... existing code ...
    
    // NEW: Add PanelTier enum (if not present)
    public enum PanelTier { Core, Pro, Advanced, Technical, Meta }
    
    // NEW: Extend PanelDescriptor (preserve existing properties)
    public sealed class PanelDescriptor
    {
        // EXISTING: Preserve these
        public string PanelId { get; init; }
        public string DisplayName { get; init; }
        public PanelRegion Region { get; init; }
        public Type ViewType { get; init; }
        public Type ViewModelType { get; init; }
        
        // NEW: Add from skeleton
        public string Category { get; init; } = string.Empty;
        public PanelTier Tier { get; init; } = PanelTier.Core;
        public string IconKey { get; init; } = string.Empty;
        public bool IsPlugin { get; init; } = false;
    }
    
    // NEW: Add CreateDefault() method
    public static PanelRegistry CreateDefault()
    {
        var r = new PanelRegistry();
        
        // EXISTING: Register existing 6 core panels (preserve)
        r.Register(new PanelDescriptor { 
            PanelId = "Profiles", 
            DisplayName = "Profiles",
            Region = PanelRegion.Left,
            // ... existing properties ...
        });
        // ... other existing panels ...
        
        // NEW: Register 9 advanced panels from skeleton
        r.Register(new PanelDescriptor { 
            PanelId = "TextSpeechEditor",
            DisplayName = "Text-Based Speech Editor",
            Category = "Studio",
            Tier = PanelTier.Pro,
            DefaultRegion = PanelRegion.Center,
            ViewType = typeof(TextSpeechEditorView),
            ViewModelType = typeof(TextSpeechEditorPanelViewModel),
            IconKey = "Icon.EditText"
        });
        // ... other advanced panels ...
        
        return r;
    }
}
```

---

### Step 2: Extend IBackendClient

**Skeleton:** `core/IBackendClient.cs`  
**Existing:** `src/VoiceStudio.Core/Services/IBackendClient.cs`

**Actions:**
1. Read existing `IBackendClient.cs`
2. Add new methods from skeleton (preserve existing)
3. Add new events from skeleton (preserve existing)
4. Update implementation in `BackendClient.cs` to support new methods

**Integration Pattern:**
```csharp
// Existing IBackendClient.cs
public interface IBackendClient
{
    // EXISTING: Preserve all existing methods
    Task<bool> CheckHealthAsync();
    Task<AnalyzeVoiceResult> AnalyzeVoiceAsync(AnalyzeVoiceRequest request);
    // ... existing methods ...
    
    // NEW: Add from skeleton
    Task<bool> TrainStartAsync(TrainRequest req);
    Task<bool> TtsSynthesizeAsync(TtsRequest req);
    Task<bool> SpectrogramGenerateAsync(SpectrogramRequest req);
    Task<object> LexiconListAsync();
    Task<bool> LexiconUpsertAsync(LexiconEntry entry);
    Task<object> VoiceEmbeddingsAsync();
    Task<object> MixAnalyzeAsync(MixAnalyzeRequest req);
    Task<object> StyleExtractAsync(StyleExtractRequest req);
    Task<object> VoiceBlendPreviewAsync(BlendRequest req);
    
    // EXISTING: Preserve all existing events
    event EventHandler<SystemStats> SystemStatsUpdated;
    // ... existing events ...
    
    // NEW: Add from skeleton
    event EventHandler<object> TrainProgress;
    event EventHandler<object> SpectrogramUpdated;
    event EventHandler<object> LogReceived;
    event EventHandler<object> MixSuggestionReady;
}
```

**Note:** Replace `object` types with proper model types as implementation progresses.

---

### Step 3: Add ThemeManager

**Skeleton:** `core/ThemeManager.cs`  
**Target:** `src/VoiceStudio.App/Services/ThemeManager.cs`

**Actions:**
1. Create new file `src/VoiceStudio.App/Services/ThemeManager.cs`
2. Copy skeleton implementation
3. Enhance with runtime theme switching (see `PANEL_IMPLEMENTATION_GUIDE.md` → Theme Switching)
4. Integrate with existing `DesignTokens.xaml`

**Integration Pattern:**
```csharp
// NEW: src/VoiceStudio.App/Services/ThemeManager.cs
using System.IO;
using System.Text.Json;
using Microsoft.UI.Xaml;

namespace VoiceStudio.App.Services
{
    public sealed class ThemeManager
    {
        public string CurrentTheme { get; private set; } = "Dark";
        public string Density { get; private set; } = "Standard";

        public void ApplyTheme(string name)
        {
            CurrentTheme = name;
            // TODO: Update ResourceDictionaries (see PANEL_IMPLEMENTATION_GUIDE.md)
            Persist();
        }

        public void ApplyLayoutDensity(string density)
        {
            Density = density;
            Persist();
        }

        private void Persist()
        {
            var settingsDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "VoiceStudio"
            );
            Directory.CreateDirectory(settingsDir);
            var path = Path.Combine(settingsDir, "settings.json");
            File.WriteAllText(path, JsonSerializer.Serialize(new 
            { 
                theme = CurrentTheme, 
                density = Density 
            }));
        }
    }
}
```

---

### Step 4: Integrate MainWindow Structure

**Skeleton:** `ui/Views/MainWindow.xaml` + `ui/ViewModels/MainWindowViewModel.cs`  
**Existing:** `src/VoiceStudio.App/MainWindow.xaml` + `MainWindow.xaml.cs`

**Important:** The skeleton uses `TabView` directly in regions (PanelStack implementation). The existing code uses `PanelHost` controls. **We need to merge both approaches.**

**Actions:**
1. **PRESERVE** existing MainWindow structure with PanelHost controls
2. **ENHANCE** PanelHost to support PanelStack (TabView) internally
3. **ADD** MainWindowViewModel pattern from skeleton (if not exists)
4. **INTEGRATE** PanelTemplateSelector for dynamic panel loading
5. **WIRE** Command Palette (Ctrl+P) from skeleton

**Integration Pattern:**
```xml
<!-- Existing MainWindow.xaml - ENHANCE, don't replace -->
<Window>
  <Grid>
    <!-- EXISTING: Preserve existing structure -->
    <Grid.RowDefinitions>
      <RowDefinition Height="Auto"/>   <!-- Command Deck -->
      <RowDefinition Height="*"/>       <!-- Main Workspace -->
      <RowDefinition Height="Auto"/>   <!-- Status Bar -->
    </Grid.RowDefinitions>
    
    <!-- EXISTING: Preserve command deck -->
    <Grid Grid.Row="0">
      <!-- Existing menu and toolbar -->
    </Grid>
    
    <!-- EXISTING: Preserve main workspace -->
    <Grid Grid.Row="1">
      <Grid.ColumnDefinitions>
        <ColumnDefinition Width="0.2*"/>   <!-- Left -->
        <ColumnDefinition Width="0.55*"/>   <!-- Center -->
        <ColumnDefinition Width="0.25*"/>  <!-- Right -->
      </Grid.ColumnDefinitions>
      <Grid.RowDefinitions>
        <RowDefinition Height="*"/>
        <RowDefinition Height="0.18*"/>    <!-- Bottom -->
      </Grid.RowDefinitions>
      
      <!-- EXISTING: Preserve PanelHost controls -->
      <!-- ENHANCE: PanelHost now supports PanelStack internally -->
      <controls:PanelHost Grid.Row="0" Grid.Column="0" x:Name="LeftPanelHost">
        <!-- PanelHost internally uses PanelStack (TabView) if multiple panels -->
      </controls:PanelHost>
      
      <!-- Similar for Center, Right, Bottom -->
    </Grid>
    
    <!-- EXISTING: Preserve status bar -->
    <Border Grid.Row="2">
      <!-- Existing status bar -->
    </Border>
  </Grid>
</Window>
```

**MainWindowViewModel Integration:**
```csharp
// ENHANCE existing MainWindow.xaml.cs or create MainWindowViewModel
public sealed partial class MainWindowViewModel : ObservableObject
{
    public ObservableCollection<PanelTab> PanelTabsLeft { get; } = new();
    public ObservableCollection<PanelTab> PanelTabsCenter { get; } = new();
    public ObservableCollection<PanelTab> PanelTabsRight { get; } = new();
    public ObservableCollection<PanelTab> PanelTabsBottom { get; } = new();
    
    public IRelayCommand OpenCommandPaletteCmd { get; }
    
    private readonly PanelRegistry _panelRegistry;
    private readonly CommandPaletteService _palette;
    
    public MainWindowViewModel(PanelRegistry registry, CommandPaletteService palette)
    {
        _panelRegistry = registry;
        _palette = palette;
        OpenCommandPaletteCmd = new RelayCommand(() => _palette.Show());
        
        // Initialize panels per region
        InitializePanels();
    }
    
    private void InitializePanels()
    {
        foreach (var d in _panelRegistry.AllDescriptors())
        {
            var tab = new PanelTab(d.DisplayName, d);
            switch (d.DefaultRegion)
            {
                case PanelRegion.Left: PanelTabsLeft.Add(tab); break;
                case PanelRegion.Center: PanelTabsCenter.Add(tab); break;
                case PanelRegion.Right: PanelTabsRight.Add(tab); break;
                case PanelRegion.Bottom: PanelTabsBottom.Add(tab); break;
            }
        }
    }
}
```

---

### Step 5: Add PanelTemplateSelector

**Skeleton:** `core/PanelTemplateSelector.cs`  
**Target:** `src/VoiceStudio.App/Controls/PanelTemplateSelector.cs`

**Actions:**
1. Create new file `src/VoiceStudio.App/Controls/PanelTemplateSelector.cs`
2. Copy skeleton implementation
3. Add DataTemplates for all panels in XAML resources

**Integration Pattern:**
```csharp
// NEW: src/VoiceStudio.App/Controls/PanelTemplateSelector.cs
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.Core.Panels;

namespace VoiceStudio.App.Controls
{
    public sealed class PanelTemplateSelector : DataTemplateSelector
    {
        public DataTemplate TextSpeechEditorTemplate { get; set; }
        public DataTemplate ProsodyTemplate { get; set; }
        // ... other templates ...

        protected override DataTemplate SelectTemplateCore(object item)
        {
            if (item is PanelDescriptor d)
            {
                switch (d.PanelId)
                {
                    case "TextSpeechEditor": return TextSpeechEditorTemplate;
                    case "ProsodyPhoneme": return ProsodyTemplate;
                    // ... other cases ...
                    default: return null;
                }
            }
            return null;
        }
    }
}
```

---

### Step 5: Add 9 Advanced Panel ViewModels

**Skeleton:** `ui/ViewModels/Panels/*.cs`  
**Target:** `src/VoiceStudio.App/ViewModels/Panels/*.cs`

**Actions:**
1. Copy all 9 ViewModels from skeleton
2. Update namespaces to match existing structure:
   - Skeleton: `VoiceStudio.ViewModels.Panels`
   - Existing: `VoiceStudio.App.ViewModels.Panels`
3. Ensure all implement `IPanelView` interface
4. Wire up `IBackendClient` dependency injection
5. **PRESERVE** existing 6 core panel ViewModels

**Files to Add:**
- `TextSpeechEditorPanelViewModel.cs`
- `ProsodyPanelViewModel.cs`
- `SpatialStagePanelViewModel.cs`
- `MixAssistantPanelViewModel.cs`
- `StyleTransferPanelViewModel.cs`
- `EmbeddingExplorerPanelViewModel.cs`
- `AssistantPanelViewModel.cs`
- `LexiconPanelViewModel.cs`
- `VoiceMorphPanelViewModel.cs`

**Integration Pattern:**
```csharp
// NEW: src/VoiceStudio.App/ViewModels/Panels/TextSpeechEditorPanelViewModel.cs
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using VoiceStudio.Core.Panels;
using VoiceStudio.Core.Services;

namespace VoiceStudio.App.ViewModels.Panels
{
    public sealed partial class TextSpeechEditorPanelViewModel : ObservableObject, IPanelView
    {
        [ObservableProperty] private bool isBusy;
        public IRelayCommand PreviewCmd { get; }
        public IRelayCommand ApplyCmd { get; }

        private readonly IBackendClient backend;

        // IPanelView implementation
        public string PanelId => "TextSpeechEditor";
        public string DisplayName => "Text-Based Speech Editor";
        public PanelRegion Region => PanelRegion.Center;

        public TextSpeechEditorPanelViewModel(IBackendClient backendClient)
        {
            backend = backendClient;
            PreviewCmd = new RelayCommand(OnPreview);
            ApplyCmd = new RelayCommand(OnApply);
        }

        private void OnPreview()
        {
            // TODO: call backend preview
        }

        private void OnApply()
        {
            // TODO: call backend apply
        }
    }
}
```

---

### Step 6: Add 9 Advanced Panel Views

**Skeleton:** `ui/Views/Panels/*.xaml`  
**Target:** `src/VoiceStudio.App/Views/Panels/*.xaml`

**Actions:**
1. Copy all 9 XAML Views from skeleton
2. Update namespaces to match existing structure:
   - Skeleton: `VoiceStudio.Views.Panels`
   - Existing: `VoiceStudio.App.Views.Panels`
3. Update code-behind files to match
4. Ensure all use design tokens (VSQ.*)
5. **PRESERVE** existing 6 core panel Views

**Files to Add:**
- `TextSpeechEditorView.xaml` + `.xaml.cs`
- `ProsodyView.xaml` + `.xaml.cs`
- `SpatialStageView.xaml` + `.xaml.cs`
- `MixAssistantView.xaml` + `.xaml.cs`
- `StyleTransferView.xaml` + `.xaml.cs`
- `EmbeddingExplorerView.xaml` + `.xaml.cs`
- `AssistantView.xaml` + `.xaml.cs`
- `LexiconView.xaml` + `.xaml.cs`
- `VoiceMorphView.xaml` + `.xaml.cs`

**Integration Pattern:**
```xml
<!-- NEW: src/VoiceStudio.App/Views/Panels/TextSpeechEditorView.xaml -->
<UserControl
  x:Class="VoiceStudio.App.Views.Panels.TextSpeechEditorView"
  xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
  xmlns:controls="using:Microsoft.UI.Xaml.Controls"
  Background="{StaticResource VSQ.Panel.BackgroundBrush}">
  <Grid Padding="8">
    <Grid.RowDefinitions>
      <RowDefinition Height="Auto"/>
      <RowDefinition Height="*"/>
      <RowDefinition Height="Auto"/>
    </Grid.RowDefinitions>

    <StackPanel Orientation="Horizontal" Spacing="6">
      <TextBlock Text="Text‑Based Speech Editor" 
                 Style="{StaticResource VSQ.Text.Title}"/>
    </StackPanel>

    <Border Grid.Row="1" 
            BorderBrush="{StaticResource VSQ.Panel.BorderBrush}" 
            BorderThickness="1" 
            CornerRadius="{StaticResource VSQ.CornerRadius.Panel}">
      <Grid>
        <TextBlock Text="Transcript + Word‑Aligned Waveform + Diff Overlays" 
                   Style="{StaticResource VSQ.Text.Body}"
                   Foreground="{StaticResource VSQ.Text.SecondaryBrush}"
                   HorizontalAlignment="Center" 
                   VerticalAlignment="Center"/>
      </Grid>
    </Border>

    <StackPanel Grid.Row="2" Orientation="Horizontal" Spacing="8" HorizontalAlignment="Right">
      <Button Content="Preview" />
      <Button Content="Apply" />
    </StackPanel>
  </Grid>
</UserControl>
```

**Code-Behind:**
```csharp
// NEW: src/VoiceStudio.App/Views/Panels/TextSpeechEditorView.xaml.cs
using Microsoft.UI.Xaml.Controls;
using VoiceStudio.App.ViewModels.Panels;

namespace VoiceStudio.App.Views.Panels
{
    public sealed partial class TextSpeechEditorView : UserControl
    {
        public TextSpeechEditorView()
        {
            this.InitializeComponent();
            this.DataContext = new TextSpeechEditorPanelViewModel(/* inject IBackendClient */);
        }
    }
}
```

---

### Step 7: Merge DesignTokens

**Skeleton:** `ui/Resources/DesignTokens.xaml`  
**Existing:** `src/VoiceStudio.App/Resources/DesignTokens.xaml`

**Actions:**
1. Read existing `DesignTokens.xaml`
2. Add new tokens from skeleton (preserve existing)
3. Add icon keys from skeleton
4. Ensure no conflicts

**Integration Pattern:**
```xml
<!-- Existing DesignTokens.xaml -->
<ResourceDictionary>
  <!-- EXISTING: Preserve all existing tokens -->
  <Color x:Key="VSQ.Background.Darker">#FF0A0F15</Color>
  <!-- ... existing tokens ... -->
  
  <!-- NEW: Add from skeleton (if not present) -->
  <SolidColorBrush x:Key="VSQ.Panel" Color="#12151C"/>
  <SolidColorBrush x:Key="VSQ.AccentAlt" Color="#7C4DFF"/>
  <SolidColorBrush x:Key="VSQ.SubtleText" Color="#9FB2C6"/>
  
  <!-- NEW: Add icon keys -->
  <x:String x:Key="Icon.EditText">Icon.EditText</x:String>
  <x:String x:Key="Icon.Prosody">Icon.Prosody</x:String>
  <!-- ... other icon keys ... -->
</ResourceDictionary>
```

---

### Step 8: Merge Services

#### CommandPaletteService

**Skeleton:** `services/CommandPaletteService.cs`  
**Existing:** `src/VoiceStudio.App/Services/CommandPaletteService.cs` (if exists)

**Actions:**
1. If exists: Merge skeleton enhancements
2. If not exists: Create from skeleton
3. Integrate with existing `CommandPalette` control
4. Wire to `PanelRegistry`

#### PluginService

**Skeleton:** `services/PluginService.cs`  
**Existing:** `src/VoiceStudio.App/Services/PluginManager.cs` (may exist)

**Actions:**
1. If `PluginManager.cs` exists: Merge skeleton into it
2. If not: Create `PluginService.cs` from skeleton
3. Integrate with existing plugin system

#### DiagnosticsService

**Skeleton:** `services/DiagnosticsService.cs`  
**Target:** `src/VoiceStudio.App/Services/DiagnosticsService.cs`

**Actions:**
1. Create new file from skeleton
2. Integrate with existing `DiagnosticsView`
3. Wire binding error logging

---

### Step 9: Add Backend Routes

**Skeleton:** `backend/app/routes/*.py`  
**Target:** `backend/api/routes/*.py` (or create `backend/api/` structure)

**Actions:**
1. Create backend directory structure if not exists:
   ```
   backend/
     api/
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
       models.py
       main.py
       ws/
         events.py
       requirements.txt
   ```
2. Copy all route files from skeleton
3. Copy `models.py` from skeleton
4. Copy `main.py` from skeleton
5. Copy `ws/events.py` from skeleton
6. Copy `requirements.txt` from skeleton
7. Update imports to match new structure

**Integration Pattern:**
```python
# NEW: backend/api/routes/asr.py
from fastapi import APIRouter
from ..models import *

router = APIRouter(prefix="/api/asr", tags=["asr"])

@router.post("/align")
def align_audio(req: dict) -> dict:
    # TODO: align words to timeline; return dummy
    return {
        "blocks": [{
            "start": 0,
            "end": 1000,
            "text": "Hello",
            "tokens": [{"t": "Hello", "s": 0, "e": 1000}]
        }]
    }
```

---

### Step 10: Add Tests

**Skeleton:** `tests/*.md`  
**Target:** `tests/*.md` (or `docs/tests/*.md`)

**Actions:**
1. Create `tests/` directory if not exists
2. Copy test documentation from skeleton:
   - `perf_budgets.md`
   - `ui_bindings.md`
   - `abx_protocol.md`
3. Integrate with existing test structure

---

## ✅ INTEGRATION CHECKLIST

### Core Infrastructure
- [ ] PanelRegistry merged (existing + skeleton)
- [ ] IBackendClient extended (existing + skeleton)
- [ ] ThemeManager added
- [ ] PanelTemplateSelector added
- [ ] DesignTokens merged (existing + skeleton)

### Advanced Panels
- [ ] 9 ViewModels added (with IPanelView implementation)
- [ ] 9 Views added (XAML + code-behind)
- [ ] All panels registered in PanelRegistry
- [ ] All panels use design tokens
- [ ] All panels have proper namespaces

### Services
- [ ] CommandPaletteService merged/created
- [ ] PluginService merged/created
- [ ] DiagnosticsService created
- [ ] All services integrated with existing code

### Backend
- [ ] Backend directory structure created
- [ ] All route files added
- [ ] models.py added
- [ ] main.py added
- [ ] WebSocket events.py added
- [ ] requirements.txt added

### Tests
- [ ] Test documentation added
- [ ] Performance budgets documented
- [ ] UI bindings checklist created
- [ ] ABX protocol documented

### Verification
- [ ] Solution compiles without errors
- [ ] All existing functionality preserved
- [ ] All new panels accessible via Command Palette
- [ ] All panels appear in PanelRegistry
- [ ] Backend routes return placeholder data (no 404s)
- [ ] Design tokens resolve correctly

---

## 🔍 NAMESPACE MAPPING

### Skeleton → Existing

| Skeleton Namespace | Existing Namespace |
|-------------------|-------------------|
| `VoiceStudio` | `VoiceStudio.Core` (for core types) |
| `VoiceStudio.ViewModels.Panels` | `VoiceStudio.App.ViewModels.Panels` |
| `VoiceStudio.Views.Panels` | `VoiceStudio.App.Views.Panels` |
| `VoiceStudio` (services) | `VoiceStudio.App.Services` |

**Update all skeleton files to use existing namespace structure.**

---

## 📝 FILES TO CREATE/MODIFY

### New Files (Add)
- `src/VoiceStudio.App/Services/ThemeManager.cs`
- `src/VoiceStudio.App/Controls/PanelTemplateSelector.cs`
- `src/VoiceStudio.App/Services/DiagnosticsService.cs`
- `src/VoiceStudio.App/ViewModels/Panels/TextSpeechEditorPanelViewModel.cs`
- `src/VoiceStudio.App/ViewModels/Panels/ProsodyPanelViewModel.cs`
- `src/VoiceStudio.App/ViewModels/Panels/SpatialStagePanelViewModel.cs`
- `src/VoiceStudio.App/ViewModels/Panels/MixAssistantPanelViewModel.cs`
- `src/VoiceStudio.App/ViewModels/Panels/StyleTransferPanelViewModel.cs`
- `src/VoiceStudio.App/ViewModels/Panels/EmbeddingExplorerPanelViewModel.cs`
- `src/VoiceStudio.App/ViewModels/Panels/AssistantPanelViewModel.cs`
- `src/VoiceStudio.App/ViewModels/Panels/LexiconPanelViewModel.cs`
- `src/VoiceStudio.App/ViewModels/Panels/VoiceMorphPanelViewModel.cs`
- `src/VoiceStudio.App/Views/Panels/TextSpeechEditorView.xaml` + `.cs`
- `src/VoiceStudio.App/Views/Panels/ProsodyView.xaml` + `.cs`
- `src/VoiceStudio.App/Views/Panels/SpatialStageView.xaml` + `.cs`
- `src/VoiceStudio.App/Views/Panels/MixAssistantView.xaml` + `.cs`
- `src/VoiceStudio.App/Views/Panels/StyleTransferView.xaml` + `.cs`
- `src/VoiceStudio.App/Views/Panels/EmbeddingExplorerView.xaml` + `.cs`
- `src/VoiceStudio.App/Views/Panels/AssistantView.xaml` + `.cs`
- `src/VoiceStudio.App/Views/Panels/LexiconView.xaml` + `.cs`
- `src/VoiceStudio.App/Views/Panels/VoiceMorphView.xaml` + `.cs`
- `backend/api/routes/*.py` (all route files)
- `backend/api/models.py`
- `backend/api/main.py`
- `backend/api/ws/events.py`
- `backend/api/requirements.txt`
- `tests/perf_budgets.md`
- `tests/ui_bindings.md`
- `tests/abx_protocol.md`

### Existing Files (Modify)
- `src/VoiceStudio.Core/Panels/PanelRegistry.cs` - Merge skeleton enhancements
- `src/VoiceStudio.Core/Services/IBackendClient.cs` - Extend with skeleton methods
- `src/VoiceStudio.App/Resources/DesignTokens.xaml` - Merge skeleton tokens
- `src/VoiceStudio.App/Services/CommandPaletteService.cs` - Merge if exists
- `src/VoiceStudio.App/Services/PluginService.cs` or `PluginManager.cs` - Merge if exists

---

## 🚨 CRITICAL INTEGRATION RULES

1. **PRESERVE EXISTING CODE** - Never delete existing functionality
2. **MERGE, DON'T REPLACE** - Add skeleton code alongside existing
3. **NAMESPACE CONSISTENCY** - Update all skeleton files to match existing structure
4. **DESIGN TOKENS** - Use existing VSQ.* tokens, add new ones from skeleton
5. **MVVM SEPARATION** - No logic in code-behind, all in ViewModels
6. **IPanelView IMPLEMENTATION** - All new ViewModels must implement IPanelView
7. **BACKEND COMPATIBILITY** - Ensure backend routes match IBackendClient interface

---

## 📚 REFERENCE DOCUMENTS

- `PANEL_IMPLEMENTATION_GUIDE.md` - Complete panel implementation guide
- `INNOVATIVE_ADVANCED_PANELS_CATALOG.md` - Advanced panels catalog
- `INTEGRATION_GUIDE.md` - General integration patterns
- `PRESERVATION_CHECKLIST.md` - Preservation guide
- `CURSOR_AGENT_GUIDELINES_V2.md` - Agent system guidelines

---

## 💡 KEY REMINDERS

1. **Skeleton is a starting point** - Enhance with full implementation
2. **Preserve existing structure** - Don't break what works
3. **Update namespaces** - Match existing codebase structure
4. **Wire up dependencies** - IBackendClient, PanelRegistry, etc.
5. **Test after each step** - Verify compilation and functionality

**Remember:** Integration means merging, not replacing. Preserve everything that works, add new alongside.

