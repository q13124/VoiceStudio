# Command Binding Guide

> **GAP-B18**: Standardizing command binding patterns across VoiceStudio
> **Last Updated**: 2026-02-16

## Overview

VoiceStudio uses MVVM pattern with WinUI 3. This guide defines the preferred command binding patterns to ensure consistency and maintainability.

## Binding Pattern Priority

### 1. PREFERRED: x:Bind with ViewModel Command

Use `x:Bind` to bind directly to ViewModel commands. This is the recommended pattern for all new development.

```xml
<!-- PREFERRED: x:Bind to ViewModel command -->
<Button Content="Save" Command="{x:Bind ViewModel.SaveCommand}"/>

<!-- With parameter -->
<Button Content="Delete"
        Command="{x:Bind ViewModel.DeleteCommand}"
        CommandParameter="{x:Bind SelectedItem}"/>

<!-- Async command with loading state -->
<Button Content="Generate"
        Command="{x:Bind ViewModel.GenerateCommand}"
        IsEnabled="{x:Bind ViewModel.IsNotBusy, Mode=OneWay}"/>
```

**Advantages:**
- Compile-time type checking
- Better performance than `{Binding}`
- IntelliSense support in XAML
- Clear ownership and testability

### 2. ACCEPTABLE: ICommand via Registry

Use registry-based commands for cross-panel or application-wide actions.

```xml
<!-- ACCEPTABLE: Registry-based command -->
<Button Content="Export"
        Command="{x:Bind Services.CommandRegistry.GetCommand('export')}"/>

<!-- MenuFlyout items -->
<MenuFlyoutItem Text="New Project"
                Command="{x:Bind Services.CommandRegistry.GetCommand('file.new')}"/>
```

**When to use:**
- Global application commands (File, Edit, View menus)
- Commands shared across multiple panels
- Keyboard shortcut actions

### 3. DEPRECATED: Click Handlers

Direct Click handlers are deprecated and should be migrated.

```xml
<!-- DEPRECATED: Direct click handler -->
<Button Content="Legacy" Click="OnLegacyClick"/>
```

**Why deprecated:**
- No CanExecute support
- Harder to test
- Tightly couples View to behavior
- Cannot be bound to keyboard shortcuts

---

## Migration Strategy

### Step 1: Identify Click Handlers

Use the Button Pattern Audit (`docs/architecture/BUTTON_PATTERN_AUDIT.md`) to identify handlers.

### Step 2: Create ViewModel Commands

```csharp
// Before (Click handler in code-behind)
private async void OnExportClick(object sender, RoutedEventArgs e)
{
    await ExportAsync();
}

// After (Command in ViewModel)
public IAsyncRelayCommand ExportCommand { get; }

public MyViewModel(IViewModelContext context) : base(context)
{
    ExportCommand = new AsyncRelayCommand(ExportAsync, CanExport);
}

private bool CanExport() => SelectedItem != null && !IsBusy;

private async Task ExportAsync()
{
    // Export logic
}
```

### Step 3: Update XAML Binding

```xml
<!-- Before -->
<Button Content="Export" Click="OnExportClick"/>

<!-- After -->
<Button Content="Export" Command="{x:Bind ViewModel.ExportCommand}"/>
```

### Step 4: Remove Event Handler

Delete the Click handler from code-behind after migration.

### Step 5: Register for Global Access (if needed)

```csharp
// In AppServices or CommandRegistry initialization
commandRegistry.Register("export", viewModel.ExportCommand);
```

---

## Migration Priority Matrix

Based on panel usage frequency (from BUTTON_PATTERN_AUDIT.md):

| Panel | Click Handlers | Priority | Sprint Target |
|-------|----------------|----------|---------------|
| Timeline | 24 | P0 | Sprint 3 |
| Effects | 18 | P1 | Sprint 3-4 |
| Synthesis | 15 | P1 | Sprint 4 |
| Library | 12 | P2 | Sprint 4-5 |
| Profiles | 8 | P2 | Sprint 5 |
| Other | 21 | P3 | Future |

---

## Command Types

### AsyncRelayCommand

For async operations (API calls, file I/O, synthesis):

```csharp
public IAsyncRelayCommand GenerateCommand { get; }

GenerateCommand = new AsyncRelayCommand(
    GenerateAsync,
    () => CanGenerate,
    allowConcurrentExecutions: false
);
```

### RelayCommand

For synchronous operations:

```csharp
public IRelayCommand SelectAllCommand { get; }

SelectAllCommand = new RelayCommand(
    SelectAll,
    () => HasItems
);
```

### RelayCommand<T>

For commands with parameters:

```csharp
public IRelayCommand<VoiceProfile> DeleteProfileCommand { get; }

DeleteProfileCommand = new RelayCommand<VoiceProfile>(
    profile => DeleteProfile(profile),
    profile => profile != null && !profile.IsDefault
);
```

### EnhancedAsyncRelayCommand

For commands with CancellationToken support (GAP-I15):

```csharp
public IAsyncRelayCommand<string> CreateCommand { get; }

// EnhancedAsyncRelayCommand passes CancellationToken automatically
CreateCommand = new EnhancedAsyncRelayCommand<string>(
    async (name, ct) => await CreateAsync(name, ct)
);
```

---

## CanExecute Patterns

### Single Condition

```csharp
SaveCommand = new RelayCommand(Save, () => IsDirty);
```

### Multiple Conditions (AND)

```csharp
ExportCommand = new RelayCommand(
    Export,
    () => HasSelection && !IsBusy && IsConnected
);
```

### Property-Based (Automatic Refresh)

Use `[RelayCommand]` source generator with `CanExecute` method:

```csharp
[RelayCommand(CanExecute = nameof(CanSave))]
private async Task SaveAsync()
{
    // ...
}

private bool CanSave() => IsDirty && !IsBusy;
```

