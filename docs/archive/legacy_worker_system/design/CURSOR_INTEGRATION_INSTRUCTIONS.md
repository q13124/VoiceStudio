# Cursor Integration Instructions
## How to Integrate New UI with Existing VoiceStudio Code

**Purpose:** Clear instructions for Cursor to integrate the new UI design with existing code while preserving all functionality.

---

## 🎯 PRIMARY DIRECTIVE

**INTEGRATE, DON'T REPLACE**

The new UI design should be **integrated** with existing VoiceStudio code, not replace it. All existing functionality must be preserved.

---

## 📋 STEP-BY-STEP INTEGRATION PROCESS

### Phase 0: Pre-Integration Audit (Overseer)

**Before making ANY changes:**

1. **Inventory Existing Code**
   ```
   Command: "Create a complete inventory of all existing VoiceStudio files:
   - List all .xaml files with full paths
   - List all .cs files with full paths  
   - Document all existing ViewModels and their properties
   - Document all existing services and their methods
   - Document all existing data bindings
   - Document all existing event handlers
   - Save to PRESERVATION_INVENTORY.md"
   ```

2. **Identify Existing Functionality**
   - What panels exist?
   - What features are implemented?
   - What data bindings are active?
   - What event handlers are wired?
   - What services are registered?

3. **Create Preservation Checklist**
   - Use `PRESERVATION_CHECKLIST.md` as template
   - Document every existing feature
   - Document every existing binding
   - Document every existing handler

---

### Phase 1: Foundation Integration (Worker 1)

**Tasks:**
1. Merge DesignTokens.xaml (ADD new, KEEP existing)
2. Update MainWindow.xaml (ADD new structure, PRESERVE existing)
3. Preserve App.xaml.cs initialization
4. Verify compilation

**Integration Pattern:**
```xml
<!-- DesignTokens.xaml - ADD new tokens, KEEP existing -->
<!-- Existing tokens -->
<Color x:Key="VSQ.Existing.Color">#FF123456</Color>

<!-- NEW: Add these tokens (don't remove existing) -->
<Color x:Key="VSQ.Background.Darker">#FF0A0F15</Color>
<Color x:Key="VSQ.Background.Dark">#FF121A24</Color>
<!-- ... more new tokens ... -->
```

```xml
<!-- MainWindow.xaml - ADD new structure, PRESERVE existing -->
<Window>
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto"/>   <!-- NEW: Command Deck -->
            <RowDefinition Height="*"/>      <!-- EXISTING: Main content -->
            <RowDefinition Height="Auto"/>   <!-- NEW: Status Bar -->
        </Grid.RowDefinitions>
        
        <!-- NEW: Top Command Deck -->
        <Grid Grid.Row="0">
            <!-- New menu and toolbar -->
        </Grid>
        
        <!-- EXISTING: Preserve existing main content -->
        <Grid Grid.Row="1">
            <!-- Keep ALL existing controls, add new PanelHosts alongside -->
            <!-- Existing named controls preserved -->
            <!-- Existing event handlers preserved -->
        </Grid>
        
        <!-- NEW: Status Bar -->
        <Border Grid.Row="2">
            <!-- New status bar -->
        </Border>
    </Grid>
</Window>
```

**Verification:**
- [ ] Existing MainWindow content preserved
- [ ] New structure added
- [ ] All existing controls still accessible
- [ ] Compilation successful

---

### Phase 2-4: Panel Integration (Workers 2-4)

**For Each Panel (ProfilesView, TimelineView, etc.):**

**Step 1: Read Existing**
```
Command: "Read [PanelName]View.xaml completely. Document:
- All x:Name attributes
- All data bindings
- All event handlers
- All Grid/StackPanel structures
- All existing functionality"
```

