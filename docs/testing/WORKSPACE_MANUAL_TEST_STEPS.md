# Workspace Switching — Manual Test Steps

Use these steps to verify that workspace profiles and the toolbar workspace dropdown work correctly.

## Prerequisites

- VoiceStudio built and runnable (Debug or Release).
- No need to clear settings unless testing first-run behavior.

## Test Steps

1. **Start the app**
   - Launch VoiceStudio.
   - Note the default panels in Left, Center, Right, and Bottom regions (e.g. Studio workspace: Profiles, Timeline, EffectsMixer, Macro).

2. **Switch workspaces in order**
   - Open the **Workspace** dropdown in the toolbar (Command Deck).
   - Switch to **Recording** → confirm panels change per Recording layout (e.g. Recording-focused panels).
   - Switch to **Training** → confirm panels change per Training layout.
   - Switch to **Synthesis** → confirm panels change per Synthesis layout.
   - Switch to **Studio** → confirm panels return to Studio layout.
   - Switch to **Batch Lab** → confirm panels change per Batch Lab layout.
   - Switch to **Pro Mix** → confirm panels change per Pro Mix layout.
   - Switch to **Mixing** and **Analysis** → confirm each updates the layout.

3. **Return to Studio**
   - Select **Studio** from the workspace dropdown.
   - Confirm the layout matches the initial Studio layout (e.g. Profiles, Timeline, EffectsMixer, Macro).

4. **Persistence**
   - With any workspace selected (e.g. Training), close the application.
   - Reopen VoiceStudio.
   - Confirm the last selected workspace is restored (dropdown shows that workspace and panels match).

## Optional: First-Run / Empty Layout

- Clear or rename `%LocalAppData%/VoiceStudio/` (or delete only the workspace profile files under `WorkspaceProfiles/`) so no saved layout exists.
- Start the app.
- Confirm the default workspace is **Studio** and that panels load from the embedded Studio layout (no empty layout).

## Pass Criteria

- Each workspace selection changes the panel layout immediately.
- Toolbar workspace combo shows the current workspace and stays in sync after switch.
- After restart, the last selected workspace is restored.
- No silent failures: unknown panel IDs or embedded load failures are logged; app falls back gracefully (e.g. empty layout with warning).

## Automated / Gate C

**Implemented** (TD-036, 2026-02-12). The Gate C UI smoke (`--smoke-ui`) now includes workspace-switch steps at the end of `RunGateCUiSmokeNavigationAsync` in `MainWindow.xaml.cs`:

1. **WorkspaceSwitchToTraining**: Calls `PanelStateService.SwitchWorkspaceProfileAsync("training")`, waits for layout application, then asserts that center `PanelHost.Content` is `TrainingView`.
2. **WorkspaceSwitchToStudio**: Switches back to `"studio"` and asserts center panel is `TimelineView`.

Assertions use the view type name (e.g. `TrainingView`, `TimelineView`) which corresponds to deterministic panel IDs from the [AUTOMATION_ID_REGISTRY](../developer/AUTOMATION_ID_REGISTRY.md). Failures are logged in `ui_smoke_steps_latest.log` and reflected in `ui_smoke_summary.json`.

Run via: `.\scripts\gatec-publish-launch.ps1` or with `--smoke-ui` flag.
