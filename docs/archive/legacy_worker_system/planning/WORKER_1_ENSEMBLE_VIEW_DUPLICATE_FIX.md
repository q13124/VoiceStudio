# EnsembleSynthesisView Duplicate Action Fix

**Date:** 2025-01-28  
**Status:** ✅ **COMPLETE**

---

## Summary

Removed duplicate `SimpleAction` registration for removing voices from the EnsembleSynthesisView code-behind, as the ViewModel's `RemoveVoiceCommand` already handles undo/redo using the proper `RemoveEnsembleVoiceAction`.

---

## Changes Made

### File Modified
- `src/VoiceStudio.App/Views/Panels/EnsembleSynthesisView.xaml.cs`

### Fix Details

**Removed Duplicate Undo/Redo Registration:**
- The code-behind was manually creating and registering a `SimpleAction` for voice removal
- This duplicated the undo/redo logic already handled by `RemoveVoiceCommand` in the ViewModel
- The ViewModel uses `RemoveEnsembleVoiceAction`, which is the proper undoable action class

**Before:**
```csharp
await ViewModel.RemoveVoiceCommand.ExecuteAsync(voice);

// Register undo action
if (_undoRedoService != null && voiceIndex >= 0)
{
    var actionObj = new SimpleAction(
        "Remove Voice",
        () => ViewModel.Voices.Insert(voiceIndex, voiceToRemove),
        () => ViewModel.Voices.Remove(voiceToRemove));
    _undoRedoService.RegisterAction(actionObj);
}
```

**After:**
```csharp
await ViewModel.RemoveVoiceCommand.ExecuteAsync(voice);

// Undo/redo is handled by RemoveVoiceCommand via RemoveEnsembleVoiceAction
```

---

## Context

- ✅ **EnsembleSynthesisViewModel** already has proper UndoRedoService integration
- ✅ **RemoveVoiceCommand** uses `RemoveEnsembleVoiceAction` for undo/redo
- ✅ **AddVoiceCommand** uses `AddEnsembleVoiceAction` for undo/redo
- ✅ The duplicate registration was causing redundant undo/redo entries

---

## Benefits

1. **Consistent Undo/Redo Behavior**: All voice operations now use the same undo/redo mechanism
2. **Single Source of Truth**: Undo/redo logic is managed entirely in the ViewModel
3. **No Duplicate Actions**: Prevents duplicate undo stack entries
4. **Maintainability**: Changes to undo/redo behavior only need to be made in one place

---

## Notes

- The `DuplicateVoiceAsync` method in the code-behind still uses `SimpleAction` because there's no ViewModel command for duplication - this is acceptable
- Job deletion uses `SimpleAction` in the code-behind because `DeleteJobAsync` doesn't handle undo/redo in the ViewModel (likely intentional since jobs are historical records)
- All other service integrations (ToastNotificationService, ContextMenuService, DragDropVisualFeedbackService, MultiSelectService) are already properly integrated

---

**Status:** ✅ **COMPLETE**  
**Duplicate action registration removed, consistent with other panels.**