**Step 2: Update Structure**
```xml
<!-- [PanelName]View.xaml - PRESERVE existing, ADD new -->
<UserControl>
    <Grid>
        <Grid.RowDefinitions>
            <RowDefinition Height="32"/>   <!-- NEW: Header/Tabs -->
            <RowDefinition Height="*"/>     <!-- EXISTING: Main content -->
        </Grid.RowDefinitions>
        
        <!-- NEW: Add new header/tabs -->
        <StackPanel Grid.Row="0">
            <!-- New tabs or header -->
        </StackPanel>
        
        <!-- EXISTING: Preserve existing content -->
        <Grid Grid.Row="1">
            <!-- Keep ALL existing controls -->
            <!-- Preserve ALL existing bindings -->
            <!-- Preserve ALL existing handlers -->
            
            <!-- NEW: Add new features alongside -->
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="*"/>      <!-- EXISTING: List -->
                <ColumnDefinition Width="260"/>    <!-- NEW: Details -->
            </Grid.ColumnDefinitions>
            
            <!-- EXISTING: Preserve existing ListView -->
            <ListView Grid.Column="0"
                     x:Name="ExistingListView"
                     ItemsSource="{Binding ExistingItems}"
                     SelectionChanged="ExistingListView_SelectionChanged"/>
            
            <!-- NEW: Add detail panel -->
            <Border Grid.Column="1">
                <!-- New detail inspector -->
            </Border>
        </Grid>
    </Grid>
</UserControl>
```

**Step 3: Update ViewModel**
```csharp
// [PanelName]ViewModel.cs - PRESERVE existing, ADD new
public class [PanelName]ViewModel : INotifyPropertyChanged, IPanelView  // NEW: Add interface
{
    // EXISTING: Preserve all existing properties
    public ObservableCollection<Item> ExistingItems { get; set; }  // PRESERVE
    public Item SelectedItem { get; set; }  // PRESERVE
    // ... all existing properties preserved ...
    
    // NEW: Add IPanelView properties
    public string PanelId => "[panelname]";
    public string DisplayName => "[Panel Name]";
    public PanelRegion Region => PanelRegion.[Region];
    
    // EXISTING: Preserve all existing methods
    public void ExistingMethod() { /* PRESERVE */ }
    
    // NEW: Add new methods alongside
    public void NewMethod() { /* NEW */ }
}
```

**Verification:**
- [ ] Existing controls preserved
- [ ] Existing bindings work
- [ ] Existing handlers work
- [ ] New features work
- [ ] Compilation successful

---

### Phase 5: Advanced Controls (Worker 5)

**PanelStack Integration:**
- PanelStack.xaml is NEW file (no conflicts)
- Integrate into PanelHost (PanelHost supports both single panel and PanelStack)
- Test with existing panels

