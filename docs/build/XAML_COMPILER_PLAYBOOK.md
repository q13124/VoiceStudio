# XAML Compiler Playbook

This is the single operational runbook for diagnosing and resolving WinUI 3 XAML compiler issues in VoiceStudio. Use this document when builds fail with XAML-related errors.

**Last Updated:** 2026-02-04

---

## Quick Reference Checklist

When a build fails with exit code 1 and no error message:

- [ ] Run diagnostic build: `.\scripts\build-with-binlog.ps1`
- [ ] Analyze binlog: `.\scripts\analyze-binlog.ps1 -OutputFormat summary`
- [ ] Check for nested Views: Look for `NESTED_VIEWS_XAML` in output
- [ ] Check for forbidden patterns: `python scripts/lint_xaml.py`
- [ ] Run binary search if needed: `.\scripts\xaml-binary-search.ps1`

---

## Decision Tree

```
Build Failed
    │
    ├─► Exit code 1, no error output?
    │       │
    │       ├─► Run build-with-binlog.ps1
    │       │       │
    │       │       └─► Analyze binlog for XamlCompiler.exe invocation
    │       │               │
    │       │               ├─► Nested Views detected? → Flatten or enable EnableViewsFlattener
    │       │               │
    │       │               ├─► TextElement.* on ContentPresenter? → Remove attached property
    │       │               │
    │       │               └─► Unknown? → Run xaml-binary-search.ps1
    │       │
    │       └─► No XamlCompiler invocation found? → Build failed before XAML phase
    │
    ├─► WMC9999 error?
    │       │
    │       └─► Ensure UseXamlCompilerExecutable=true in Directory.Build.targets
    │
    ├─► MSB3030 "file was not found"?
    │       │
    │       └─► XAML not copied to obj/ → Check EnsureXamlInObj target
    │
    └─► Specific error code?
            │
            └─► Search error code in docs/issues/ or GitHub issues
```

---

## Common Failure Patterns

| Symptom | Cause | Fix |
|---------|-------|-----|
| Exit code 1, no output.json | XAML in nested Views subfolder | Flatten to Views root OR set `<EnableViewsFlattener>true</EnableViewsFlattener>` |
| Exit code 1, no output.json | TextElement.* on ContentPresenter | Remove attached property, use explicit TextBlock |
| WMC9999 "Unknown error" | In-process compiler failure | Ensure `UseXamlCompilerExecutable=true` |
| MSB3030 "file was not found" | XAML not in obj/ | Check EnsureXamlInObj target in Directory.Build.targets |
| Intermittent failures | File lock contention | Build single-threaded with `-m:1` |
| Animation crash | ObjectAnimationUsingKeyFrames on attached property | Animate direct properties only |

---

## Diagnostic Commands (Copy-Paste Ready)

### 1. Full Diagnostic Build

```powershell
# Clean single-threaded build with binlog capture
.\scripts\build-with-binlog.ps1
```

### 2. Analyze Binlog

```powershell
# Quick summary
.\scripts\analyze-binlog.ps1 -OutputFormat summary

# Full text output
.\scripts\analyze-binlog.ps1 -OutputFormat text

# JSON for programmatic consumption
.\scripts\analyze-binlog.ps1 -OutputFormat json

# Write to file (for CI)
.\scripts\analyze-binlog.ps1 -OutputFormat text -OutputFile .buildlogs\analysis-output.txt
```

### 3. Binary Search for Problematic File

```powershell
# Automatically bisect to find the problematic XAML file
.\scripts\xaml-binary-search.ps1
```

### 4. XAML Lint Check

```powershell
# Check all XAML files for forbidden patterns
python scripts/lint_xaml.py

# Check specific file
python scripts/lint_xaml.py src/VoiceStudio.App/Views/Panels/SettingsView.xaml
```

### 5. Single-Threaded Build (Eliminates Race Conditions)

```powershell
# Build with single thread to eliminate parallel execution issues
dotnet build VoiceStudio.sln -c Debug -p:Platform=x64 -m:1
```

### 6. Clean and Rebuild

```powershell
# Nuclear option: full clean and rebuild
Remove-Item -Recurse -Force .vs, bin, obj -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force src/VoiceStudio.App/bin, src/VoiceStudio.App/obj -ErrorAction SilentlyContinue
dotnet restore
dotnet build VoiceStudio.sln -c Debug -p:Platform=x64 -m:1
```

---

## Forbidden XAML Patterns

These patterns will crash XamlCompiler.exe. Never use them:

### 1. Attached Properties on ContentPresenter

```xml
<!-- FORBIDDEN -->
<ContentPresenter TextElement.Foreground="{TemplateBinding Foreground}" />

<!-- SAFE -->
<ContentPresenter Foreground="{TemplateBinding Foreground}" />
```

