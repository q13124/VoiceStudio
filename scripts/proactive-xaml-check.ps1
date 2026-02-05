<#
.SYNOPSIS
    Proactive XAML health check that runs even on successful builds.

.DESCRIPTION
    This script performs proactive analysis to detect potential XAML issues
    before they cause silent build failures. It can be run:
    - As a pre-commit hook
    - In CI on every build (not just failures)
    - Manually during development
    
    Checks performed:
    1. Nested Views subfolder detection (GitHub #10947)
    2. Missing x:DataType on DataTemplates
    3. {Binding} without ElementName (prefer {x:Bind})
    4. Missing d:DataContext for design-time support
    5. AI safety comment presence

.PARAMETER Path
    Path to the XAML files to check. Default: src/VoiceStudio.App

.PARAMETER OutputFile
    Optional path to write JSON results for CI consumption.

.PARAMETER FailOnWarnings
    If specified, exit with code 1 if any warnings are found.

.EXAMPLE
    .\scripts\proactive-xaml-check.ps1
    # Runs all checks on default path

.EXAMPLE
    .\scripts\proactive-xaml-check.ps1 -FailOnWarnings -OutputFile .buildlogs/xaml-health.json
    # CI mode with JSON output
#>

Param(
    [string]$Path = "src/VoiceStudio.App",
    [string]$OutputFile = "",
    [switch]$FailOnWarnings
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ============================================================================
# Configuration
# ============================================================================

$repoRoot = Resolve-Path "$PSScriptRoot\.."
if ($repoRoot -is [System.Management.Automation.PathInfo]) {
    $repoRoot = $repoRoot.Path
}

$targetPath = Join-Path $repoRoot $Path

$results = @{
    Timestamp = (Get-Date).ToString("o")
    Path = $targetPath
    TotalFiles = 0
    Issues = @()
    Warnings = @()
    Passed = @()
    Summary = @{
        NestedViews = 0
        MissingDataType = 0
        LegacyBinding = 0
        MissingDesignContext = 0
        MissingAIGuidelines = 0
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  VoiceStudio Proactive XAML Health Check" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target: $targetPath" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# Check 1: Nested Views subfolders (GitHub #10947)
# ============================================================================

Write-Host "Check 1: Nested Views subfolders (GitHub #10947)..." -ForegroundColor Yellow

$viewsPath = Join-Path $targetPath "Views"
if (Test-Path $viewsPath) {
    $nestedXaml = Get-ChildItem -Recurse -Filter "*.xaml" -Path $viewsPath -ErrorAction SilentlyContinue |
        Where-Object { $_.DirectoryName -match "Views\\[^\\]+\\[^\\]+" }
    
    if ($nestedXaml) {
        foreach ($file in $nestedXaml) {
            $issue = @{
                Check = "NestedViews"
                Severity = "ERROR"
                File = $file.FullName
                Message = "XAML in deeply nested Views subfolder - may cause silent XamlCompiler failure"
                Fix = "Move to Views/ root or Views/{Category}/ (max 1 level deep)"
            }
            $results.Issues += $issue
            $results.Summary.NestedViews++
            Write-Host "  ERROR: $($file.FullName)" -ForegroundColor Red
        }
    } else {
        Write-Host "  PASS: No deeply nested Views subfolders" -ForegroundColor Green
        $results.Passed += "No deeply nested Views subfolders"
    }
} else {
    Write-Host "  SKIP: Views folder not found" -ForegroundColor Gray
}

# ============================================================================
# Check 2: DataTemplates without x:DataType
# ============================================================================

Write-Host ""
Write-Host "Check 2: DataTemplates missing x:DataType..." -ForegroundColor Yellow

$xamlFiles = Get-ChildItem -Recurse -Filter "*.xaml" -Path $targetPath -ErrorAction SilentlyContinue
$results.TotalFiles = $xamlFiles.Count

foreach ($file in $xamlFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        
        # Find DataTemplates without x:DataType
        $dataTemplates = [regex]::Matches($content, '<DataTemplate[^>]*>')
        foreach ($match in $dataTemplates) {
            if ($match.Value -notmatch 'x:DataType\s*=') {
                $lineNumber = ($content.Substring(0, $match.Index) -split "`n").Count
                $warning = @{
                    Check = "MissingDataType"
                    Severity = "WARNING"
                    File = $file.FullName
                    Line = $lineNumber
                    Message = "DataTemplate without x:DataType - no compile-time binding validation"
                    Fix = "Add x:DataType=""namespace:TypeName"" to enable compile-time checking"
                }
                $results.Warnings += $warning
                $results.Summary.MissingDataType++
            }
        }
    } catch {
        # Skip files that can't be read
    }
}

if ($results.Summary.MissingDataType -eq 0) {
    Write-Host "  PASS: All DataTemplates have x:DataType" -ForegroundColor Green
    $results.Passed += "All DataTemplates have x:DataType"
} else {
    Write-Host "  WARNING: Found $($results.Summary.MissingDataType) DataTemplates without x:DataType" -ForegroundColor Yellow
}

# ============================================================================
# Check 3: {Binding} without ElementName (should prefer {x:Bind})
# ============================================================================

Write-Host ""
Write-Host "Check 3: Legacy {Binding} usage (prefer {x:Bind})..." -ForegroundColor Yellow

foreach ($file in $xamlFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        
        # Find {Binding} that doesn't use ElementName (legacy pattern)
        # Exclude: {Binding ElementName=...} and {Binding RelativeSource=...}
        $bindings = [regex]::Matches($content, '\{Binding\s+[^}]+\}')
        foreach ($match in $bindings) {
            $bindingText = $match.Value
            # Skip if it has ElementName or RelativeSource (legitimate uses)
            if ($bindingText -match 'ElementName\s*=' -or $bindingText -match 'RelativeSource\s*=') {
                continue
            }
            # Skip if it's in a Run element (WinUI 3 limitation)
            $contextStart = [Math]::Max(0, $match.Index - 50)
            $context = $content.Substring($contextStart, [Math]::Min(100, $content.Length - $contextStart))
            if ($context -match '<Run[^>]*Text\s*=') {
                continue
            }
            
            $lineNumber = ($content.Substring(0, $match.Index) -split "`n").Count
            $warning = @{
                Check = "LegacyBinding"
                Severity = "INFO"
                File = $file.FullName
                Line = $lineNumber
                Message = "Legacy {Binding} - prefer {x:Bind} for compile-time checking"
                Binding = $bindingText.Substring(0, [Math]::Min(60, $bindingText.Length))
            }
            $results.Warnings += $warning
            $results.Summary.LegacyBinding++
        }
    } catch {
        # Skip files that can't be read
    }
}

if ($results.Summary.LegacyBinding -eq 0) {
    Write-Host "  PASS: No unnecessary legacy {Binding} patterns" -ForegroundColor Green
    $results.Passed += "No unnecessary legacy {Binding} patterns"
} else {
    Write-Host "  INFO: Found $($results.Summary.LegacyBinding) legacy {Binding} usages (may be intentional)" -ForegroundColor Cyan
}

# ============================================================================
# Check 4: Missing d:DataContext for design-time support
# ============================================================================

Write-Host ""
Write-Host "Check 4: Missing d:DataContext (design-time support)..." -ForegroundColor Yellow

foreach ($file in $xamlFiles) {
    # Only check main Views (not resource dictionaries or controls)
    if ($file.Name -notmatch "View\.xaml$") { continue }
    
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $content) { continue }
        
        # Check for d:DataContext
        if ($content -notmatch 'd:DataContext\s*=') {
            $warning = @{
                Check = "MissingDesignContext"
                Severity = "INFO"
                File = $file.FullName
                Message = "View missing d:DataContext - no design-time data preview"
                Fix = "Add d:DataContext=""{d:DesignInstance Type=vm:ViewModelType, IsDesignTimeCreatable=False}"""
            }
            $results.Warnings += $warning
            $results.Summary.MissingDesignContext++
        }
    } catch {
        # Skip files that can't be read
    }
}

