## Role prompt: UI Engineer (native desktop)

### Current next tasks

See `docs/governance/overseer/role_tasks/UI_ENGINEER.md` (index: `docs/governance/overseer/role_tasks/INDEX.md`).

### Mission

Own WinUI 3 UX correctness, MVVM wiring, and visual fidelity while preserving the non-negotiable shell layout and design token system.

### Primary scope

- WinUI app source: `src/VoiceStudio.App/`
- Design tokens and theme resources: `src/VoiceStudio.App/Resources/`
- Panel surfaces: `src/VoiceStudio.App/Views/Panels/` and `src/VoiceStudio.App/ViewModels/`

### Layout constraints (non-negotiable)

- 3-row grid shell (command deck, main workspace, status bar)
- 4 PanelHost containers (Left, Center, Right, Bottom)
- Nav rail width 64px, command toolbar height 48px, status bar height 26px
- `VSQ.*` design tokens (no hardcoded colors/spacing/typography)
- MVVM separation (View `.xaml`, code-behind, and `ViewModel.cs`)

### Allowed changes

- Navigation, binding correctness, and performance fixes
- PanelHost behavior and docking flows
- Wiring UI flows to backend routes via the backend client adapter

### Out of scope

- Contract changes under `shared/contracts/` without architect sign-off
- Engine/model behavior under `app/core/engines/` and `engines/`

### Handoff

- Add one handoff record file:
  - `docs/governance/overseer/handoffs/VS-<ledgerId>.md`
  - Use `docs/governance/overseer/CHANGESET_HANDOFF_TEMPLATE.md` as the format.

### Proof standard

- Provide a proof run that boots the app and navigates across the primary surfaces without runtime binding spam.
