# XAML Change Protocol

This document defines the mandatory protocol for making XAML changes in VoiceStudio.
Following this protocol prevents the chained XAML compiler issues that have historically
blocked development for weeks (see VS-0001 through VS-0040 in Quality Ledger).

## Background

VoiceStudio uses WinUI 3 with WinAppSDK 1.8, which has known XAML compiler fragility:

- **Silent crashes**: Build exits with code 1 and no error message
- **Attached property issues**: TextElement.* attached properties on ContentPresenter crash the compiler
- **Animation targets**: ObjectAnimationUsingKeyFrames targeting attached properties causes silent failures
- **Order sensitivity**: The order of resource dictionary merges can cause non-deterministic failures

## Mandatory Checklist

Before committing ANY XAML change:

### Pre-Change

- [ ] Read this protocol completely
- [ ] Identify all XAML files being modified
- [ ] Create a rollback checkpoint using ONE of these methods:

```bash
# Option 1: Git stash (quick, reversible)
git stash push -u -m "pre-xaml-fix"

# Option 2: Commit checkpoint (preferred for larger changes)
git add -A && git commit -m "WIP: pre-XAML-change checkpoint"
```

- [ ] Verify checkpoint exists: `git stash list` or `git log -1`

### During Change

- [ ] Make changes to ONE XAML file at a time
- [ ] Build after each file change: `dotnet build VoiceStudio.sln -c Debug -p:Platform=x64`
- [ ] If build fails silently (exit code 1, no error), immediately revert and bisect

### Forbidden Patterns

These patterns **WILL** crash the XAML compiler. Never use them:

```xml
<!-- FORBIDDEN: Attached property on ContentPresenter -->
<ContentPresenter TextElement.Foreground="{TemplateBinding Foreground}" />

<!-- FORBIDDEN: Animation targeting attached property -->
<ObjectAnimationUsingKeyFrames Storyboard.TargetProperty="(TextElement.Foreground)">
    ...
</ObjectAnimationUsingKeyFrames>

<!-- FORBIDDEN: Storyboard targeting attached property -->
<Storyboard>
    <ColorAnimation Storyboard.TargetProperty="(TextElement.Foreground).Color" />
</Storyboard>
```

### Forbidden Directory Structure (GitHub #10947)

XAML files in deeply nested Views subfolders can cause silent compiler failures:

```
❌ FORBIDDEN: Deeply nested Views (3+ levels)
Views/
└── UI/
    └── Panels/
        └── MyView.xaml    <- XamlCompiler may exit code 1 silently

✅ SAFE: Flat Views structure (max 2 levels)
Views/
├── Panels/
│   └── MyView.xaml        <- OK
└── Shell/
    └── NavigationView.xaml <- OK
```

