# ADR-028: Unified Command Architecture

## Status

**Accepted** (2026-02-08)

## Context

VoiceStudio evolved with three parallel command invocation mechanisms:

1. **ViewModel ICommands** (~400+ across ViewModels) - Standard WPF/WinUI pattern
2. **Click Handlers** (~100+ in MainWindow.xaml.cs) - Direct event handlers
3. **UnifiedCommandRegistry** (33+ commands) - Centralized command system with routing

This fragmentation led to:
- Commands not executing when buttons clicked
- Missing command handlers for menu items
- Keyboard shortcuts not working consistently
- No centralized health monitoring
- Difficult debugging of "why didn't this button work?"

The UnifiedCommandRegistry was introduced but not fully integrated, leaving gaps where:
- Navigation buttons used direct SwitchToPanel calls
- Menu items had individual event handlers
- No connection between UI elements and registry commands

## Options Considered

### Option 1: Full ViewModel Migration

Migrate all commands to ViewModel ICommands, removing the registry.

**Pros:**
- Standard MVVM pattern
- IDE support for bindings
- No custom infrastructure

**Cons:**
- Loses centralized command tracking
- No built-in keyboard shortcut system
- Commands scattered across ViewModels
- Difficult to audit/monitor

### Option 2: Full Registry Migration

Migrate all commands to UnifiedCommandRegistry, removing ViewModel commands.

**Pros:**
- Single source of truth
- Built-in health tracking
- Centralized keyboard shortcuts
- Easy to audit

**Cons:**
- Massive migration effort
- Fighting WinUI conventions
- Complex bindings for simple cases
- ViewModel pattern violation

### Option 3: Hybrid Architecture (Selected)

Keep both systems with clear responsibilities:
- **UnifiedCommandRegistry** for global, cross-cutting, and routed commands
- **ViewModel ICommands** for panel-specific, view-local commands

**Pros:**
- Leverages existing infrastructure
- Incremental migration possible
- Follows platform conventions for local commands
- Centralized tracking for important commands

**Cons:**
- Two systems to maintain
- Clear guidelines needed
- Potential confusion about where to add new commands

## Decision

**Option 3: Hybrid Architecture** with the following responsibilities:

### UnifiedCommandRegistry Scope

Commands that are:
- **Routed from multiple UI elements** (e.g., menu + toolbar + shortcut)
- **Global in scope** (e.g., file operations, navigation, app settings)
- **Need health monitoring** (critical user-facing actions)
- **Have keyboard shortcuts** (centralized shortcut management)
- **Cross-cutting** (affect multiple panels or app state)

```csharp
// Example: Registered in command handlers
_registry.Register(new CommandDescriptor
{
    Id = "file.save",
    Title = "Save Project",
    KeyboardShortcut = "Ctrl+S",
    Category = CommandCategory.File,
    Handler = async (ctx, ct) => await SaveProjectAsync()
});
```

### ViewModel ICommand Scope

Commands that are:
- **Panel-specific** (e.g., "Add Layer" in timeline panel)
- **View-local** (no need for routing or shortcuts)
- **Simple property mutations** (toggle states, local validation)
- **Part of data binding** (ListView selections, form inputs)

```csharp
// Example: ViewModel command
public ICommand AddLayerCommand { get; }
public StudioViewModel()
{
    AddLayerCommand = new RelayCommand(AddLayer, CanAddLayer);
}
```

### Integration Points

#### 1. CommandRouter
Central hub for executing registry commands from any UI element:

```csharp
public class CommandRouter
{
    public void WireButton(ButtonBase button, string commandId);
    public void WireMenuItem(MenuFlyoutItem item, string commandId);
    public Task ExecuteAsync(string commandId, object? context = null);
}
```

#### 2. Navigation Routing
All navigation buttons route through CommandRouter to registry:

```csharp
private void NavStudio_Click(object sender, RoutedEventArgs e)
{
    ExecuteNavCommand("nav.studio", "Studio");
}

private void ExecuteNavCommand(string commandId, string fallbackPanel)
{
    if (_commandRouter != null)
        _commandRouter.ExecuteFireAndForget(commandId);
    else
        SwitchToPanel(fallbackPanel);  // Graceful fallback
}
```

