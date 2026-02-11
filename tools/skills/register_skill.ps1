<#
.SYNOPSIS
    Registers a new skill in the VoiceStudio .cursor/skills directory.

.DESCRIPTION
    Creates the standard skill directory structure with SKILL.md and optional
    invoke.py script. Validates skill metadata and creates boilerplate files.

.PARAMETER Name
    The skill name (kebab-case, e.g., "my-new-skill")

.PARAMETER Category
    The skill category: "roles" or "tools"

.PARAMETER Description
    Short description of the skill (1-2 sentences)

.PARAMETER DisplayName
    Human-readable display name

.PARAMETER WithScript
    Include an invoke.py script template

.PARAMETER Force
    Overwrite existing skill if it exists

.EXAMPLE
    .\register_skill.ps1 -Name "code-analyzer" -Category "tools" -Description "Analyzes code for patterns"

.EXAMPLE
    .\register_skill.ps1 -Name "qa-engineer" -Category "roles" -Description "QA testing role" -WithScript

.NOTES
    Author: VoiceStudio Team
    Version: 1.0.0
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[a-z][a-z0-9-]*[a-z0-9]$")]
    [string]$Name,

    [Parameter(Mandatory = $true)]
    [ValidateSet("roles", "tools")]
    [string]$Category,

    [Parameter(Mandatory = $true)]
    [string]$Description,

    [string]$DisplayName = "",

    [switch]$WithScript,

    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Constants
$SkillsRoot = Join-Path $PSScriptRoot "..\..\..\.cursor\skills"
$TemplatesDir = Join-Path $PSScriptRoot "templates"

# Resolve absolute path
$SkillsRoot = (Resolve-Path $SkillsRoot -ErrorAction SilentlyContinue)?.Path
if (-not $SkillsRoot) {
    $SkillsRoot = Join-Path (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))) ".cursor\skills"
}

# Validate skills root exists
if (-not (Test-Path $SkillsRoot)) {
    Write-Error "Skills root not found: $SkillsRoot"
    exit 1
}

# Derive display name if not provided
if (-not $DisplayName) {
    $DisplayName = ($Name -replace '-', ' ') -replace '(\w)', { $args[0].Value.ToUpper() }
    $DisplayName = $DisplayName.Substring(0,1).ToUpper() + $DisplayName.Substring(1)
}

# Build skill path
$SkillDir = Join-Path $SkillsRoot $Category $Name

# Check if skill already exists
if (Test-Path $SkillDir) {
    if (-not $Force) {
        Write-Error "Skill already exists: $SkillDir. Use -Force to overwrite."
        exit 1
    }
    Write-Warning "Overwriting existing skill: $Name"
}

# Create skill directory
New-Item -ItemType Directory -Path $SkillDir -Force | Out-Null
Write-Host "Created skill directory: $SkillDir" -ForegroundColor Green

# Generate SKILL.md content
$SkillMdContent = @"
# $DisplayName Skill

## Description

$Description

## When to Use

Use this skill when:
- [Describe use cases]

## Usage

``````
@skill-$Category-$Name
``````

## Capabilities

- [List key capabilities]

## Example Prompts

- "Example prompt that triggers this skill"

## Integration

This skill integrates with:
- [List integrations if any]

## Notes

- Created: $(Get-Date -Format "yyyy-MM-dd")
- Category: $Category
- Name: $Name
"@

# Write SKILL.md
$SkillMdPath = Join-Path $SkillDir "SKILL.md"
Set-Content -Path $SkillMdPath -Value $SkillMdContent -Encoding UTF8
Write-Host "Created: $SkillMdPath" -ForegroundColor Cyan

# Create scripts directory and invoke.py if requested
if ($WithScript) {
    $ScriptsDir = Join-Path $SkillDir "scripts"
    New-Item -ItemType Directory -Path $ScriptsDir -Force | Out-Null

    $InvokePyContent = @"
"""
$DisplayName Skill Invoke Script

This script is executed when the skill is invoked.
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="$Description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    result = {
        "skill": "$Name",
        "category": "$Category",
        "status": "ok",
        "data": {},
    }

    # TODO: Implement skill logic here

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[$Name] Skill executed successfully")

    return 0


if __name__ == "__main__":
    sys.exit(main())
"@

    $InvokePyPath = Join-Path $ScriptsDir "invoke.py"
    Set-Content -Path $InvokePyPath -Value $InvokePyContent -Encoding UTF8
    Write-Host "Created: $InvokePyPath" -ForegroundColor Cyan
}

# Create __init__.py if scripts were created
if ($WithScript) {
    $InitPath = Join-Path $SkillDir "scripts\__init__.py"
    Set-Content -Path $InitPath -Value "# $DisplayName skill scripts" -Encoding UTF8
}

# Summary
Write-Host ""
Write-Host "Skill registered successfully!" -ForegroundColor Green
Write-Host "  Name:     $Name" -ForegroundColor White
Write-Host "  Category: $Category" -ForegroundColor White
Write-Host "  Path:     $SkillDir" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Edit SKILL.md to add detailed documentation"
if ($WithScript) {
    Write-Host "  2. Implement logic in scripts/invoke.py"
}
Write-Host ""
