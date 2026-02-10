# ADR-016: Gate C Artifact Choice

## Status

**Accepted** (2026-01-29)

## Context

Gate C requires a deterministic "standard launch artifact" for boot stability verification. Two options were evaluated:

1. **MSIX Package**: Windows App SDK native packaging format with automatic runtime management
2. **Unpackaged Apphost EXE**: Self-contained executable with embedded runtime

## Decision

**Lock unpackaged self-contained apphost EXE as the Gate C standard launch method.**

## Rationale

### ✅ Unpackaged EXE Advantages

- **Faster iteration**: Direct EXE execution vs MSIX installation overhead
- **Debugging clarity**: Direct process launch with immediate error visibility
- **Runtime control**: Explicit Windows App SDK runtime inclusion
- **CI/CD compatibility**: No package installation requirements
- **Current working state**: Debug builds launch successfully

### ❌ MSIX Disadvantages (Encountered)

- **PRI resource conflicts**: Duplicate item errors in build pipeline
- **Installation overhead**: Package deployment vs direct execution
- **Activation complexity**: WinRT class registration requirements
- **Build complexity**: MSIX manifest and signing requirements

### Evidence from VS-0020 Investigation

- Release publish produces functional apphost EXE under `.buildlogs/`
- CoreMessagingXP.dll crash (0xC0000602) appears runtime-related, not packaging-related
- Gate C script `scripts/gatec-publish-launch.ps1` successfully produces and launches unpackaged EXE
- WinUI activation issues (VS-0012) can be isolated without MSIX complexity

## Implementation

### MSBuild Properties (Locked)

```xml
<WindowsPackageType>None</WindowsPackageType>
<EnableMsixTooling>false</EnableMsixTooling>
<EnableDefaultPriItems>false</EnableDefaultPriItems>
<UseAppHost>true</UseAppHost>
<SelfContained>true</SelfContained>
<WindowsAppSDKSelfContained>true</WindowsAppSDKSelfContained>
```

### Gate C Proof Script

`scripts/gatec-publish-launch.ps1` implements the standard method:

- Publishes with above properties
- Launches resulting `VoiceStudio.App.exe`
- Verifies process stability for N seconds

## Consequences

### ✅ Positive

- Faster Gate C iteration cycles
- Clearer failure diagnosis
- Consistent with current working builds
- Single-lane packaging: unpackaged EXE + installer only (MSIX archived/removed)

### ⚠️ Risk Mitigation

- Installer is the only supported distribution path (Inno Setup / WiX)
- Runtime embedding ensures local-first operation
- WinUI activation issues isolated from packaging decisions

## Alternatives Considered

### MSIX as Primary

**Rejected** due to build complexity and activation issues encountered in VS-0012 investigation.

### Framework-dependent EXE

**Rejected** due to .NET runtime installation complexity in clean environments.

## Change History

- **2026-01-06**: Decision locked in ADR
- **Context**: VS-0020 investigation completed, unpackaged EXE proven functional
- **2026-01-10**: MSIX lane explicitly archived/removed; installer-based distribution only