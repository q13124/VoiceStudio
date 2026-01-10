# Build & Tooling Engineer — Next task list

## Mission alignment

Keep the build/publish lane deterministic so **voice cloning quality work** can proceed without toolchain drift.

## Current state snapshot (from evidence)

- Gate C artifact: **unpackaged self-contained apphost EXE** (preferred fast path).
- Publish is green; binlogs retained under `.buildlogs/` (see `docs/governance/overseer/handoffs/VS-0020.md`).
- Default model root is now `E:\VoiceStudio\models` (set by `backend/api/main.py` unless overridden).

## What you do next (ordered)

### 1) Make Gate C proof reproducible (publish + launch)

- [ ] Add a single-command script to publish Release apphost and launch smoke it (no placeholders):
  - **Location**: `scripts/` (or `tools/`)
  - **Must do**:
    - Run `dotnet publish` (Release, win-x64, self-contained, apphost)
    - Start the produced `VoiceStudio.App.exe`
    - Capture **exit code**, and optionally write a minimal launch log to `.buildlogs/`
  - **Success**: running the script on a clean shell produces the same publish output and launch behavior every time.

### 2) Ensure toolchain pinning is stable (no experimental WinUI)

- [ ] Verify the build uses the pinned WinAppSDK/WinUI toolchain (no `*-experimental` compiler/tooling).
- [ ] If any experimental packages are being restored, remove/override them via `Directory.Build.props`/central package versions.
- **Success**: publish/binlog shows stable WinUI/XAML compiler inputs; no “experimental” package paths appear.

### 3) CI enforcement lane coverage (build + publish sanity)

- [ ] Add/adjust CI checks to run:
  - RuleGuard
  - `dotnet build` (Debug/Release x64)
  - `dotnet publish` (Release, Gate C artifact)
  - Sanity check publish output contains `VoiceStudio.App.exe` and supporting files
- **Success**: CI can fail fast when publish output regresses (missing apphost, missing deps, etc.).

### 4) Close the build-side Gate C work item (handoff hygiene)

- [ ] Update `docs/governance/overseer/handoffs/VS-0020.md` with:
  - The latest proof commands
  - Binlog paths
  - Launch result (including exit code + any captured crash evidence if it fails)
- [ ] Coordinate with Overseer to ensure **the ledger** includes VS-0020 and reflects current state (DONE vs IN_PROGRESS).
- **Success**: other roles can look at the ledger + VS-0020 handoff and know exactly how to reproduce success.

## Hand-off expectation

When you finish, Release Engineer should be able to:

- Use the Gate C script/output to launch the Release artifact reliably
- Proceed to installer/upgrade proof work (Gate H) without build uncertainty
