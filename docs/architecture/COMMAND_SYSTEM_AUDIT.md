# VoiceStudio Command System Audit

**Date**: 2026-02-08  
**Status**: Complete

## Executive Summary

VoiceStudio has three command systems that operate in parallel:

1. **ViewModel Commands (MVVM)**: ~400+ ICommand properties across 67 ViewModels
2. **Unified Command Registry**: 33+ global commands in 5 handlers
3. **Click Handlers**: 100+ event handlers in Views and Controls

## Command Source Statistics

| Source | Count | Pattern | Location |
|--------|-------|---------|----------|
| ViewModel ICommand | 400+ | `public IAsyncRelayCommand Name { get; }` | `ViewModels/*.cs` |
| Registry Commands | 33 | `_registry.Register(descriptor, handler, canExecute)` | `Commands/*.cs` |
| Click Handlers | 100+ | `private void Name_Click(object, RoutedEventArgs)` | `Views/**/*.cs`, `Controls/**/*.cs` |

## Registry Command Inventory

### FileOperationsHandler (7 commands)
- `file.new` - Create new project (Ctrl+N)
- `file.open` - Open existing project (Ctrl+O)
- `file.save` - Save current project (Ctrl+S)
- `file.saveAs` - Save project as (Ctrl+Shift+S)
- `file.import` - Import audio files (Ctrl+I)
- `file.export` - Export audio (Ctrl+E)
- `file.close` - Close project (Ctrl+W)

### ProfileOperationsHandler (7 commands)
- `profile.create` - Create new voice profile
- `profile.edit` - Edit selected profile
- `profile.delete` - Delete selected profile
- `profile.save` - Save profile changes
- `profile.load` - Load profile
- `profile.clone` - Clone profile
- `profile.select` - Select profile

### PlaybackOperationsHandler (10 commands)
- `playback.play` - Start playback (Space)
- `playback.pause` - Pause playback
- `playback.toggle` - Toggle play/pause
- `playback.stop` - Stop playback
- `playback.record` - Start/stop recording (R)
- `playback.rewind` - Rewind (Home)
- `playback.forward` - Fast forward (End)
- `playback.stepBack` - Step back (Left)
- `playback.stepForward` - Step forward (Right)
- `playback.seek` - Seek to position

### NavigationHandler (4+ commands)
- `nav.studio` - Navigate to Studio/Timeline (Ctrl+1)
- `nav.profiles` - Navigate to Profiles (Ctrl+2)
- `nav.settings` - Navigate to Settings (Ctrl+,)
- `nav.back` - Go back (Alt+Left)
- `nav.forward` - Go forward (Alt+Right) [stub]

### SettingsOperationsHandler (5 commands)
- `settings.save` - Save settings
- `settings.reset` - Reset to defaults
- `settings.export` - Export settings
- `settings.import` - Import settings
- `settings.theme` - Toggle theme

## Duplication Analysis

### Navigation Commands vs Click Handlers

| Button | Click Handler | Registry Command | Status |
|--------|--------------|------------------|--------|
| NavStudio | `NavStudio_Click` | `nav.studio` | **DUPLICATE** |
| NavProfiles | `NavProfiles_Click` | `nav.profiles` | **DUPLICATE** |
| NavLibrary | `NavLibrary_Click` | `nav.library` | **DUPLICATE** |
| NavEffects | `NavEffects_Click` | `nav.effects` | **DUPLICATE** |
| NavTrain | `NavTrain_Click` | `nav.train` | **DUPLICATE** |
| NavAnalyze | `NavAnalyze_Click` | `nav.analyze` | **DUPLICATE** |
| NavSettings | `NavSettings_Click` | `nav.settings` | **DUPLICATE** |
| NavLogs | `NavLogs_Click` | `nav.logs` | **DUPLICATE** |

**Recommendation**: Replace Click handlers with `CommandRouter.ExecuteAsync("nav.*")` calls.

### Menu Items vs Registry Commands

Most menu items use inline lambdas that duplicate registry command functionality.

**Recommendation**: Wire menu items to registry commands via `CommandRouter`.

## Architecture Decision

**Hybrid Approach (Recommended)**:

1. **Global/Cross-Cutting Commands** → Unified Registry
   - Navigation commands
   - File operations (new, open, save)
   - Playback controls
   - Settings operations
   - Commands with keyboard shortcuts

2. **Panel-Specific Commands** → ViewModel ICommand
   - Panel-local operations
   - Commands tightly coupled to ViewModel state
   - Commands that need fine-grained CanExecute logic

3. **Legacy Click Handlers** → Migrate to one of above
   - Replace with CommandRouter calls where possible
   - Keep only for truly UI-specific logic (hover effects, focus management)

## Migration Path

### Phase 1: Navigation Unification
1. Update MainWindow Click handlers to use `CommandRouter.ExecuteAsync()`
2. Test keyboard shortcuts continue to work
3. Test UI buttons continue to work

### Phase 2: Menu Unification
1. Wire File menu items to registry
2. Wire View menu items to registry
3. Wire Modules menu items to registry

### Phase 3: Deprecation
1. Mark old Click handlers as legacy
2. Document migration pattern
3. Gradually refactor remaining handlers

## Keyboard Shortcuts (via Registry)

All shortcuts are registered in `UnifiedCommandRegistry` and handled by `KeyboardShortcutService`.

| Shortcut | Command | Description |
|----------|---------|-------------|
| Ctrl+N | file.new | New Project |
| Ctrl+O | file.open | Open Project |
| Ctrl+S | file.save | Save Project |
| Ctrl+Shift+S | file.saveAs | Save As |
| Ctrl+I | file.import | Import Audio |
| Ctrl+E | file.export | Export Audio |
| Ctrl+W | file.close | Close Project |
| Space | playback.toggle | Play/Pause |
| R | playback.record | Record |
| Home | playback.rewind | Rewind |
| End | playback.forward | Fast Forward |
| Ctrl+1 | nav.studio | Studio Panel |
| Ctrl+, | nav.settings | Settings Panel |
| Alt+Left | nav.back | Go Back |
| Alt+Right | nav.forward | Go Forward |

## Conclusion

The command system works but has significant duplication between Click handlers and Registry commands. The recommended approach is:

1. Keep ViewModel commands for panel-specific logic
2. Use Registry for global/cross-cutting commands
3. Wire UI elements (buttons, menus) to Registry via CommandRouter
4. Eliminate duplicate Click handlers