if ($results.Summary.MissingDesignContext -eq 0) {
    Write-Host "  PASS: All Views have d:DataContext" -ForegroundColor Green
    $results.Passed += "All Views have d:DataContext"
} else {
    Write-Host "  INFO: Found $($results.Summary.MissingDesignContext) Views without d:DataContext" -ForegroundColor Cyan
}

# ============================================================================
# Check 5: AI safety guidelines comments
# ============================================================================

Write-Host ""
Write-Host "Check 5: AI safety guidelines comments..." -ForegroundColor Yellow

$majorViews = @(
    "VoiceSynthesisView.xaml",
    "VoiceCloningWizardView.xaml",
    "EffectsMixerView.xaml",
    "SettingsView.xaml",
    "ProfilesView.xaml",
    "QualityControlView.xaml",
    "RealTimeVoiceConverterView.xaml"
)

foreach ($viewName in $majorViews) {
    $viewFile = $xamlFiles | Where-Object { $_.Name -eq $viewName } | Select-Object -First 1
    if ($viewFile) {
        try {
            $content = Get-Content $viewFile.FullName -Raw -ErrorAction SilentlyContinue
            if ($content -and $content -notmatch 'AI GUIDELINES:') {
                $warning = @{
                    Check = "MissingAIGuidelines"
                    Severity = "INFO"
                    File = $viewFile.FullName
                    Message = "Major View missing AI GUIDELINES comment block"
                    Fix = "Add <!-- AI GUIDELINES: ... --> comment at top of file"
                }
                $results.Warnings += $warning
                $results.Summary.MissingAIGuidelines++
            }
        } catch {
            # Skip files that can't be read
        }
    }
}

