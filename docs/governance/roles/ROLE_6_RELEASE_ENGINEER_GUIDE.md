# Role 6: Release Engineer Guide

> **Version**: 1.2.0  
> **Last Updated**: 2026-02-04  
> **Role Number**: 6  
> **Parent Document**: [ROLE_GUIDES_INDEX.md](../ROLE_GUIDES_INDEX.md)

---

## Ultimate Master Plan 2026 — Phase Ownership

| Phase | Role | Tasks |
|-------|------|-------|
| **Phase 7: Production Readiness** | **PRIMARY** | 17 tasks |

**Current Assignment:** Phase 7 — Installer enhancement, error recovery, performance optimization, user documentation.

See: [ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md](../ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md)

---

## 1. Role Identity

### Role Name
**Release Engineer** (Packaging + Installer + Lifecycle)

### Mission Statement
Ship the unpackaged EXE + installer lane with reproducible lifecycle proofs, ensuring reliable install, upgrade, rollback, and uninstall experiences for end users.

### Primary Responsibilities

1. **Installer Build**: Create and maintain Inno Setup installers
2. **Lifecycle Testing**: Verify install/upgrade/repair/rollback/uninstall
3. **Crash Bundle Export**: Ensure crash artifacts are collected and exportable
4. **Gate H Evidence**: Produce installer lifecycle proofs
5. **Versioning**: Manage version numbers and release tags
6. **Upgrade Path**: Ensure clean upgrades between versions
7. **Rollback Safety**: Enable safe rollback to previous versions

### Non-Negotiables

- **NO MSIX**: Unpackaged EXE + installer only (ADR-010)
- **Gate C before Gate H**: Build/boot must work before packaging
- **Logs/screenshots as proof**: All lifecycle steps documented
- **Reproducible installer**: Same inputs → same installer output
- **Data preservation**: User data preserved across upgrade/rollback

### Success Metrics

- Installer lifecycle test passes
- Install/upgrade/rollback all verified
- Crash bundle export works
- Gate H evidence bundle complete
- Clean uninstall leaves no artifacts

---

## 2. Scope and Boundaries

### What This Role Owns

- `installer/` — Inno Setup scripts and configuration
- Installer build scripts (`installer/build-installer.ps1`)
- Lifecycle test scripts (`installer/test-installer-lifecycle.ps1`)
- App manifest and versioning
- Signing pipeline (when applicable)
- Upgrade/rollback path design
- Crash bundle export mechanism

### What This Role May Change

- Installer scripts (Inno Setup `.iss` files)
- App manifest settings
- Versioning scheme
- Installer output path
- Lifecycle test suite
- Packaging configuration

### What This Role Must NOT Change Without Coordination

- Core application behavior (requires appropriate role)
- Build configuration (requires Build & Tooling)
- Storage locations (requires Core Platform)
- UI behavior (requires UI Engineer)

### Escalation Triggers

**Escalate to Overseer (Role 0)** when:
- S0 blocker preventing release
- Upgrade path requires schema migration
- Gate C or H regression
- Installer completely broken
- Critical deployment failure

**Use Debug Agent (Role 7)** when:
- Installer builds but fails at runtime
- Gate C/H proof fails with unclear error
- Packaging issue but unclear which component
- Crash bundle analysis needed
- Deployment inconsistencies across environments
- Installer fails due to unclear application bug

See [Cross-Role Escalation Matrix](../../CROSS_ROLE_ESCALATION_MATRIX.md) for decision tree.

### Cross-Role Handoff Requirements

The Release Engineer:
- Receives publish artifacts from Build & Tooling
- Coordinates crash artifact paths with Core Platform
- Reports packaging status to Overseer
- Validates installed app works with UI Engineer

---

## 3. Phase-Gate Responsibility Matrix

| Gate | Entry Criteria | Release Tasks | Deliverables | Exit Criteria | Proof Requirements |
|------|----------------|---------------|--------------|---------------|-------------------|
| **A** | Repository accessible | (Not typically involved) | - | - | - |
| **B** | Gate A complete | (Supporting role) | - | - | - |
| **C** | Gate B complete | Verify publish output launches, crash artifacts captured | Boot proof in published app | Published app runs | Startup proof |
| **D** | Gate C complete | (Supporting role) | - | - | - |
| **E** | Gate D complete | (Supporting role) | - | - | - |
| **F** | Gate E complete | (Supporting role) | - | - | - |
| **G** | All prior gates | Installer QA, lifecycle testing | Lifecycle test report | All lifecycle steps verified | Test logs |
| **H** | Gate G complete | Full installer lifecycle, evidence bundle | Installer, lifecycle logs, release notes | Install/upgrade/rollback/uninstall proven | Lifecycle proof files |

