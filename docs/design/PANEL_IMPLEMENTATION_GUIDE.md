# VoiceStudio Quantum+ Panel Implementation Guide
## Complete Guide for Implementing 100+ Modular Panels

**Version:** 1.0  
**Based on:** VoiceStudio Quantum+ Panel Implementation Guide  
**Purpose:** Comprehensive guide for implementing all panels following MVVM patterns

---

## 📋 TABLE OF CONTENTS

1. [Panel Tiers and Organization](#panel-tiers)
2. [Panel Structure (View, ViewModel, Service Wiring)](#panel-structure)
3. [Panel Registration and Navigation](#panel-registration)
4. [Real-Time Data Flow with IBackendClient](#realtime-data)
5. [Specific Panel Implementations](#specific-panels)
6. [Diagnostics and Debugging](#diagnostics)
7. [Theme Switching](#theme-switching)
8. [PanelStack for Multiple Panels](#panelstack)

---

## 🏷️ Panel Tiers and Organization {#panel-tiers}

VoiceStudio's panels are categorized into **five tiers** to group features by user level or functionality:

### Tier Definitions

**Core Panels:**
- Fundamental features always available to all users
- Examples: Timeline editor, Profiles manager, Mixer, Library
- Default panels comprising the primary studio workflow

**Pro Panels:**
- Premium or advanced creative tools, enabled for pro users
- Examples: Advanced prosody editor, multi-voice generator, deepfake creator
- Conditionally enabled based on license or settings

**Advanced Panels:**
- Specialized high-end functionalities or analytical tools for power users
- Examples: GPU/MCP performance dashboard, detailed analytics charts, spectrogram analyzer
- Might require activating "Advanced Mode" in the UI

**Technical Panels:**
- System, developer, or debugging-oriented panels
- Examples: Diagnostics/log viewer, plugin debug console, raw API inspector
- Often hidden under a developer toggle or used internally

**Meta Panels:**
- Overarching utility or meta-information panels spanning multiple domains
- Examples: "Ultimate Dashboard" aggregating stats, AI Governor control panel, project-wide settings
- Provide cross-cutting oversight or configuration

### PanelTier Enum

```csharp
public enum PanelTier
{
    Core,
    Pro,
    Advanced,
    Technical,
    Meta
}
```

### PanelDescriptor Extension

Extend `PanelDescriptor` to include `Tier`:

```csharp
public sealed class PanelDescriptor
{
    public string PanelId { get; init; } = string.Empty;
    public string DisplayName { get; init; } = string.Empty;
    public PanelRegion Region { get; init; }
    public Type ViewType { get; init; } = typeof(object);
    public Type ViewModelType { get; init; } = typeof(object);
    public PanelTier Tier { get; init; } = PanelTier.Core;  // NEW
    public string Category { get; init; } = string.Empty;  // NEW (Studio, Profiles, Library, etc.)
    public Symbol Icon { get; init; } = Symbol.Document;    // NEW
    public bool IsPlugin { get; init; } = false;            // NEW
}
```

**Key Point:** While tiers help organize panels, every panel follows the same scaffolding pattern and is integrated into the unified system. The PanelRegistry contains entries for all ~100+ panels, regardless of tier, so they can be easily instantiated and shown on demand.

---

## 🏗️ Panel Structure: View, ViewModel, and Service Wiring {#panel-structure}

Each panel in VoiceStudio Quantum+ is implemented using the **MVVM (Model-View-ViewModel)** pattern.

### Required Components

Every panel should be scaffolded with:

1. **View (XAML):** Defines the UI layout and bindings
2. **ViewModel (C# class):** Contains state and logic, interacts with backend services
3. **Optional Model or Service references:** For complex data structures

### File Organization

**Consistent naming and folder structure:**

```
Panels/
├── Core/
│   ├── ProfilesView.xaml
│   ├── ProfilesView.xaml.cs
│   ├── ProfilesViewModel.cs
│   ├── TimelineView.xaml
│   └── ...
├── Pro/
│   ├── AdvancedMixerView.xaml
│   └── ...
├── Advanced/
│   └── ...
├── Technical/
│   └── ...
└── Meta/
    └── ...
```

**Alternative:** Group by function instead of tier (flat structure under `Panels/`).

**Namespace Convention:**
- ViewModels: `VoiceStudio.App.ViewModels.Panels` or `VoiceStudio.Panels`
- Views: `VoiceStudio.App.Views.Panels`

---

## 📐 View (XAML) Guidelines

### Structure

- Use a **UserControl** (or Page) for each panel's view XAML
- This UserControl will be loaded into a PanelHost
- The XAML defines the layout (grids, text, buttons, charts, etc.)

### Data Binding

- Bind UI elements to ViewModel properties using `{Binding ...}` or `{x:Bind ...}`
- **Prefer `{x:Bind}`** for compile-time binding (better performance, catches errors at build time)
- `{Binding}` with DataContext is fine for more dynamic scenarios

### Code-Behind Rules

**DO NOT put application logic in code-behind of XAML.cs**

The code-behind should ideally only contain:
- `InitializeComponent()`
- Setting the DataContext to the ViewModel

**Example:**
```csharp
public sealed partial class VoiceTrainingView : UserControl
{
    public VoiceTrainingView()
    {
        this.InitializeComponent();
        this.DataContext = new VoiceTrainingViewModel(); // Assign VM
    }
}
```

**Alternative:** If using dependency injection or MVVM framework (like MVVM Toolkit), resolve ViewModel from container.

**Key Point:** The view should NOT implement logic itself; it relies on binding to the ViewModel.

### Styling

- Apply consistent styling using design tokens from `DesignTokens.xaml`
- Use `Background="{StaticResource VSQ.Panel.Background}"` or similar tokens
- Use text styles like `Style="{StaticResource VSQ.Text.Body}"`
- **Do not hardcode colors or sizes** - use shared resources
- All panels must adhere to the unified theme

### Panel Title/Icon

- Each panel View might include a title or icon, but since PanelHost provides a header with title and icon, the panel's content area usually just contains the functional UI
- PanelHost will display the panel's DisplayName and Icon in its chrome
- Design your XAML assuming it will be hosted inside a PanelHost with a title bar

---

## 💻 ViewModel (C#) Guidelines

### Base Class

- Derive from a base class that supports property change notifications
- Implement `INotifyPropertyChanged`, or use `ObservableObject` from `CommunityToolkit.Mvvm`
- Each ViewModel should expose properties (and possibly `ObservableCollection`s) that the View binds to

**Example:**
```csharp
public class SpectrogramViewModel : ObservableObject
{
    private ImageSource _spectrogramImage;
    public ImageSource SpectrogramImage
    {
        get => _spectrogramImage;
        set => SetProperty(ref _spectrogramImage, value);
    }
}
```

### Commands

- Include **commands** (typically `ICommand` implementations) in the ViewModel for any user actions
- Use `RelayCommand` or similar patterns to implement commands
- Commands call into backend services or perform logic

**Example:**
```csharp
public ICommand GenerateSpectrogramCommand => new RelayCommand(() =>
{
    backend.RequestSpectrogram(currentAudioId);
});
```

### Service Wiring

Each ViewModel that needs to communicate with the backend should get an instance of the relevant service:

- Primary service: `IBackendClient` - interface abstracting calls to Python FastAPI backend
- Accept `IBackendClient` via constructor or fetch from ServiceProvider
- ViewModels remain decoupled from actual communication details

**Example Skeleton:**
```csharp
public class SpectrogramViewModel : ObservableObject
{
    private readonly IBackendClient backend; // backend service interface

    public SpectrogramViewModel(IBackendClient backendClient)
    {
        backend = backendClient;
        // Subscribe to backend events for live updates
        backend.SpectrogramUpdated += OnSpectrogramUpdated;
    }

    private ImageSource _spectrogramImage;
    public ImageSource SpectrogramImage
    {
        get => _spectrogramImage;
        set => SetProperty(ref _spectrogramImage, value);
    }

    private void OnSpectrogramUpdated(object sender, SpectrogramDataEventArgs e)
    {
        // Assume e contains new spectrogram image data
        SpectrogramImage = ConvertToImage(e.ImageData);
    }

    public ICommand GenerateSpectrogramCommand => new RelayCommand(() =>
    {
        // Send request to backend to generate/update spectrogram
        backend.RequestSpectrogram(currentAudioId);
    });
}
```

### No Logic in Views

**All business logic, data handling, and backend calls should reside in ViewModel (or lower service) code.**

The XAML code-behind should contain **zero logic** except possibly UI-specific tweaks or events that cannot be handled via binding (and even those should call into the ViewModel).

**Rule:** If you open any panel's `.xaml.cs`, it should be trivial or empty, while all functionality is in the corresponding `ViewModel.cs`.

---

## 📝 Panel Registration and Navigation {#panel-registration}

### PanelRegistry

All panels are discovered and loaded via a central **PanelRegistry**. The PanelRegistry maintains metadata about each panel and provides lookup functions.

**Register every panel (Core, Pro, Advanced, etc.) with this registry** so the UI can create instances on demand.

### PanelDescriptor

Each panel is described by a `PanelDescriptor` object containing:

- `PanelId` - Unique string key
- `DisplayName` - User-friendly name for UI
- `Icon` - Icon asset or Symbol to display in PanelHost header or menus
- `Region` - Which layout region the panel defaults to (Left, Center, Right, Bottom, etc.)
- `ViewType` - The Type of the UserControl for the panel's View
- `ViewModelType` - The Type of its ViewModel
- `Tier` - PanelTier (Core, Pro, Advanced, Technical, Meta)
- `Category` - Category string (Studio, Profiles, Library, Effects, Train, Analyze, Settings, Logs)

### Registration at Startup

**Ensure that all panels are registered at startup.**

This can be done in `App.OnLaunched` or during `MainWindow` initialization:

```csharp
_panelRegistry = new PanelRegistry();

_panelRegistry.Register(new PanelDescriptor
{
    PanelId = "Profiles",
    DisplayName = "Profiles",
    Region = PanelRegion.Left,
    Icon = Symbol.Contact,
    ViewType = typeof(ProfilesView),
    ViewModelType = typeof(ProfilesViewModel),
    Tier = PanelTier.Core,
    Category = "Profiles"
});

_panelRegistry.Register(new PanelDescriptor
{
    PanelId = "Timeline",
    DisplayName = "Timeline",
    Region = PanelRegion.Center,
    Icon = Symbol.Audio,
    ViewType = typeof(TimelineView),
    ViewModelType = typeof(TimelineViewModel),
    Tier = PanelTier.Core,
    Category = "Studio"
});

// ... (register all other panels similarly)
```

**Tip:** Group registration calls by tier or feature for readability. Register all Core panels together, then Pro, etc.

### Navigation and Panel Activation

VoiceStudio's UI has a left navigation rail with main sections (Studio, Profiles, Library, Effects, Train, Analyze, Settings, Logs, etc.).

**Each nav button, when clicked, should activate the appropriate panel(s) via the PanelRegistry.**

**Mapping Examples:**
- "Profiles" button → Opens **Profiles** panel in left region
- "Library" → Opens **Library** panel (center region)
- "Effects" → Opens **Effects** panel (right region)
- "Train" → Opens **VoiceTraining** panel (center region)
- "Analyze" → Opens **Analyzer** or **Spectrogram** panel
- "Settings" → Opens **Settings** panel
- "Logs" → Opens **Diagnostics/Logs** panel (bottom region)
- "Studio" → Resets to default arrangement (Timeline center, Mixer right, etc.)

**Implementation:**
```csharp
void OnNavButtonClick(object sender, RoutedEventArgs e)
{
    var button = (ToggleButton)sender;
    string panelId = MapNavButtonToPanelId(button.Name);
    ActivatePanel(panelId);
}

void ActivatePanel(string panelId)
{
    PanelDescriptor desc = _panelRegistry.GetPanel(panelId);
    if (desc == null) return;

    // Determine target region host
    PanelRegion region = desc.Region;
    PanelHost host = GetPanelHostForRegion(region);

    // If PanelStack is enabled in that host, add or switch tab
    var view = (UserControl)Activator.CreateInstance(desc.ViewType);
    
    // Optionally, if using manual ViewModel creation:
    // var vm = (ViewModelBase)_serviceProvider.GetService(desc.ViewModelType);
    // view.DataContext = vm;

    host.SetContent(view, desc.DisplayName, desc.Icon);
}
```

**Note:** If PanelHost contains a PanelStack (tabs), add the panel as a new tab instead of replacing content (see PanelStack section).

### Panel Hosts and Regions

The main window layout is divided into regions (Left, Center, Right, Bottom, etc.) each containing a **PanelHost** control.

**Default Panel Assignments:**
- Profiles → Left region
- Timeline → Center region
- Mixer → Right region
- Macro → Bottom region

On startup, load default panels into each region's PanelHost:

```csharp
var defaultLeft = _panelRegistry.GetDefaultPanel(PanelRegion.Left);
LeftPanelHost.SetContent(
    (UserControl)Activator.CreateInstance(defaultLeft.ViewType),
    defaultLeft.DisplayName,
    defaultLeft.Icon
);
```

---

## 🔄 Real-Time Data Flow with IBackendClient {#realtime-data}

One of the critical aspects is routing live data from the Python backend (FastAPI and MCP servers) to the UI panels.

### IBackendClient Interface

The **IBackendClient** interface serves as the bridge. It should handle:

1. **Requests/Commands** from UI to backend (e.g., "start training model", "synthesize this text", "fetch library items")
2. **Real-time updates/events** from backend to UI (e.g., progress updates, streamed data like spectrogram frames, log messages)

### Implementation

**IBackendClient Interface:**
```csharp
interface IBackendClient
{
    // Requests (async returning Task or data)
    Task<ProjectData> LoadProjectAsync(string projectId);
    Task<bool> StartTrainingAsync(TrainingParams args);
    Task<AudioData> SynthesizeSpeechAsync(string text, VoiceSettings settings);
    // ...other request methods...

    // Events for realtime updates
    event EventHandler<TrainingProgressEventArgs> TrainingProgress;
    event EventHandler<SpectrogramDataEventArgs> SpectrogramUpdated;
    event EventHandler<LogMessageEventArgs> LogMessageReceived;
    // ...other events...
}
```

**BackendClient Implementation:**
- Initialize on startup (perhaps as a singleton)
- Connect to FastAPI server (local or remote)
- Start background task to listen on WebSocket for events
- Hook incoming messages to appropriate events

### WebSocket for Real-Time Updates

**WebSocket is preferred for responsiveness.**

- FastAPI endpoint for WebSocket connections that pushes events
- BackendClient holds WebSocket connection to receive push notifications
- For long jobs (like training), backend sends periodic status events over socket

**Alternative:** If WebSocket not feasible, use SignalR or polling (less preferred).

### Thread Safety

**Ensure thread-safety:**
- WebSocket listener runs on background thread
- When raising events that update ObservableCollections or UI-bound properties, marshal to UI thread
- Use `CoreDispatcher` or `SynchronizationContext` in WinUI
- IBackendClient can handle this by invoking events on UI thread
- ViewModel can use `DispatcherQueue.TryEnqueue` when setting properties

### Example: Live Update Flow

**Voice Training Session:**
1. User clicks "Train" in VoiceTrainingView → bound to `StartTrainingCommand` in ViewModel
2. Command calls `IBackendClient.StartTrainingAsync` with parameters
3. FastAPI backend starts training job and returns acknowledgment
4. As training proceeds, backend emits progress events over WebSocket
5. BackendClient receives messages, identifies as training progress, invokes `TrainingProgress` event
6. VoiceTrainingViewModel (subscribed to `backend.TrainingProgress`) receives event
7. ViewModel updates `Progress` property and `StatusMessage` property
8. UI's progress bar and status text (bound to those properties) automatically refresh
9. On completion, final events sent, UI shows completion message

**This pattern should be applied to any panel requiring live updates:**
- Spectrogram panel for real-time visualization
- Analyzer panel for level meters
- Logs panel for new log entries
- Training panel for progress
- etc.

### Summary for Each Panel

**For each panel:**
1. Identify what data/actions it needs from the backend
2. In its ViewModel, subscribe to relevant events (or call appropriate backend methods)
3. Update properties on events so the UI reflects new data
4. Use commands to trigger backend actions and handle results
5. Keep interactions asynchronous and user-friendly (show loading indicators via UI binding)

**By routing everything through IBackendClient, we have a single coordination point for backend calls**, which can internally coordinate with multiple microservices or agents.

---

## 🎯 Specific Panel Implementations {#specific-panels}

### VoiceTraining Panel (Train Panel)

**Purpose:** Allows user to train a custom voice model using provided audio data.

**UI & ViewModel:**
- Controls: dataset selection, training parameters (dropdowns, sliders), "Start Training" button, progress bar, log output/status display
- ViewModel manages these and interacts with training service

**Backend Integration:**
1. User clicks "Start Training" → call `backend.StartTrainingAsync(params)` from ViewModel
2. Backend endpoint (e.g., `POST /train`) kicks off process
3. Might go through SupervisorAI to distribute task to specific engine (voice cloning MCP server)
4. `ai_context.json` may contain context (project/user info) - pass along in request
5. UI immediately reflects running state: disable Start button, show progress 0%, etc.
6. ViewModel properties: `IsTraining` (bool), `TrainingProgress` (0-100), `StatusMessage`
7. Backend sends progress updates via WebSocket → triggers `IBackendClient.TrainingProgress` events
8. ViewModel's subscribed handler updates `TrainingProgress` and status text
9. XAML binds ProgressBar value and TextBlock to these properties
10. On completion, final event indicates success/failure, ViewModel sets `IsTraining = false`

**Edge Cases:**
- If user navigates away during training, background process still runs
- IBackendClient handles that globally
- Panel could be reopened later and still receive updates if connection active
- Keep VoiceTrainingViewModel alive for duration (PanelStack tab remains until user closes)
- Global indicator (Status Bar) shows training job running

### Spectrogram Panel (Analyze Audio)

**Purpose:** Visualize audio as a spectrogram (frequency vs time heatmap) in real-time or on-demand.

**UI & ViewModel:**
- Display image or graphical control showing spectrogram
- Controls for zoom, playback, or capturing new audio
- ViewModel manages image data and possibly audio playback synchronization

**Backend Integration - Two Modes:**

**1. Static Analysis:**
- User provides audio clip (file selection or current project's audio)
- Hits "Generate Spectrogram"
- ViewModel calls `backend.RequestSpectrogram(audioId)`
- FastAPI service processes audio (libraries or AI for analysis)
- Returns raw data (array of values) or image (PNG)
- IBackendClient raises `SpectrogramUpdated` with result
- ViewModel sets `SpectrogramImage` property to display it

**2. Real-Time Mode:**
- If spectrogram should update live during playback/recording
- UI subscribes to streaming data
- Audio engine sends short spectrogram slices or FFT data continuously (e.g., every 50ms)
- IBackendClient has event (like `AudioFrameAnalyzed` with frequency data)
- ViewModel accumulates these into image or uses control that can draw streaming spectrogram
- Simpler approach: backend streams video or sequence of images that UI updates

**Display:**
- XAML shows in `<Image Stretch="Uniform">` control
- Or `SwapChainPanel` for high-performance drawing (DirectX rendering)
- Image updated a few times per second is fine

**Additional Features:**
- Overlay playhead if audio is playing
- Subscribe to "current playback time" event
- Draw vertical line on spectrogram image indicating current playback position
- Could be done by separate canvas overlay or regenerating image with highlight

### SSML Editor Panel

**Purpose:** Interface for editing SSML (Speech Synthesis Markup Language) and previewing synthesized speech.

**UI & ViewModel:**
- Text editor for SSML markup
- Preview button to synthesize and play audio
- Possibly syntax highlighting or validation
- ViewModel manages SSML text and preview audio

**Backend Integration:**
- User edits SSML text → ViewModel property `SsmlText` (string)
- User clicks "Preview" → command calls `backend.SynthesizeSpeechAsync(ssmlText, voiceSettings)`
- Backend endpoint (e.g., `POST /synthesize`) processes SSML
- Returns audio data (file path or byte array)
- ViewModel receives result, sets `PreviewAudioPath` property
- UI binds audio player control to this path
- User can play preview

**Note:** SSML panel might use existing SSML panel to show results, or plugin that analyzes audio might leverage Spectrogram panel.

### Plugin Panels

**Purpose:** Panels provided by plugins (loaded dynamically).

**Integration:**
- Plugin assemblies loaded at startup (or runtime on command)
- Register any new panels into PanelRegistry
- Panels can communicate with plugin's backend functions via existing IBackendClient
- Keep UI styling consistent (use same resources)
- Allow theme switching to affect plugin panels
- Provide debugging support: tie into Diagnostics panel to log plugin info or errors

**Plugin Manager Panel:**
- List all active plugins
- Allow interacting with them (toggling, showing info)
- Show list of plugin names and statuses
- "Open [PluginName] Panel" if applicable
- Implement with PluginService

**Cursor Implementation:**
- Load plugin assemblies at startup (and possibly at runtime on command)
- Register any new panels into PanelRegistry
- Ensure panels can communicate with their plugin's backend functions via existing IBackendClient
- Keep UI styling consistent and allow theme switching
- Provide debugging support: tie into Diagnostics panel

---

## 🔍 Diagnostics and Debugging {#diagnostics}

With ~100 panels and complex data binding, diagnostics are crucial.

### Binding Errors

**In WinUI, binding failures typically output warnings to debug console.**

**To surface these:**
- Run app in debug mode and watch output
- Enable logging for binding errors
- Use `x:Bind` (fails at compile if property doesn't exist)
- Subscribe to `FrameworkElement.BindingFailed` events

**Example:**
```csharp
FrameworkElement.BindingFailed += (sender, args) =>
{
    Debug.WriteLine($"Binding failed: {args.Message}");
    // Optionally, collect these messages in a list to show in debug console UI
    DiagnosticsService.ReportBindingError(args.Message);
};
```

**DiagnosticsViewModel** could have `ObservableCollection<LogMessage>` that includes binding error messages, which DiagnosticsView displays (filtered or tagged as "Binding").

**In development builds, developers can open Diagnostics panel and see if any binding is broken for newly added panels.**

### Hot Reload / Live Update of UI

- WinUI 3 XAML Hot Reload can be useful during development
- If panel's XAML is changed and hot-reloaded, binding diagnostics help ensure everything still works
- Developers should verify each panel's bindings

### Performance Diagnostics

- Diagnostics panel might show data binding performance or general UI performance metrics
- With many panels and possibly a lot of data, monitoring UI thread FPS or memory could be relevant
- Tools like WinUI's built-in visual diagnostics or Event Tracing for Windows (ETW) could be integrated
- For now, stick to binding and log diagnostics

---

## 🎨 Theme Switching {#theme-switching}

VoiceStudio Quantum+ uses a theming system defined in `DesignTokens.xaml` and a `ThemeManager` class for runtime theme changes.

### Global Resource Dictionaries

- Default theme (professional dark theme) is already loaded in `App.xaml`
- If multiple themes are supported (e.g., light theme or alternate "Sci-Fi" theme), prepare additional ResourceDictionary XAML files:
  - `DesignTokens.Light.xaml`
  - `DesignTokens.SciFi.xaml`
- These define the same resource keys (`VSQ.*`) but with different values (colors, etc.)

### ThemeManager

The `ThemeManager` class holds the current theme and can apply a new one.

**Method: `ApplyTheme(string themeName)`**
1. Loads the XAML ResourceDictionary for the given theme
2. Replaces or updates resource values
3. All bound UI (which uses `StaticResource` or `ThemeResource`) will update if those resources change
4. If using `StaticResource`, you might need to re-merge to get changes
5. If using `ThemeResource`, it updates automatically when theme changes
6. **Use `ThemeResource` for colors that can change with theme**
7. Handle any theme-specific logic (like switching icons if needed for light vs dark)

### UI to Trigger Theme Switching

- Under the **View** menu, add options like "Theme: Dark / Light / Professional / SciFi"
- When user selects one, call `ThemeManager.ApplyTheme`
- Persist the choice (in settings) so that on next run the theme is restored

### Panel Considerations

- All panels use shared resources, so theoretically they will all update when theme changes
- If any panel does custom drawing (e.g., custom control in code-behind) using old values, it should listen for theme changes
- In WinUI, controls get a theme changed event if system theme changes
- For custom theme, you might need to manually notify
- **If using only XAML-defined brushes and ThemeResource, you are safe**

### Layout Themes

- "Layout themes" suggests different panel layouts or densities for different use cases
- "Professional layout" vs "Simplified layout"
- ThemeManager could adjust things like panel default placements or visibility
- "Beginner" layout might hide advanced panels
- This overlaps with tiers: switching to "Simple Mode" could simply not show Advanced/Technical tier panels
- If such layout presets exist, they can be invoked similarly (perhaps via Workspace dropdown or separate setting)

**Cursor Implementation:**
- Implement ThemeManager wiring
- Connect menu commands to theme apply logic
- Verify that all UI elements including panels reflect the change
- If switching to light theme, PanelHosts and panels should all update their backgrounds, text colors, etc., as defined in alternate DesignTokens

---

## 📚 PanelStack for Multiple Panels per Region {#panelstack}

Originally, the interface replaced the content of each PanelHost when switching panels. To meet the full **studio-grade spec**, we need to allow **multiple panels in the same region simultaneously** via a tabbed interface – this is where **PanelStack** comes in.

### Design

- Each PanelHost will contain a PanelStack control instead of a direct ContentPresenter
- In `PanelHost.xaml`, inside the panel body, place a `TabView` (WinUI's TabView control) or custom control
- Each tab's content will be one panel's UserControl
- PanelHost will bind TabView's Items to a collection of open panels

### PanelStackViewModel

- Maintain a **PanelStackViewModel** per region, or integrated into each PanelHost's ViewModel
- Has `ObservableCollection<PanelDescriptor>` or `<PanelInstance>` representing open panels in that host
- Has an index for the selected tab

### PanelRegistry Integration

- PanelRegistry can assist PanelStack when adding new panels
- Add a method `OpenPanel(string panelId)` that internally calls PanelRegistry to get descriptor and then adds it to appropriate PanelStack collection
- Could be part of PanelHost's code-behind or a Navigation service

### Implementation Steps

1. **Create PanelStack Control:**
   - If not using WinUI's built-in TabView, create a user control `PanelStack.xaml` that wraps a TabView
   - PanelStack would have methods like `AddPanel(UserControl panel, string title, Icon icon)` to add a new tab
   - `ClosePanel(UserControl panel)` to remove
   - **Easier: use TabView directly in PanelHost**

2. **Modify PanelHost:**
   - Change `PanelHost.xaml` to include a TabView in the content area
   - When only one panel is present, hide the tab strip for cleaner look (TabView has property to hide tabs if only one item)
   - PanelHost's dependency properties (Title, Icon, Content) may need adjustments: with multiple tabs, each tab has its own title/icon
   - PanelHost's header could either reflect the active tab's info, or move title/icon into TabView's tabs themselves

3. **Good Approach:**
   - Each Tab item's header is a combination of icon and title of that panel
   - PanelHost header remains for window controls (pop-out, collapse, etc.) and shows active tab's title/icon
   - When tab changes, update PanelHost header to match active tab

4. **PanelStack Integration:**
   - When `ActivatePanel(panelId)` is called:
     - Check if PanelStack is enabled in that PanelHost
     - If panel already open (exists in PanelStack), switch to that tab
     - If not open, add as new tab
     - Set as active tab

### Example Flow

```csharp
void ActivatePanel(string panelId)
{
    PanelDescriptor desc = _panelRegistry.GetPanel(panelId);
    if (desc == null) return;

    PanelRegion region = desc.Region;
    PanelHost host = GetPanelHostForRegion(region);
    PanelStack stack = host.GetPanelStack(); // Get the TabView/PanelStack

    // Check if panel already open
    var existingTab = stack.Items.FirstOrDefault(t => t.PanelId == panelId);
    if (existingTab != null)
    {
        stack.SelectedItem = existingTab; // Switch to existing tab
        return;
    }

    // Create new panel instance
    var view = (UserControl)Activator.CreateInstance(desc.ViewType);
    var tabItem = new TabViewItem
    {
        Header = desc.DisplayName,
        IconSource = new SymbolIconSource { Symbol = desc.Icon },
        Content = view
    };

    stack.Items.Add(tabItem);
    stack.SelectedItem = tabItem;
    
    // Update PanelHost header to match active tab
    host.Title = desc.DisplayName;
    host.Icon = desc.Icon;
}
```

### Persistence

- PanelStack state (which tabs are open, which is active) should be saved to `LayoutTheme.json`
- On startup, restore open panels per region
- This allows users to have their preferred panel arrangement persist across sessions

---

## ✅ Implementation Checklist

### For Each Panel

- [ ] Create View (XAML) as UserControl
- [ ] Create ViewModel (C#) implementing INotifyPropertyChanged or ObservableObject
- [ ] ViewModel implements IPanelView interface
- [ ] ViewModel has IBackendClient dependency (via constructor or service locator)
- [ ] ViewModel subscribes to relevant backend events
- [ ] ViewModel exposes properties for UI binding
- [ ] ViewModel exposes commands for user actions
- [ ] Code-behind only contains InitializeComponent() and DataContext assignment
- [ ] View uses design tokens (no hardcoded colors/sizes)
- [ ] Panel registered in PanelRegistry with complete metadata
- [ ] Panel assigned to appropriate region
- [ ] Panel tier and category set correctly
- [ ] Navigation button mapped to panel (if applicable)
- [ ] Panel tested with real-time data updates (if applicable)
- [ ] Panel tested with theme switching
- [ ] Panel works in PanelStack (if applicable)

---

## 📚 Reference Documents

- `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` - Master specification
- `INNOVATIVE_ADVANCED_PANELS_CATALOG.md` - **NEW** - Complete catalog of 9 innovative advanced panels
- `CURSOR_AGENT_GUIDELINES_V2.md` - Archived: [legacy_worker_system/design/](../archive/legacy_worker_system/design/CURSOR_AGENT_GUIDELINES_V2.md)
- `INTEGRATION_GUIDE.md` - Archived: [legacy_worker_system/design/](../archive/legacy_worker_system/design/INTEGRATION_GUIDE.md)
- `PRESERVATION_CHECKLIST.md` - Preservation guide
- `MEMORY_BANK.md` - Archived: [legacy_worker_system/design/](../archive/legacy_worker_system/design/MEMORY_BANK.md)

---

## 💡 Key Reminders

1. **MVVM separation is mandatory** - No logic in code-behind
2. **Use design tokens** - No hardcoded values
3. **IBackendClient for all backend communication** - Single coordination point
4. **Real-time updates via events** - WebSocket preferred
5. **Thread safety** - Marshal to UI thread when updating properties
6. **PanelRegistry for all panels** - Register at startup
7. **PanelStack for multiple panels** - Tabbed interface per region
8. **Theme switching** - All panels must support it
9. **Diagnostics** - Binding errors and performance monitoring

**Remember:** Every panel follows the same pattern. Consistency ensures maintainability and extensibility.

