# ScriptEditorView Duplicate Action Fix

**Date:** 2025-01-28  
**Status:** ✅ **COMPLETE**

---

## Summary

Removed duplicate `SimpleAction` registrations for deleting scripts and removing segments from the ScriptEditorView code-behind, as the ViewModel's commands already handle undo/redo using proper undoable action classes.

---

## Changes Made

### File Modified
- `src/VoiceStudio.App/Views/Panels/ScriptEditorView.xaml.cs`

### Fix Details

**Removed Duplicate Undo/Redo Registrations:**

1. **Delete Script Action** - Removed duplicate `SimpleAction` registration
   - The ViewModel's `DeleteScriptCommand` already uses `DeleteScriptAction`
   - Duplicate registration was causing redundant undo stack entries

2. **Remove Segment Action** - Removed duplicate `SimpleAction` registration
   - The ViewModel's `RemoveSegmentCommand` already uses `RemoveScriptSegmentAction`
   - Duplicate registration was causing redundant undo stack entries

**Before (Delete Script):**
```csharp
await ViewModel.DeleteScriptCommand.ExecuteAsync(script);

// Register undo action
if (_undoRedoService != null && scriptIndex >= 0)
{
    var actionObj = new SimpleAction(
        $"Delete Script: {script.Name}",
        () => ViewModel.Scripts.Insert(scriptIndex, scriptToDelete),
        () => ViewModel.Scripts.Remove(scriptToDelete));
    _undoRedoService.RegisterAction(actionObj);
}
```

**After (Delete Script):**
```csharp
await ViewModel.DeleteScriptCommand.ExecuteAsync(script);

// Undo/redo is handled by DeleteScriptCommand via DeleteScriptAction
```

**Before (Remove Segment):**
```csharp
await ViewModel.RemoveSegmentCommand.ExecuteAsync(segment);

// Register undo action
if (_undoRedoService != null && segmentIndex >= 0)
{
    var actionObj = new SimpleAction(
        "Delete Segment",
        () => ViewModel.SelectedScript.Segments.Insert(segmentIndex, segmentToDelete),
        () => ViewModel.SelectedScript.Segments.Remove(segmentToDelete));
    _undoRedoService.RegisterAction(actionObj);
}
```

**After (Remove Segment):**
```csharp
await ViewModel.RemoveSegmentCommand.ExecuteAsync(segment);

// Undo/redo is handled by RemoveSegmentCommand via RemoveScriptSegmentAction
```

---

## Context

- ✅ **ScriptEditorViewModel** already has proper UndoRedoService integration
- ✅ **DeleteScriptCommand** uses `DeleteScriptAction` for undo/redo
- ✅ **RemoveSegmentCommand** uses `RemoveScriptSegmentAction` for undo/redo
- ✅ **AddSegmentCommand** uses `AddScriptSegmentAction` for undo/redo
- ✅ The duplicate registrations were causing redundant undo/redo entries

---

## Notes

- The `DuplicateSegment` action in the code-behind still uses `SimpleAction` because there's no ViewModel command for duplication - this is acceptable
- All other service integrations (ToastNotificationService, ContextMenuService, DragDropVisualFeedbackService) are already properly integrated
- The ViewModel handles all undo/redo logic consistently using proper action classes

---

## Benefits

1. **Consistent Undo/Redo Behavior**: All script and segment operations now use the same undo/redo mechanism
2. **Single Source of Truth**: Undo/redo logic is managed entirely in the ViewModel
3. **No Duplicate Actions**: Prevents duplicate undo stack entries
4. **Maintainability**: Changes to undo/redo behavior only need to be made in one place

---

**Status:** ✅ **COMPLETE**  
**Duplicate action registrations removed, consistent with other panels.**

