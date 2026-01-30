# Missing Files Recovery Guide — TASK-0022

**Created**: 2026-01-30  
**Purpose**: Map missing types to files and responsible role/chat instances for recovery from Cursor chat history

---

## Missing Types and Files (from Build Errors)

### Group 1: Core Services Interfaces (Role 4 — Core Platform)

| Missing Type | Expected File Location | Responsible Role | Evidence/Task |
|--------------|------------------------|------------------|---------------|
| **IPanelRegistry** | `src/VoiceStudio.Core/Services/IPanelRegistry.cs` | Role 4 | STATE.md line 71-80, PANEL_REGISTRY_IMPLEMENTATION_COMPLETE.md, docs say "added Register method to IPanelRegistry" |
| **ITelemetryService** | `src/VoiceStudio.Core/Services/ITelemetryService.cs` | Role 4 | TASK-0007 (SLO Dashboard) references "SLO models added to Telemetry.cs" |
| **IViewModelContext** | `src/VoiceStudio.Core/Services/IViewModelContext.cs` OR `src/VoiceStudio.App/ViewModels/IViewModelContext.cs` | Role 3/4 | BaseViewModel references this; likely TD-004 DI migration work |
| **IProjectRepository** | `src/VoiceStudio.Core/Services/IProjectRepository.cs` | Role 4 | ProjectStore references; part of VS-0004/VS-0015 storage work |

**Search in chat instances**: `/role-core-platform` conversations from 2026-01-25 to 2026-01-29

---

### Group 2: Use Cases (Role 3 — UI Engineer, or Role 4)

| Missing Type | Expected File Location | Responsible Role | Evidence/Task |
|--------------|------------------------|------------------|---------------|
| **IProfilesUseCase** | `src/VoiceStudio.App/UseCases/IProfilesUseCase.cs` OR `src/VoiceStudio.Core/Services/IProfilesUseCase.cs` | Role 3/4 | Created in recovery session (Role 2 added this); ProfilesViewModel uses it; in git at App/Core/Services/IProfilesUseCase.cs but namespace wrong |
| **Namespace VoiceStudio.App.UseCases** | `src/VoiceStudio.App/UseCases/` directory | Role 3/4 | ProfilesViewModel imports this; part of DI refactor (TD-004) |

**Note**: IProfilesUseCase EXISTS at `src/VoiceStudio.App/Core/Services/IProfilesUseCase.cs` but referenced as `VoiceStudio.App.UseCases.IProfilesUseCase`. Fix: Either move file or fix namespace references.

**Search in chat instances**: `/role-ui-engineer` OR `/role-core-platform` conversations about ProfilesViewModel, DI migration

---

### Group 3: Persistence Layer (Role 4 — Core Platform)

| Missing Type | Expected File Location | Responsible Role | Evidence/Task |
|--------------|------------------------|------------------|---------------|
| **Namespace Services.Persistence** | `src/VoiceStudio.App/Services/Persistence/` | Role 4 | ProjectStore imports this; VS-0004 (project persistence) work |
| **IProjectRepository** (dup) | In Persistence namespace | Role 4 | Same as Group 1 |
| **ProjectMetadata** | `src/VoiceStudio.Core/Models/ProjectMetadata.cs` | Role 4 | ProjectStore uses this |
| **ProjectData** | `src/VoiceStudio.Core/Models/ProjectData.cs` | Role 4 | ProjectStore uses this |

**Search in chat instances**: `/role-core-platform` conversations about VS-0004, VS-0015, project persistence, storage durability

---

### Group 4: Models (Role 3 — UI, or multiple roles)

| Missing Type | Expected File Location | Responsible Role | Evidence/Task |
|--------------|------------------------|------------------|---------------|
| **DiagnosticsSettings** | `src/VoiceStudio.Core/Models/SettingsData.cs` OR separate file | Role 3/4 | TelemetryService references; part of Settings/diagnostics work |
| **SLO Models** (SLODefinition, etc.) | `src/VoiceStudio.Core/Models/Telemetry.cs` | Role 3 | TASK-0007: "SLO models added to Telemetry.cs" |

**Search in chat instances**: `/role-ui-engineer` for TASK-0007 (SLO Dashboard), SettingsViewModel work

---

### Group 5: Panel Registry Implementation (Role 4)

| Missing Type | Expected File Location | Responsible Role | Evidence/Task |
|--------------|------------------------|------------------|---------------|
| **IPanelRegistry interface** | `src/VoiceStudio.Core/Services/IPanelRegistry.cs` | Role 4 | Docs say created; multiple services depend on it |
| **PanelRegistry class** (implementation) | `src/VoiceStudio.App/Services/PanelRegistry.cs` | Role 4 | Implements IPanelRegistry |