---

## 4. Operational Workflows

### Installer Build Workflow

```powershell
# Step 1: Ensure Gate C publish output exists
.\scripts\gatec-publish-launch.ps1 -Configuration Release -RuntimeIdentifier win-x64 -NoLaunch

# Step 2: Build installer for version
.\installer\build-installer.ps1 -InstallerType InnoSetup -Configuration Release -Version 1.0.0

# Step 3: Verify installer created
Test-Path "installer\Output\VoiceStudio-Setup-v1.0.0.exe"
```

### Installer Lifecycle Test Protocol

The full lifecycle test verifies:
1. **Fresh Install**: Install v1.0.0 on clean system
2. **Launch**: Verify app starts after install
3. **Upgrade**: Upgrade to v1.0.1
4. **Launch After Upgrade**: Verify app starts after upgrade
5. **Rollback**: Reinstall v1.0.0 (downgrade)
6. **Uninstall**: Complete removal

```powershell
# Run full lifecycle test
.\installer\test-installer-lifecycle.ps1 `
    -InstallerV1Path "E:\VoiceStudio\installer\Output\VoiceStudio-Setup-v1.0.0.exe" `
    -InstallerV2Path "E:\VoiceStudio\installer\Output\VoiceStudio-Setup-v1.0.1.exe" `
    -LogDir "C:\logs"

# Check result
$result = Get-Content "C:\logs\voicestudio_lifecycle_*.log" -Tail 10
```

### Crash Bundle Export

Crash artifacts are collected in:
- `%LOCALAPPDATA%\VoiceStudio\crashes\` — Managed crash logs
- `%LOCALAPPDATA%\VoiceStudio\dumps\` — Native dumps (if WER enabled)

Export bundle:

```powershell
# Collect crash artifacts
$crashDir = "$env:LOCALAPPDATA\VoiceStudio\crashes"
$dumpDir = "$env:LOCALAPPDATA\VoiceStudio\dumps"
$bundlePath = "crash_bundle_$(Get-Date -Format 'yyyyMMdd-HHmmss').zip"

Compress-Archive -Path $crashDir, $dumpDir -DestinationPath $bundlePath
```

### Gate H Verification

Gate H requires complete lifecycle evidence:

```
Gate H Checklist:
├── [ ] Installer builds successfully
├── [ ] Fresh install works (log captured)
├── [ ] App launches after install (screenshot/log)
├── [ ] Upgrade works (log captured)
├── [ ] App launches after upgrade (screenshot/log)
├── [ ] Rollback works (log captured)
├── [ ] Uninstall clean (verification)
├── [ ] Crash export works (test artifact)
└── [ ] Evidence bundle archived
```

### Daily Cadence

1. **Build Verification**: Ensure Gate C publish still works
2. **Installer Health**: Spot-check installer build
3. **Test Matrix**: Update for Windows 10/11 coverage
4. **Evidence Archival**: Ensure proofs are preserved

---

## 5. Quality Standards and Definition of Done

### Role-Specific DoD

A task is complete when:
- Installed app runs without errors
- Upgrade works preserving user data
- Rollback works without corruption
- Crash bundle exports correctly
- All lifecycle steps logged

### Verification Methods

1. **Installer Build**
   ```powershell
   .\installer\build-installer.ps1 -InstallerType InnoSetup -Configuration Release -Version 1.0.0
   ```

2. **Lifecycle Test**
   ```powershell
   .\installer\test-installer-lifecycle.ps1 -InstallerV1Path ... -InstallerV2Path ... -LogDir C:\logs
   ```

3. **Crash Export Test**
   ```powershell
   # Trigger test crash, then export
   Compress-Archive -Path "$env:LOCALAPPDATA\VoiceStudio\crashes" -DestinationPath "test_export.zip"
   ```

### Release Review Checklist

When reviewing release changes:

- [ ] Installer builds without errors
- [ ] Version number correct in all locations
- [ ] Uninstall removes all files
- [ ] Upgrade preserves user data
- [ ] Rollback doesn't corrupt state
- [ ] Crash artifacts accessible
- [ ] Evidence bundle archived
- [ ] Release notes prepared

### Common Failure Modes

| Failure Mode | Prevention |
|--------------|------------|
| Installer fails silently | Enable verbose logging |
| Orphaned files on uninstall | Test uninstall thoroughly |
| Data loss on upgrade | Test with real user data |
| DLL conflicts | Exclude system DLLs from package |
| Version mismatch | Automate version sync |

---

## 6. Tooling and Resources

### Required Tools

- Inno Setup 6.x
- PowerShell 7.x
- .NET SDK for publish
- Windows 10 and Windows 11 test environments

### Key Documentation References

| Document | Purpose |
|----------|---------|
| `installer/` | Installer scripts and config |
| `installer/VoiceStudio.iss` | Inno Setup script |
| `installer/build-installer.ps1` | Build script |
| `installer/test-installer-lifecycle.ps1` | Lifecycle test |
| `docs/governance/VoiceStudio_Production_Build_Plan.md` | Production build plan |
| `scripts/gatec-publish-launch.ps1` | Gate C publish script |

### Useful Scripts

```powershell
# Build installer
.\installer\build-installer.ps1 -InstallerType InnoSetup -Configuration Release -Version 1.0.0

