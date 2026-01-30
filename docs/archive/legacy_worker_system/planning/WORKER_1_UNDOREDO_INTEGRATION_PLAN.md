# Worker 1: UndoRedoService Integration Plan

**Date:** 2025-01-27  
**Status:** 📋 **PLANNING**  
**Task:** TASK-W1-001 - Integrate UndoRedoService into all editable panels

---

## 📊 **Current State**

### **✅ Service Infrastructure - COMPLETE**
- ✅ `UndoRedoService` class exists (`src/VoiceStudio.App/Services/UndoRedoService.cs`)
- ✅ `IUndoableAction` interface defined
- ✅ Service registered in `ServiceProvider`
- ✅ `UndoRedoIndicator` control exists and subscribes to service
- ✅ Keyboard shortcuts registered in `MainWindow` (Ctrl+Z, Ctrl+Y) - **NOT YET WIRED**

### **⚠️ Integration Status**
- ✅ `TimelineView.xaml.cs` has `UndoRedoService` initialized (line 43)
- ⏳ **No actions are being registered** yet
- ⏳ **Keyboard shortcuts not wired** to service methods

---

## 🎯 **Integration Strategy**

### **Phase 1: Wire Up Global Undo/Redo (Quick Win)** ✅ **READY**

**Files to Modify:**
1. `src/VoiceStudio.App/MainWindow.xaml.cs`
   - Wire `edit.undo` keyboard shortcut to `UndoRedoService.Undo()`
   - Wire `edit.redo` keyboard shortcut to `UndoRedoService.Redo()`

**Implementation:**
```csharp
// In RegisterKeyboardShortcuts()
_keyboardShortcutService.RegisterShortcut(
    "edit.undo",
    VirtualKey.Z,
    VirtualKeyModifiers.Control,
    () => {
        var undoService = ServiceProvider.GetUndoRedoService();
        if (undoService.CanUndo)
        {
            undoService.Undo();
        }
    },
    "Undo");
```

---

### **Phase 2: Integrate into Core Panels (Incremental)**

**Priority Panels for Undo/Redo:**
1. **TimelineViewModel** - High Priority
   - Track creation/deletion
   - Clip creation/deletion/moving
   - Timeline edits

2. **ProfilesViewModel** - Medium Priority
   - Profile creation/deletion
   - Profile property edits

3. **LibraryViewModel** - Medium Priority
   - Asset deletion
   - Folder creation/deletion

4. **EffectsMixerView** - Low Priority
   - Effect chain modifications
   - Mixer parameter changes

---

## 📋 **Implementation Pattern for Each Panel**

### **Step 1: Add Service Reference**
```csharp
private readonly UndoRedoService? _undoRedoService;

public ViewModel(...)
{
    // ...
    try
    {
        _undoRedoService = ServiceProvider.GetUndoRedoService();
    }
    catch
    {
        _undoRedoService = null;
    }
}
```

### **Step 2: Create Undoable Action Classes**

For each operation, create an action class:

```csharp
private class CreateProfileAction : IUndoableAction
{
    private readonly ProfilesViewModel _viewModel;
    private readonly VoiceProfile _profile;
    
    public string ActionName => $"Create Profile '{_profile.Name}'";
    
    public CreateProfileAction(ProfilesViewModel viewModel, VoiceProfile profile)
    {
        _viewModel = viewModel;
        _profile = profile;
    }
    
    public void Undo()
    {
        // Remove the profile
        _viewModel.Profiles.Remove(_profile);
    }
    
    public void Redo()
    {
        // Re-add the profile
        _viewModel.Profiles.Add(_profile);
    }
}
```

### **Step 3: Register Actions After Operations**

```csharp
private async Task CreateProfileAsync(string? name)
{
    // ... existing code ...
    var profile = await _backendClient.CreateProfileAsync(name!);
    Profiles.Add(profile);
    
    // Register undo action
    if (_undoRedoService != null)
    {
        _undoRedoService.RegisterAction(new CreateProfileAction(this, profile));
    }
}
```

---

## 🎯 **Recommended Approach**

### **Option A: Incremental Integration (Recommended)**
1. ✅ Wire up global keyboard shortcuts first (quick win)
2. Integrate into TimelineViewModel (highest impact)
3. Then integrate into other panels incrementally

### **Option B: Comprehensive Integration**
- Implement all undoable actions across all panels at once
- More complex, but complete solution

---

## 📋 **Example: TimelineViewModel Integration**

### **Undoable Actions Needed:**
1. `CreateTrackAction` - Undo track creation
2. `DeleteTrackAction` - Undo track deletion
3. `CreateClipAction` - Undo clip creation
4. `DeleteClipAction` - Undo clip deletion
5. `MoveClipAction` - Undo clip movement

### **Integration Points:**
- `AddTrackAsync()` → Register `CreateTrackAction`
- `DeleteSelectedClipsAsync()` → Register `DeleteClipAction` (batch)
- `AddClipToTrackAsync()` → Register `CreateClipAction`

---

## ⚠️ **Considerations**

### **Backend Operations:**
- Some operations require backend API calls (create profile, delete asset)
- Undo actions must either:
  - **Option 1:** Keep local state only (UI-only undo)
  - **Option 2:** Call backend to reverse operations (more complex)
  - **Recommendation:** Start with Option 1 for simplicity

### **Batch Operations:**
- Multi-select operations (batch delete) should register a single action that undoes all operations
- Example: `BatchDeleteClipsAction` contains list of clips to restore

---

## ✅ **Next Steps**

1. **Immediate:** Wire up keyboard shortcuts in MainWindow
2. **Next:** Integrate undo/redo into TimelineViewModel
3. **Then:** Integrate into ProfilesViewModel
4. **Finally:** Integrate into other panels as needed

---

**Last Updated:** 2025-01-27  
**Status:** 📋 **PLANNING - Ready for Implementation**