**Search in chat instances**: `/role-core-platform` conversations about panel system, IPanelRegistry

---

## Quick Fix Options (If Chat Recovery Too Complex)

### Option A: Comment Out Missing References (Fast)

Comment out code that references missing types:
- ProfilesViewModel: comment out `IProfilesUseCase` usage
- ServiceProvider: comment out `ITelemetryService`, `IPanelRegistry`, `UseCases` methods
- ProjectStore: comment out Persistence imports
- AdvancedPanelRegistrationService: comment out or stub registry calls

**Effort**: 30 minutes  
**Result**: Builds pass, but features broken

### Option B: Create Minimal Stubs (Medium)

Create minimal interface/class stubs for each missing type:
```csharp
// src/VoiceStudio.Core/Services/IPanelRegistry.cs
namespace VoiceStudio.Core.Services
{
    public interface IPanelRegistry
    {
        void Register(PanelDescriptor descriptor);
        PanelDescriptor? GetDescriptor(string panelId);
    }
}
```

**Effort**: 1-2 hours  
**Result**: Builds pass, minimal functionality

### Option C: Full Chat History Extraction (Comprehensive)

Use Cursor UI to:
1. Open Composer history (Ctrl+L)
2. Search for each missing type name
3. Find conversation where it was generated
4. Copy full implementation
5. Create files

**Effort**: 2-4 hours  
**Result**: Full functionality restored

---

## Recommended Search Strategy

### Step 1: Search Cursor Composer History

Press **Ctrl+L** in Cursor, then search for:
1. "IPanelRegistry"
2. "IProfilesUseCase"
3. "ITelemetryService"
4. "Services.Persistence"
5. "ProjectMetadata"
6. "DiagnosticsSettings"

For each result, note:
- Conversation ID/timestamp
- Full code block generated
- File path mentioned

### Step 2: Search by Role Command

Search chat history for:
- `/role-core-platform` (most likely has IPanelRegistry, Persistence, repositories)
- `/role-ui-engineer` (ProfilesViewModel, UseCases, SLO models)
- `/role-build-tooling` (any build-related interface additions)

### Step 3: Search by Task

Search for task references:
- "TASK-0006" or "TASK-0007" or "TASK-0008" (advanced panels - SLO models, telemetry)
- "VS-0004" (project persistence)
- "VS-0015" (storage migration)
- "VS-0036" (IPanelRegistry addition per Proof Index)

### Step 4: Timeline-Based Search

Focus on conversations from:
- **2026-01-25 to 2026-01-28**: Most Core Platform and UI work
- **2026-01-28**: TASK-0006/0007/0008 (advanced panels)
- **2026-01-27**: VS-0036 fix (IPanelRegistry.Register method)

---

## Recovery Priority (If Doing Manual Extraction)

**Priority 1** (critical for builds):
1. `IPanelRegistry` interface — 10+ references
2. `IProfilesUseCase` namespace fix — already exists, just wrong namespace
3. `Services.Persistence` — needed by ProjectStore

**Priority 2** (for features):
4. `ITelemetryService` — needed for SLO Dashboard
5. `IViewModelContext` — needed for BaseViewModel
6. `ProjectMetadata`, `ProjectData` — needed for project operations

**Priority 3** (can defer):
7. `DiagnosticsSettings` — can stub
8. SLO models — can recreate from TASK-0007

---

## Files Currently in Git (After Merge)

✅ **Present**:
- `src/VoiceStudio.App/Core/Services/IProfilesUseCase.cs` (but wrong namespace)
- `src/VoiceStudio.App/Core/Panels/PanelDescriptor.cs`
- `src/VoiceStudio.App/Core/Panels/PanelRegion.cs`
- `tools/overseer/` (complete)
- `.cursor/STATE.md` (with all proof references)

❌ **Missing**:
- `src/VoiceStudio.Core/Services/IPanelRegistry.cs`
- `src/VoiceStudio.Core/Services/ITelemetryService.cs`
- `src/VoiceStudio.Core/Services/IViewModelContext.cs`
- `src/VoiceStudio.Core/Services/IProjectRepository.cs`
- `src/VoiceStudio.Core/Models/ProjectMetadata.cs`
- `src/VoiceStudio.Core/Models/ProjectData.cs`
- `src/VoiceStudio.Core/Models/Telemetry.cs` (with SLO models)
- `src/VoiceStudio.App/Services/Persistence/` directory
- `src/VoiceStudio.App/UseCases/` directory (or namespace fix for IProfilesUseCase)

---

*Use this guide to systematically recover missing code from Cursor chat history. Each missing type is mapped to its expected location and the role/task that created it.*