### 2. Animations Targeting Attached Properties

```xml
<!-- FORBIDDEN -->
<ObjectAnimationUsingKeyFrames Storyboard.TargetProperty="(TextElement.Foreground)">

<!-- SAFE -->
<ObjectAnimationUsingKeyFrames Storyboard.TargetProperty="Foreground">
```

### 3. Deeply Nested Views Subfolders

```
FORBIDDEN: Views/UI/Panels/MyView.xaml (3+ levels)
SAFE:      Views/Panels/MyView.xaml (2 levels max)
```

---

## Build Configuration Reference

### Required Settings in Directory.Build.targets

```xml
<!-- External compiler (avoids WMC9999) -->
<UseXamlCompilerExecutable>true</UseXamlCompilerExecutable>

<!-- Stability settings -->
<XAMLFingerprint>false</XAMLFingerprint>
<EnableWin32Codegen>false</EnableWin32Codegen>
<UseVCMetaManaged>false</UseVCMetaManaged>
```

### Nested Views Protection

```xml
<!-- Fail-fast: ERROR on nested Views XAML (default: true) -->
<EnableViewsSubfolderError>true</EnableViewsSubfolderError>

<!-- OR: Automatic flattening workaround (opt-in) -->
<EnableViewsFlattener>true</EnableViewsFlattener>
```

---

## CI/CD Behavior

When a build fails in CI:

1. **Binlogs are captured** and uploaded as artifacts (`build-binlogs`)
2. **Binlog analysis runs automatically** on failure
3. **PR comment is posted** with diagnostic information (if PR build)
4. **Download binlog artifact** to debug locally with MSBuild Structured Log Viewer

### Retrieving CI Artifacts

1. Go to the failed workflow run
2. Download `build-binlogs` artifact
3. Open `.binlog` file in [MSBuild Structured Log Viewer](https://msbuildlog.com/)
4. Search for "XamlCompiler" to find the failing task

---

## Emergency Recovery

If you're stuck with a broken build and need to ship:

### Option 1: Revert XAML Changes

```powershell
# Revert all XAML changes to last known good state
git checkout HEAD~1 -- "src/**/*.xaml"
```

### Option 2: Enable Flattener Workaround

Add to `src/VoiceStudio.App/VoiceStudio.App.csproj`:

```xml
<PropertyGroup>
  <EnableViewsFlattener>true</EnableViewsFlattener>
</PropertyGroup>
```

### Option 3: Disable Nested Views Check

Add to `src/VoiceStudio.App/VoiceStudio.App.csproj`:

```xml
<PropertyGroup>
  <EnableViewsSubfolderError>false</EnableViewsSubfolderError>
</PropertyGroup>
```

**Warning:** Option 3 allows silent failures. Only use as temporary measure.

---

## GitHub Issue References

- **#10027**: [Can't get error output from XamlCompiler.exe](https://github.com/microsoft/microsoft-ui-xaml/issues/10027)
- **#10947**: [XamlCompiler.exe exits code 1 for Views subfolders](https://github.com/microsoft/microsoft-ui-xaml/issues/10947)

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [XAML_CHANGE_PROTOCOL.md](../developer/XAML_CHANGE_PROTOCOL.md) | Mandatory procedures for XAML changes |
| [UI_HARDENING_GUIDELINES.md](../developer/UI_HARDENING_GUIDELINES.md) | Best practices for XAML stability |
| [XAML_BUILD_PIPELINE_README.md](XAML_BUILD_PIPELINE_README.md) | Build pipeline technical details |
| [Directory.Build.targets](../../Directory.Build.targets) | MSBuild configuration |

---

## Diagnostic Script Reference

| Script | Purpose |
|--------|---------|
| `scripts/build-with-binlog.ps1` | Clean single-threaded build with binlog |
| `scripts/analyze-binlog.ps1` | Extract XamlCompiler info from binlog |
| `scripts/analyze_binlog.py` | Python alternative for binlog analysis |
| `scripts/xaml-binary-search.ps1` | Binary search to isolate problematic XAML |
| `scripts/lint_xaml.py` | Check XAML for forbidden patterns |
| `tools/xaml-compiler-wrapper.cmd` | Compiler wrapper with false-positive handling |

---

## Quality Ledger Entries

Related issues from the Quality Ledger:

- **VS-0001**: XAML compiler false-positive exit code 1 fix
- **VS-0005**: XAML Page items disabled causing missing XAML copy failures
- **VS-0035**: XAML compiler exits code 1 with no output (WinAppSDK 1.8)
- **VS-0040**: XAML compiler silent crash on TextElement.Foreground attached property