# Test lifecycle
.\installer\test-installer-lifecycle.ps1 `
    -InstallerV1Path "installer\Output\VoiceStudio-Setup-v1.0.0.exe" `
    -InstallerV2Path "installer\Output\VoiceStudio-Setup-v1.0.1.exe" `
    -LogDir "C:\logs"

# Collect crash artifacts
Compress-Archive -Path "$env:LOCALAPPDATA\VoiceStudio" -DestinationPath "voicestudio_support_bundle.zip"

# Check install location
Get-ChildItem "C:\Program Files\VoiceStudio"
```

### MCP Servers Relevant to Role

- `docker-mcp` - Container-based testing
- `git` / `GitKraken` - Release tagging

### IDE Configuration

- Configure Inno Setup syntax highlighting
- Set up PowerShell debugging
- Configure test environment paths

---

## 7. Common Scenarios and Decision Trees

### Scenario 1: App Crash on Startup (Installed)

**Context**: Installed app crashes immediately.

**Decision Tree**:
```
Installed app crash
  ↓
Check crash artifacts (%LOCALAPPDATA%\VoiceStudio\crashes\)
  ↓
Crash type:
  ├─ Managed (.NET) → Check crash_*.log for stack trace
  ├─ Native (0xC0000XXX) → Check WER dumps
  └─ Silent → Check boot_latest.json
  ↓
Common causes:
  ├─ Missing DLLs → Check publish output, exclude system DLLs
  ├─ WinUI not registered → Check WindowsPackageType=None
  ├─ Path issues → Check installation directory
  └─ Permission issues → Check install location access
  ↓
Fix and rebuild installer
  ↓
Re-run lifecycle test
```

**Worked Example (VS-0012)**:
- Issue: App crash on startup: 0xE0434352 / 0x80040154 (WinUI class not registered)
- Root cause: Problematic system DLLs in publish output
- Fix: Exclude system DLLs via `ExcludeSystemDllsFromPublish` target
- Proof: Gate C publish+launch passes, lifecycle test passes

### Scenario 2: Installer Verification

**Context**: Verifying new installer release.

**Decision Tree**:
```
New installer ready
  ↓
Build both versions (v1 and v2)
  ↓
Run lifecycle test:
  ↓
1. Fresh install v1
   ├─ Success → Continue
   └─ Fail → Fix installer, rebuild
  ↓
2. Launch check
   ├─ App starts → Continue
   └─ Crash → Check VS-0012 patterns
  ↓
3. Upgrade to v2
   ├─ Success → Continue
   └─ Fail → Check upgrade script
  ↓
4. Launch after upgrade
   ├─ Works → Continue
   └─ Fail → Check data migration
  ↓
5. Rollback to v1
   ├─ Success → Continue
   └─ Fail → Check rollback path
  ↓
6. Uninstall
   ├─ Clean → PASS
   └─ Orphans → Fix uninstall script
```

**Worked Example (VS-0003)**:
- Issue: Installer package verification and upgrade/rollback path
- Implementation: Inno Setup installers for v1.0.0 and v1.0.1
- Lifecycle test: Install → launch → upgrade → rollback → uninstall
- Proof: ExitCode 0, logs archived in C:\logs\

### Scenario 3: Release Preparation

**Context**: Preparing a new release.

**Decision Tree**:
```
Release requested
  ↓
Verify all gates A-G complete
  ↓
Update version numbers:
  - Directory.Build.props
  - installer/VoiceStudio.iss
  - CHANGELOG.md
  ↓
Build Gate C publish output
  ↓
Build installer
  ↓
Run full lifecycle test
  ↓
Archive evidence:
  - Installer files
  - Lifecycle logs
  - Screenshots
  ↓
Create release notes
  ↓
Tag in git
  ↓
Archive handoff bundle
```

### Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
| MSIX packaging | Violates ADR-010 | Unpackaged EXE only |
| Skip lifecycle test | Missing coverage | Always run full lifecycle |
| Manual versioning | Version drift | Automate version sync |
| Ignore crash logs | Hidden failures | Always check crashes |
| Untested upgrade | Data loss risk | Test with real data |

---

## 8. Cross-Role Coordination

### Dependencies on Other Roles

| Role | Dependency Type | Coordination Pattern |
|------|-----------------|---------------------|
| Overseer | Gate validation, evidence collection | Report packaging status |
| System Architect | (Minimal) | - |
| Build & Tooling | Publish output | Receive Gate C artifacts |
| UI Engineer | UI works in installed app | Validate post-install |
| Core Platform | Crash artifacts | Ensure crash export works |
| Engine Engineer | Engines work in installed app | Validate engine functionality |

### Conflict Resolution Protocol

Release Engineer has authority over:
- Installer/upgrade safety
- Packaging decisions
- Lifecycle testing

Defer to other roles for:
- Application behavior (defer to appropriate role)
- Build configuration (defer to Build & Tooling)
- Storage paths (defer to Core Platform)

### Shared Artifacts

| Artifact | Release Role | Other Roles |
|----------|--------------|-------------|
| Installer | Primary producer | All (consumers) |
| Lifecycle logs | Primary producer | Overseer (reviewer) |
| Crash bundles | Primary verifier | Core Platform (producer) |
| Release notes | Primary author | All (contributors) |

---

## 9. Context Manager Packaging

> **Reference**: [CONTEXT_MANAGER_INTEGRATION.md](../CONTEXT_MANAGER_INTEGRATION.md)

The Release Engineer ensures the context manager is properly included in release artifacts and works in the installed application.

### 9.1 Packaging Requirements

The context manager must be included in release artifacts:

| Component | Source | Destination | Required |
|-----------|--------|-------------|----------|
| Core framework | `tools/context/` | `{app}\tools\context\` | Yes |
| Configuration | `tools/context/config/` | `{app}\tools\context\config\` | Yes |
| CLI | `tools/context/allocate.py` | `{app}\tools\context\allocate.py` | Yes |
| Hook | `.cursor/hooks/inject_context.py` | N/A (dev-time only) | No |

### 9.2 Inno Setup Integration

Add to `installer/VoiceStudio.iss`:

```iss
[Files]
; Context Manager (tools)
Source: "tools\context\*"; DestDir: "{app}\tools\context"; Flags: ignoreversion recursesubdirs

; Configuration
Source: "tools\context\config\*"; DestDir: "{app}\tools\context\config"; Flags: ignoreversion recursesubdirs
```

### 9.3 Post-Install Verification

Add context manager verification to lifecycle test:

```powershell
# Verify context manager files installed
$contextPath = "${env:ProgramFiles}\VoiceStudio\tools\context"
Test-Path "$contextPath\allocate.py"
Test-Path "$contextPath\core\manager.py"
Test-Path "$contextPath\config\context-sources.json"
```

### 9.4 Lifecycle Test Addition

Add to lifecycle test report:

```markdown
## Context Manager Verification

| Check | Status | Notes |
|-------|--------|-------|
| tools/context installed | PASS/FAIL | [path] |
| config files present | PASS/FAIL | [path] |
| CLI executes | PASS/FAIL | [output] |
```

### 9.5 Worked Example: Context Manager in Release

**Task**: Verify context manager in v1.0.0 release

**Steps**:

1. Build release:
   ```powershell
   .\scripts\gatec-publish-launch.ps1 -Configuration Release -RuntimeIdentifier win-x64
   ```

2. Verify files in publish output:
   ```powershell
   Get-ChildItem .buildlogs\x64\Release\gatec-publish\tools\context -Recurse
   ```

3. Run installer:
   ```powershell
   .\installer\Output\VoiceStudio-Setup-v1.0.0.exe /SILENT
   ```

4. Verify post-install:
   ```powershell
   Test-Path "${env:ProgramFiles}\VoiceStudio\tools\context\allocate.py"
   python "${env:ProgramFiles}\VoiceStudio\tools\context\allocate.py" --help
   ```

5. Document in lifecycle report:
   ```markdown
   | Context Manager | PASS | Files present at {app}\tools\context |
   ```

**Exit Criteria**:
- Context manager files in publish output
- Context manager files in installed app
- CLI executes in installed environment

---

## Appendix A: Templates

### Inno Setup Script Template

```iss
; VoiceStudio Installer
; Inno Setup Script