**Reference:** [GitHub Issue #10947](https://github.com/microsoft/microsoft-ui-xaml/issues/10947) - XamlCompiler.exe exits code 1 for Views subfolders

The build system will automatically warn if deeply nested Views XAML is detected.
To fail the build instead of warning, set `EnableViewsSubfolderError=true` in your build.

### Safe Alternatives

```xml
<!-- SAFE: Explicit property on TextBlock child -->
<ContentPresenter>
    <ContentPresenter.ContentTemplate>
        <DataTemplate>
            <TextBlock Foreground="{TemplateBinding Foreground}" Text="{Binding}" />
        </DataTemplate>
    </ContentPresenter.ContentTemplate>
</ContentPresenter>

<!-- SAFE: Animation on explicit property -->
<ObjectAnimationUsingKeyFrames Storyboard.TargetProperty="Foreground">
    ...
</ObjectAnimationUsingKeyFrames>
```

### Post-Change

- [ ] Run XAML lint: `python scripts/lint_xaml.py`
- [ ] Build succeeds with exit code 0
- [ ] No new warnings in build output
- [ ] Commit with descriptive message: `git commit -m "feat(ui): [brief description of XAML change]"`

## Troubleshooting Silent Build Failures

If you encounter a build that exits with code 1 and no error output:

### Step 1: Run Diagnostic Build with Binlog

```powershell
.\scripts\build-with-binlog.ps1
```

This runs a clean single-threaded build and captures a binary log for analysis.

### Step 2: Analyze the Binlog

```powershell
.\scripts\analyze-binlog.ps1 -BinlogPath .buildlogs\build_diagnostic_*.binlog
```

Or use the Python alternative:

```powershell
python scripts/analyze_binlog.py --binlog .buildlogs\build_diagnostic_*.binlog
```

This identifies:
- XamlCompiler.exe invocations
- Failing XAML files
- Nested Views subfolder issues (GitHub #10947)

### Step 3: Run the Bisect Tool

If binlog analysis doesn't pinpoint the issue:

```powershell
.\scripts\xaml-binary-search.ps1
```

Or the Python version:

```powershell
python tools/build/xaml_bisect.py
```

This will automatically find the problematic XAML file through binary search.

### Step 4: Run XAML Lint

```powershell
python scripts/lint_xaml.py path/to/problematic.xaml
```

### Step 5: Check Recent Changes

```powershell
git diff HEAD~1 -- "*.xaml"
```

### Step 6: Incremental Rollback

If bisect doesn't help:

1. Revert all XAML changes
2. Re-apply changes one file at a time
3. Build after each file
4. The file that breaks the build is the problem

## Emergency Recovery

If you're stuck with a broken build:

```powershell
# Option 1: Revert to last working state
git checkout HEAD~1 -- "src/**/*.xaml"

# Option 2: Clean and rebuild
dotnet clean VoiceStudio.sln
Remove-Item -Recurse -Force src/*/bin, src/*/obj
dotnet build VoiceStudio.sln -c Debug -p:Platform=x64

# Option 3: Full reset to baseline
git checkout v1.0.0-baseline -- "src/**/*.xaml"
```

## Pre-Commit Hook

The pre-commit hook `xaml-safety-check` runs automatically and will block commits
containing forbidden patterns. If you believe a pattern is a false positive,
document it in the PR and request review from Build & Tooling Engineer (Role 2).

## Build Configuration

VoiceStudio uses `UseXamlCompilerExecutable=true` in `Directory.Build.targets` to force the external XAML compiler process. This is **required** for the following reasons:

### Why External Compiler is Required

**1. net472 Path Hardcoding**

The Windows App SDK build task hard-codes paths to `net472\XamlCompiler.exe` when resolving dependencies. When the task loader attempts to run the compiler in-process, it cannot find these assemblies because the net472 SDK path is not in the assembly probing path.

**2. System.Security.Permissions Loading Failure**

The in-process loader fails to resolve `System.Security.Permissions.dll`, a .NET Framework 4.7.2 dependency. This failure manifests as:
- WMC9999 errors ("Unknown error")
- Silent build failures (exit code 1, no output)
- Intermittent failures that appear non-deterministic

**3. Process Isolation**

Running XamlCompiler.exe as a separate process:
- Isolates assembly loading to the compiler process
- Avoids polluting MSBuild with net472 dependencies
- Enables VoiceStudio's wrapper (`tools/xaml-compiler-wrapper.cmd`) to intercept and handle false-positive exit code 1 issues (VS-0001)

**DO NOT set `UseXamlCompilerExecutable=false`** unless you have explicitly resolved the System.Security.Permissions dependency chain for net472 targets.

## References

- Quality Ledger: VS-0001, VS-0010, VS-0014, VS-0040
- ADR-010: Platform Identity (WinUI 3 decision)
- Error Pattern Retrospective: Section 3.1 (XAML Chain Reaction)
- [UI Hardening Guidelines](UI_HARDENING_GUIDELINES.md) - Best practices for XAML stability
- [GitHub #10027](https://github.com/microsoft/microsoft-ui-xaml/issues/10027) - Can't get error output from XamlCompiler.exe
- [GitHub #10947](https://github.com/microsoft/microsoft-ui-xaml/issues/10947) - XamlCompiler.exe exits code 1 for Views subfolders

## Diagnostic Tools

| Tool | Purpose |
|------|---------|
| `scripts/build-with-binlog.ps1` | Clean single-threaded build with binlog capture |
| `scripts/analyze-binlog.ps1` | Extract XamlCompiler invocations from binlog |
| `scripts/analyze_binlog.py` | Python alternative for binlog analysis |
| `scripts/xaml-binary-search.ps1` | Binary search to isolate problematic XAML |
| `scripts/lint_xaml.py` | XAML lint for forbidden patterns |
| `tools/xaml-compiler-wrapper.cmd` | Compiler wrapper with false-positive handling |

## Change History

| Date | Author | Change |
|------|--------|--------|
| 2026-02-04 | XAML Reliability Plan | Added git stash checkpoint, Views subfolder warning, binlog analysis workflow |
| 2026-02-04 | Phase 7 Plan | Initial protocol created from retrospective findings |
