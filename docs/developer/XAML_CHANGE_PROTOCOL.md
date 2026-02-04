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
- [ ] Create a rollback commit point: `git add -A && git commit -m "WIP: pre-XAML-change checkpoint"`

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

### Step 1: Run the Bisect Tool

```powershell
python tools/build/xaml_bisect.py
```

This will automatically find the problematic XAML file.

### Step 2: Run XAML Lint

```powershell
python scripts/lint_xaml.py path/to/problematic.xaml
```

### Step 3: Check Recent Changes

```powershell
git diff HEAD~1 -- "*.xaml"
```

### Step 4: Incremental Rollback

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

## References

- Quality Ledger: VS-0001, VS-0010, VS-0014, VS-0040
- ADR-010: Platform Identity (WinUI 3 decision)
- Error Pattern Retrospective: Section 3.1 (XAML Chain Reaction)

## Change History

| Date | Author | Change |
|------|--------|--------|
| 2026-02-04 | Phase 7 Plan | Initial protocol created from retrospective findings |