**CommandPalette Integration:**
- CommandPalette.xaml is NEW file (no conflicts)
- Add as overlay in MainWindow (doesn't interfere with existing)
- Wire Ctrl+P keyboard shortcut (preserve existing shortcuts)

**Verification:**
- [ ] PanelStack works with existing panels
- [ ] CommandPalette accessible
- [ ] No conflicts with existing controls
- [ ] Existing keyboard shortcuts preserved

---

### Phase 6: Services Integration (Worker 6)

**New Services:**
- WindowHostService.cs (NEW file)
- PanelSettingsStore.cs (NEW file)
- AI services (NEW files)
- AutomationHelper.cs (NEW file)

**Service Registration:**
```csharp
// App.xaml.cs - ADD new services, PRESERVE existing
public App()
{
    this.InitializeComponent();
    
    // EXISTING: Preserve existing initialization
    // ... existing service registration ...
    
    // NEW: Register new services
    ServiceLocator.Register<WindowHostService>(new WindowHostService());
    ServiceLocator.Register<PanelSettingsStore>(new PanelSettingsStore());
    // ... more new services ...
}
```

**Verification:**
- [ ] New services registered
- [ ] Existing services preserved
- [ ] No service conflicts
- [ ] All services functional

---

## 🔍 CONFLICT RESOLUTION

### If New UI Conflicts with Existing

**Scenario 1: Layout Conflict**
- **Solution:** Use Grid.Row/Column to position both
- **Pattern:** Existing in Row 0, new in Row 1

**Scenario 2: Control Name Conflict**
- **Solution:** Rename new control, preserve existing
- **Pattern:** New = "NewButton", Existing = "ExistingButton"

**Scenario 3: Event Handler Conflict**
- **Solution:** Merge handlers or call both
- **Pattern:** `NewButton_Click` calls existing + new logic

**Scenario 4: Data Binding Conflict**
- **Solution:** Use different paths or merge ViewModels
- **Pattern:** Existing = `ViewModel.Property`, New = `ViewModel.NewProperty`

**Scenario 5: Service Conflict**
- **Solution:** Use different service names or namespaces
- **Pattern:** Existing = `ExistingService`, New = `NewService`

---

## ✅ INTEGRATION VERIFICATION

### After Each Phase

**Overseer Must Verify:**

1. **Compilation:**
   - [ ] Solution builds without errors
   - [ ] All design tokens resolve
   - [ ] All references resolve

2. **Functionality:**
   - [ ] All existing features work
   - [ ] All new features work
   - [ ] No runtime errors

3. **Preservation:**
   - [ ] All existing files exist
   - [ ] All existing controls exist
   - [ ] All existing bindings work
   - [ ] All existing handlers work

4. **Structure:**
   - [ ] File structure maintained
   - [ ] MVVM separation maintained
   - [ ] PanelHost system intact

---

## 🎯 SUCCESS CRITERIA

**Integration is successful when:**

- ✅ 100% of existing files preserved
- ✅ 100% of existing functionality works
- ✅ 100% of new features work
- ✅ Zero compilation errors
- ✅ Zero runtime errors
- ✅ Design tokens resolve
- ✅ File structure maintained
- ✅ MVVM separation maintained
- ✅ PanelHost system intact

---

## 📝 QUICK REFERENCE

### Do's ✅
- ✅ Read existing files first
- ✅ Document existing functionality
- ✅ Preserve existing code
- ✅ Add new alongside existing
- ✅ Test after each change
- ✅ Report conflicts immediately

### Don'ts ❌
- ❌ Delete existing files
- ❌ Remove existing functionality
- ❌ Replace existing code
- ❌ Remove existing bindings
- ❌ Remove existing handlers
- ❌ Simplify or collapse

---

## 🚨 EMERGENCY PROTOCOL

**If existing functionality breaks:**

1. **STOP** all workers immediately
2. **REVERT** to last known good state
3. **INVESTIGATE** what broke
4. **FIX** while preserving existing
5. **VERIFY** existing works before proceeding

**Overseer Command:**
```
"EMERGENCY STOP. All workers halt.
Issue: [describe]
Action: Revert to [commit/state]
Investigation: [what to check]
Resolution: [how to fix]"
```

---

## 📚 REFERENCE DOCUMENTS

- `CURSOR_AGENT_GUIDELINES.md` - Complete agent guidelines
- `INTEGRATION_GUIDE.md` - Detailed integration patterns
- `PRESERVATION_CHECKLIST.md` - Preservation checklist
- `OVERSEER_SYSTEM_PROMPT_V2.md` - Overseer prompt
- `WORKER_AGENT_PROMPTS.md` - Individual worker prompts
- `VOICESTUDIO_COMPLETE_IMPLEMENTATION_SPEC.md` - Master spec
- `MEMORY_BANK.md` - Critical information

---

## 💡 KEY REMINDERS

1. **Preservation is Priority #1**
2. **Integration = Merging, not Replacing**
3. **When in doubt, preserve**
4. **Test existing after each change**
5. **Quality and stability > speed**

**Remember:** The goal is to have BOTH existing functionality AND new UI working together seamlessly.