### Notify CanExecuteChanged

```csharp
// After state change
SaveCommand.NotifyCanExecuteChanged();

// Or use ObservableProperty with automatic notification
[ObservableProperty]
[NotifyCanExecuteChangedFor(nameof(SaveCommand))]
private bool _isDirty;
```

---

## Command Naming Conventions

| Pattern | Example | Use Case |
|---------|---------|----------|
| `{Verb}Command` | `SaveCommand` | Simple actions |
| `{Verb}{Noun}Command` | `DeleteProfileCommand` | Actions on specific entities |
| `Toggle{Property}Command` | `ToggleMuteCommand` | Boolean toggles |
| `Navigate{Target}Command` | `NavigateSettingsCommand` | Navigation actions |
| `Show{Dialog}Command` | `ShowAboutDialogCommand` | Dialog display |

---

## Testing Commands

### Unit Test Pattern

```csharp
[TestMethod]
public async Task SaveCommand_WhenDirty_ExecutesSave()
{
    // Arrange
    var vm = new MyViewModel(...);
    vm.IsDirty = true;

    // Act
    await vm.SaveCommand.ExecuteAsync(null);

    // Assert
    Assert.IsFalse(vm.IsDirty);
    _mockService.Verify(s => s.SaveAsync(It.IsAny<Model>()), Times.Once);
}

[TestMethod]
public void SaveCommand_WhenNotDirty_CannotExecute()
{
    // Arrange
    var vm = new MyViewModel(...);
    vm.IsDirty = false;

    // Assert
    Assert.IsFalse(vm.SaveCommand.CanExecute(null));
}
```

---

## Anti-Patterns to Avoid

### ❌ Fire-and-forget without error handling

```csharp
// BAD: Swallows exceptions
private void OnClick(object s, RoutedEventArgs e)
{
    _ = DoSomethingAsync(); // No error handling!
}
```

### ❌ Mixing Click and Command on same button

```xml
<!-- BAD: Confusing behavior -->
<Button Command="{x:Bind SaveCommand}" Click="OnSaveClick"/>
```

### ❌ Complex logic in CanExecute

```csharp
// BAD: Too complex, hard to test
private bool CanProcess() =>
    Items.Any(i => i.State == "ready" && !i.IsLocked && HasPermission(i.Owner));
```

### ❌ CancellationToken.None in async commands

```csharp
// BAD: See GAP-I15 - always propagate tokens
CreateCommand = new AsyncRelayCommand(async () =>
    await CreateAsync(CancellationToken.None));
```

---

## Checklist for New Commands

- [ ] Command defined in ViewModel (not code-behind)
- [ ] Using appropriate command type (Async vs Sync)
- [ ] CanExecute condition implemented
- [ ] CancellationToken propagated (for async)
- [ ] Error handling with try/catch
- [ ] Unit tests written
- [ ] XAML uses `x:Bind` (not `{Binding}`)
- [ ] Keyboard shortcut registered (if applicable)

---

## Sprint 3 Migration Progress (GAP-B18)

### Completed Migrations

| File | Handler | Migration Type |
|------|---------|----------------|
| PluginGalleryView.xaml | RefreshButton_Click | `Command="{x:Bind ViewModel.RefreshCommand}"` |
| PluginGalleryView.xaml | CheckUpdatesButton_Click | `Command="{x:Bind ViewModel.CheckForUpdatesCommand}"` |
| PluginGalleryView.xaml | PrevPageButton_Click | `Command="{x:Bind ViewModel.PreviousPageCommand}"` |
| PluginGalleryView.xaml | NextPageButton_Click | `Command="{x:Bind ViewModel.NextPageCommand}"` |
| PluginGalleryView.xaml | CancelInstall_Click | `Command="{x:Bind ViewModel.CancelInstallCommand}"` |
| ProfilesView.xaml | BatchExport_Click | `Command="{x:Bind ViewModel.ExportSelectedCommand}"` |
| PluginCard.xaml | ActionButton_Click | `Command="{x:Bind ActionCommand}" CommandParameter="{x:Bind Plugin}"` |

### CanExecute Enhancements

The following ViewModel commands were enhanced with proper `CanExecute` support:

- `PluginGalleryViewModel.NextPageCommand` - Added `CanNextPage()` predicate
- `PluginGalleryViewModel.PreviousPageCommand` - Added `CanPreviousPage()` predicate
- `ProfilesViewModel.ExportSelectedCommand` - Added `() => SelectedCount > 0` predicate

### Handlers Evaluated but Retained

| Category | Count | Reason |
|----------|-------|--------|
| Help buttons | 20+ | Acceptable per audit (pure UI logic) |
| Dialog-dependent | 15+ | Requires UI infrastructure (ContentDialog, FilePicker) |
| Control-internal (zoom/pan) | 8+ | Control-specific behavior |
| Unbound UI controls | 5+ | Would require TwoWay bindings first |

### Future Migration Candidates

These handlers could be migrated with additional ViewModel refactoring:

1. **ProfilesView.CreateProfileButton_Click** - Requires dialog abstraction
2. **MacroView.NewMacroButton_Click** - Requires dialog abstraction
3. **PluginGalleryView.ClearFilters_Click** - Requires TwoWay bindings on filter controls
4. **ThemeEditorView save/load handlers** - Requires file picker abstraction

---

## Related Documentation

- [ASYNC_PATTERNS.md](./ASYNC_PATTERNS.md) - Async patterns and cancellation
- [BUTTON_PATTERN_AUDIT.md](../architecture/BUTTON_PATTERN_AUDIT.md) - Current state audit
- [CONCURRENCY_GUIDE.md](../architecture/CONCURRENCY_GUIDE.md) - Threading and locks
