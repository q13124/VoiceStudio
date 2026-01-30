# VoiceStudio Git Hooks Setup Script
# Installs pre-commit and commit-msg hooks for commit discipline
#
# Usage: .\tools\setup-git-hooks.ps1

$ErrorActionPreference = "Stop"

Write-Host "VoiceStudio Git Hooks Setup" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

$RepoRoot = Split-Path -Parent $PSScriptRoot
$HooksDir = Join-Path $RepoRoot ".git\hooks"
$ToolsHooksDir = Join-Path $RepoRoot "tools\git-hooks"

if (-not (Test-Path $HooksDir)) {
    Write-Host "ERROR: .git/hooks directory not found. Are you in a git repository?" -ForegroundColor Red
    exit 1
}

# Define hooks to install
$hooks = @(
    @{ Name = "pre-commit"; Description = "Checks for secrets, large files, syntax errors" }
    @{ Name = "commit-msg"; Description = "Validates Conventional Commits format" }
)

Write-Host "Installing git hooks..."
Write-Host ""

foreach ($hook in $hooks) {
    $srcPath = Join-Path $ToolsHooksDir $hook.Name
    $destPath = Join-Path $HooksDir $hook.Name
    
    if (Test-Path $srcPath) {
        Copy-Item -Path $srcPath -Destination $destPath -Force
        Write-Host "  [INSTALLED] $($hook.Name): $($hook.Description)" -ForegroundColor Green
    } else {
        Write-Host "  [SKIPPED] $($hook.Name): Source file not found" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Git hooks installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Hooks will run automatically on:" -ForegroundColor Cyan
Write-Host "  - pre-commit: Before each commit (checks secrets, syntax)"
Write-Host "  - commit-msg: Validates Conventional Commits format"
Write-Host ""
Write-Host "To bypass hooks (not recommended): git commit --no-verify"