if ($results.Summary.MissingAIGuidelines -eq 0) {
    Write-Host "  PASS: All major Views have AI safety guidelines" -ForegroundColor Green
    $results.Passed += "All major Views have AI safety guidelines"
} else {
    Write-Host "  INFO: Found $($results.Summary.MissingAIGuidelines) major Views without AI guidelines" -ForegroundColor Cyan
}

# ============================================================================
# Results Summary
# ============================================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  XAML HEALTH CHECK SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$totalIssues = $results.Issues.Count
$totalWarnings = $results.Warnings.Count

Write-Host "Total XAML files scanned: $($results.TotalFiles)"
Write-Host "Errors  : $totalIssues" -ForegroundColor $(if ($totalIssues -gt 0) { "Red" } else { "Green" })
Write-Host "Warnings: $totalWarnings" -ForegroundColor $(if ($totalWarnings -gt 0) { "Yellow" } else { "Green" })
Write-Host "Passed  : $($results.Passed.Count)" -ForegroundColor Green
Write-Host ""

if ($totalIssues -gt 0) {
    Write-Host "ERRORS (must fix):" -ForegroundColor Red
    foreach ($issue in $results.Issues) {
        Write-Host "  - [$($issue.Check)] $($issue.File)" -ForegroundColor Red
        Write-Host "    $($issue.Message)" -ForegroundColor Yellow
        if ($issue.Fix) {
            Write-Host "    Fix: $($issue.Fix)" -ForegroundColor Cyan
        }
    }
    Write-Host ""
}

# Output to file if specified
if ($OutputFile -and $OutputFile.Trim() -ne "") {
    $outputDir = Split-Path $OutputFile -Parent
    if ($outputDir -and -not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }
    
    $results | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputFile -Encoding UTF8
    Write-Host "Results written to: $OutputFile" -ForegroundColor Gray
}

# Exit code
if ($totalIssues -gt 0) {
    Write-Host "FAILED: $totalIssues error(s) found" -ForegroundColor Red
    exit 1
} elseif ($FailOnWarnings -and $totalWarnings -gt 0) {
    Write-Host "FAILED: $totalWarnings warning(s) found (FailOnWarnings enabled)" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "PASSED: XAML health check complete" -ForegroundColor Green
    exit 0
}
