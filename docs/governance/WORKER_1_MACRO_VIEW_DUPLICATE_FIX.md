# MacroView Duplicate Action Fix

**Date:** 2025-01-28  
**Status:** ✅ **COMPLETE**

---

## Summary

Removed duplicate `SimpleAction` registrations for deleting macros and automation curves from the MacroView code-behind, as the ViewModel's commands already handle undo/redo using proper undoable action classes.

---

## Changes Made

### File Modified
- `src/VoiceStudio.App/Views/Panels/MacroView.xaml.cs`

### Fix Details

**Removed Duplicate Undo/Redo Registrations:**

1. **Delete Macro Action** - Removed duplicate `SimpleAction` registration
   - The ViewModel's `DeleteMacroCommand` already uses `DeleteMacroAction`
   - Duplicate registration was causing redundant undo stack entries

2. **Delete Automation Curve Action** - Removed duplicate `SimpleAction` registration
   - The ViewModel's `DeleteAutomationCurveCommand` already uses `DeleteAutomationCurveAction`
   - Duplicate registration was causing redundant undo stack entries

**Before (Delete Macro):**
```csharp
await ViewModel.DeleteMacroCommand.ExecuteAsync(macro.Id);

// Register undo action
if (_undoRedoService != null && macroIndex >= 0)
{
    var actionObj = new SimpleAction(
        $"Delete Macro: {macro.Name}",
        () => ViewModel.Macros.Insert(macroIndex, macroToDelete),
        () => ViewModel.Macros.Remove(macroToDelete));
    _undoRedoService.RegisterAction(actionObj);
}
```

**After (Delete Macro):**
```csharp
await ViewModel.DeleteMacroCommand.ExecuteAsync(macro.Id);

// Undo/redo is handled by DeleteMacroCommand via DeleteMacroAction
```

**Before (Delete Automation Curve):**
```csharp
await ViewModel.DeleteAutomationCurveCommand.ExecuteAsync(curve.Id);

// Register undo action
if (_undoRedoService != null && curveIndex >= 0)
{
    var actionObj = new SimpleAction(
        $"Delete Automation Curve: {curve.Name}",
        () => ViewModel.AutomationCurves.Insert(curveIndex, curveToDelete),
        () => ViewModel.AutomationCurves.Remove(curveToDelete));
    _undoRedoService.RegisterAction(actionObj);
}
```

**After (Delete Automation Curve):**
```csharp
await ViewModel.DeleteAutomationCurveCommand.ExecuteAsync(curve.Id);

// Undo/redo is handled by DeleteAutomationCurveCommand via DeleteAutomationCurveAction
```

---

## Context

- ✅ **MacroViewModel** already has proper UndoRedoService integration
- ✅ **DeleteMacroCommand** uses `DeleteMacroAction` for undo/redo
- ✅ **DeleteAutomationCurveCommand** uses `DeleteAutomationCurveAction` for undo/redo
- ✅ The duplicate registrations were causing redundant undo/redo entries

---

## Notes

- The `DuplicateMacro` and `DuplicateAutomationCurve` actions still use `SimpleAction` because there are no ViewModel commands for duplication - this is acceptable
- All other service integrations (ToastNotificationService, ContextMenuService) are already properly integrated

---

## Benefits

1. **Consistent Undo/Redo Behavior**: All macro and automation curve operations now use the same undo/redo mechanism
2. **Single Source of Truth**: Undo/redo logic is managed entirely in the ViewModel
3. **No Duplicate Actions**: Prevents duplicate undo stack entries
4. **Maintainability**: Changes to undo/redo behavior only need to be made in one place

---

**Status:** ✅ **COMPLETE**  
**Duplicate action registrations removed, consistent with other panels.**