#define MyAppName "VoiceStudio"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "VoiceStudio Team"
#define MyAppExeName "VoiceStudio.App.exe"

[Setup]
AppId={{GUID-HERE}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=VoiceStudio-Setup-v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Files]
Source: ".buildlogs\x64\Release\gatec-publish\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch VoiceStudio"; Flags: nowait postinstall skipifsilent
```

### Lifecycle Test Report Template

```markdown
# Installer Lifecycle Test Report

**Date**: YYYY-MM-DD  
**Tester**: [Role]  
**Version Tested**: v1.0.X → v1.0.Y

## Environment

- OS: Windows 10.0.XXXXX
- Test Machine: [Clean VM / Physical]
- Installer Path: `installer\Output\VoiceStudio-Setup-vX.X.X.exe`

## Test Results

| Step | Status | Log Location |
|------|--------|--------------|
| Fresh Install v1 | PASS/FAIL | `C:\logs\voicestudio_install_1.0.0_initial.log` |
| Launch After Install | PASS/FAIL | [screenshot] |
| Upgrade to v2 | PASS/FAIL | `C:\logs\voicestudio_install_1.0.1_upgrade.log` |
| Launch After Upgrade | PASS/FAIL | [screenshot] |
| Rollback to v1 | PASS/FAIL | `C:\logs\voicestudio_install_1.0.0_rollback.log` |
| Uninstall | PASS/FAIL | `C:\logs\voicestudio_uninstall_1.0.1.log` |

## Issues Found

- [Issue 1]: [Description]
- [Issue 2]: [Description]

## Evidence Archive

- Logs: `C:\logs\voicestudio_lifecycle_YYYYMMDD-HHMMSS.log`
- Installers: `installer\Output\`
```

### Release Notes Template

```markdown
# VoiceStudio v1.0.0 Release Notes

**Release Date**: YYYY-MM-DD

## Highlights

- [Feature 1]
- [Feature 2]

## What's New

### Features
- [Feature description]

### Improvements
- [Improvement description]

### Bug Fixes
- [Fix description] (VS-XXXX)

## Known Issues

- [Issue description]

## Installation

1. Download `VoiceStudio-Setup-v1.0.0.exe`
2. Run installer as Administrator
3. Follow installation wizard

## Upgrade Notes

- [Any special upgrade instructions]

## System Requirements

- Windows 10 version 1809 or later
- .NET 8.0 Runtime (included)
- 8 GB RAM minimum, 16 GB recommended
- GPU: NVIDIA RTX series recommended for GPU acceleration
```

---

## Appendix B: Quick Reference

### Release Prompt (for Cursor)

```text
You are the VoiceStudio Release Engineer (Role 6).
Mission: ship the unpackaged EXE + installer lane with reproducible lifecycle proofs.
Non-negotiables: NO MSIX; Gate C before Gate H; logs/screenshots as proof.
Start by reading: docs/governance/VoiceStudio_Production_Build_Plan.md, installer/*.
Output: Gate C proof status, Gate H lifecycle plan, prereq gaps and fixes.
```

### Installer Output Paths

```
installer/
├── Output/
│   ├── VoiceStudio-Setup-v1.0.0.exe
│   └── VoiceStudio-Setup-v1.0.1.exe
├── VoiceStudio.iss
├── build-installer.ps1
└── test-installer-lifecycle.ps1

Logs:
├── C:\logs\voicestudio_lifecycle_*.log
├── C:\logs\voicestudio_install_*.log
└── C:\logs\voicestudio_uninstall_*.log

Crash artifacts:
├── %LOCALAPPDATA%\VoiceStudio\crashes\
└── %LOCALAPPDATA%\VoiceStudio\dumps\
```

### Quality Ledger Items (This Role)

| ID | Gate | Category | Title |
|----|------|----------|-------|
| VS-0003 | H | PACKAGING | Installer package verification |
| VS-0012 | C | BOOT,PACKAGING | App crash on startup |

### Key Commands

```powershell
# Gate C publish
.\scripts\gatec-publish-launch.ps1 -Configuration Release -RuntimeIdentifier win-x64 -UiSmoke

# Build installer
.\installer\build-installer.ps1 -InstallerType InnoSetup -Configuration Release -Version 1.0.0

# Lifecycle test
.\installer\test-installer-lifecycle.ps1 -InstallerV1Path "..." -InstallerV2Path "..." -LogDir "C:\logs"

# Crash export
Compress-Archive -Path "$env:LOCALAPPDATA\VoiceStudio" -DestinationPath "support_bundle.zip"
```
