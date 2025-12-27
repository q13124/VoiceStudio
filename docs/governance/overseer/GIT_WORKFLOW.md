## Git collaboration workflow (multi-role)

### Purpose

Enable parallel work by multiple roles with clean integration back into `master`.

### Branch naming

- Pattern: `role/<roleName>/VS-<ledgerId>-<shortDesc>`
- `roleName`: `overseer`, `architect`, `build`, `ui`, `core`, `engine`, `release`
- `ledgerId`: an entry ID from `Recovery Plan/QUALITY_LEDGER.md`

### Change set metadata (mandatory)

Include the following metadata in the change set description (or at the top of the merge message if working locally):

- Ledger ID
- Gate (A–H)
- Owner role
- Sign-off role
- Proof run commands
- Result summary (1–3 lines)

### Basic flow

1. Create or update the ledger entry in `Recovery Plan/QUALITY_LEDGER.md`.
2. Create the branch from `master` using the naming pattern above.
3. Implement the change inside the role boundary.
4. Run proof commands for the impacted gate and capture a short result summary.
5. Add the handoff file: `docs/governance/overseer/CHANGESET_HANDOFF_TEMPLATE.md` (filled out for this change set).
6. Merge back into `master` after sign-off.