#### 3. Menu Item Creation
Menu items auto-wire to registry with shortcuts:

```csharp
private MenuFlyoutItem CreateCommandMenuItem(string text, string commandId, string? shortcut = null)
{
    var item = new MenuFlyoutItem { Text = text };
    if (shortcut != null) item.KeyboardAcceleratorTextOverride = shortcut;
    _commandRouter?.WireMenuItem(item, commandId);
    return item;
}
```

### Command Registration Structure

Commands organized by handler type:

| Handler | Responsibility | Examples |
|---------|---------------|----------|
| `NavigationOperationsHandler` | Panel navigation | nav.studio, nav.profiles, nav.settings |
| `FileOperationsHandler` | File I/O | file.new, file.open, file.save, file.import |
| `PlaybackOperationsHandler` | Audio playback | playback.play, playback.record, playback.stop |
| `EditOperationsHandler` | Editing commands | edit.undo, edit.redo, edit.cut, edit.copy |

### Health Monitoring

The UnifiedCommandRegistry provides built-in health tracking:

```csharp
public record CommandState
{
    public CommandStatus Status { get; set; }  // Working, Broken, Unknown
    public int SuccessCount { get; set; }
    public int FailureCount { get; set; }
    public DateTime? LastExecuted { get; set; }
    public string? LastError { get; set; }
}
```

Exposed in the Diagnostics panel for real-time monitoring.

### Keyboard Shortcut System

Centralized in `KeyboardShortcutService`:

```csharp
// Registration happens automatically from command descriptors
_keyboardService.RegisterFromRegistry(_commandRegistry);

// Processing in MainWindow
private void MainWindow_KeyDown(object sender, KeyRoutedEventArgs e)
{
    _keyboardService.ProcessKeyDown(e);
}
```

## Implementation Status

| Component | Status | Evidence |
|-----------|--------|----------|
| UnifiedCommandRegistry | ✅ Complete | `Services/UnifiedCommandRegistry.cs` |
| CommandRouter | ✅ Complete | `Services/CommandRouter.cs` |
| Command Handlers | ✅ Complete | `Commands/*Handler.cs` |
| Navigation Wiring | ✅ Complete | `MainWindow.xaml.cs` NavX_Click methods |
| Menu Item Wiring | ✅ Complete | `MainWindow.xaml.cs` CreateCommandMenuItem |
| Health Dashboard | ✅ Complete | `DiagnosticsView.xaml.cs` Commands tab |
| Integration Tests | ✅ Complete | `CommandSystemIntegrationTests.cs` |

## Consequences

### Positive

- **Single routing path** for global commands via CommandRouter
- **Health visibility** through diagnostics dashboard
- **Consistent shortcuts** via centralized registration
- **Graceful degradation** with fallback handlers
- **Testable** via mock command registry
- **Auditable** with command system audit document

### Negative

- Two command systems require clear guidelines
- Migration incomplete for some ViewModel commands
- Learning curve for new developers

### Neutral

- Existing ViewModel commands remain untouched unless migration needed
- Future commands should follow the decision matrix below

## Decision Matrix for New Commands

| Criterion | Use Registry | Use ViewModel |
|-----------|--------------|---------------|
| Has keyboard shortcut | ✅ | |
| Appears in menu | ✅ | |
| Cross-panel action | ✅ | |
| Needs health tracking | ✅ | |
| Panel-local only | | ✅ |
| Data binding target | | ✅ |
| Simple property toggle | | ✅ |

## References

- `docs/architecture/COMMAND_SYSTEM_AUDIT.md` - Full command inventory
- `src/VoiceStudio.App/Services/UnifiedCommandRegistry.cs`
- `src/VoiceStudio.App/Services/CommandRouter.cs`
- `src/VoiceStudio.App/Commands/` - Handler implementations
- `src/VoiceStudio.App.Tests/Commands/CommandSystemIntegrationTests.cs`
- ADR-008: Architecture Patterns
