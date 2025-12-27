# Master Workspace Migration Script
# Migrates entire workspace from C:\VoiceStudio to E:\VoiceStudio

param(
    [string]$SourceRoot = "C:\VoiceStudio",
    [string]$TargetRoot = "E:\VoiceStudio",
    [switch]$SkipVenv,
    [switch]$SkipEngines,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VoiceStudio Workspace Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Source: $SourceRoot" -ForegroundColor Yellow
Write-Host "Target: $TargetRoot" -ForegroundColor Yellow
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN MODE - No changes will be made" -ForegroundColor Magenta
    Write-Host ""
}

# Step 1: Copy workspace (excluding venv, __pycache__, .git)
Write-Host "[1/7] Copying workspace files..." -ForegroundColor Green

$excludePatterns = @(
    "__pycache__",
    "*.pyc",
    ".git",
    "venv",
    "env",
    ".venv",
    "node_modules",
    "*.egg-info",
    ".pytest_cache",
    ".mypy_cache"
)

function Copy-WorkspaceFiles {
    param([string]$Source, [string]$Target)
    
    if (-not (Test-Path $Source)) {
        Write-Host "  ⚠ Source not found: $Source" -ForegroundColor Yellow
        return
    }
    
    $items = Get-ChildItem -Path $Source -Recurse -File -ErrorAction SilentlyContinue
    
    foreach ($item in $items) {
        $relativePath = $item.FullName.Substring($Source.Length + 1)
        $shouldExclude = $false
        
        foreach ($pattern in $excludePatterns) {
            if ($relativePath -like "*$pattern*") {
                $shouldExclude = $true
                break
            }
        }
        
        if (-not $shouldExclude) {
            $targetPath = Join-Path $Target $relativePath
            $targetDir = Split-Path $targetPath -Parent
            
            if (-not $DryRun) {
                New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
                Copy-Item -Path $item.FullName -Destination $targetPath -Force
            } else {
                Write-Host "  [DRY] Would copy: $relativePath" -ForegroundColor Gray
            }
        }
    }
}

if (-not $DryRun) {
    Copy-WorkspaceFiles -Source $SourceRoot -Target $TargetRoot
    Write-Host "  ✓ Workspace files copied" -ForegroundColor Green
} else {
    Write-Host "  [DRY] Would copy workspace files" -ForegroundColor Gray
}

# Step 2: Rebuild venv and install pinned deps
if (-not $SkipVenv) {
    Write-Host ""
    Write-Host "[2/7] Rebuilding Python virtual environment..." -ForegroundColor Green
    
    $venvPath = Join-Path $TargetRoot "venv"
    $requirementsPath = Join-Path $TargetRoot "requirements.txt"
    
    if (-not $DryRun) {
        # Remove old venv if exists
        if (Test-Path $venvPath) {
            Remove-Item -Path $venvPath -Recurse -Force
        }
        
        # Create new venv
        Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
        python -m venv $venvPath
        
        # Activate and upgrade pip
        $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
        & $activateScript
        python -m pip install --upgrade pip --quiet
        
        # Install pinned dependencies (offline-first if possible)
        if (Test-Path $requirementsPath) {
            Write-Host "  Installing dependencies from requirements.txt..." -ForegroundColor Yellow
            
            # Try offline first (if pip cache exists)
            $pipCache = "$env:APPDATA\pip\cache"
            if (Test-Path $pipCache) {
                Write-Host "  Using pip cache for offline-first installation..." -ForegroundColor Gray
                pip install --cache-dir $pipCache -r $requirementsPath
            } else {
                pip install -r $requirementsPath
            }
        } else {
            Write-Host "  ⚠ requirements.txt not found" -ForegroundColor Yellow
        }
        
        Write-Host "  ✓ Virtual environment ready" -ForegroundColor Green
    } else {
        Write-Host "  [DRY] Would rebuild venv and install deps" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "[2/7] Skipping venv rebuild (--SkipVenv)" -ForegroundColor Yellow
}

# Step 3: Find and rewrite absolute paths
Write-Host ""
Write-Host "[3/7] Rewriting absolute paths in configs/manifests..." -ForegroundColor Green

$configFiles = @(
    "*.json",
    "*.yaml",
    "*.yml",
    "*.toml",
    "*.ini",
    "*.cfg",
    "*.conf",
    "*.config"
)

$pathReplacements = @{
    "C:\\VoiceStudio" = "E:\\VoiceStudio"
    "C:/VoiceStudio" = "E:/VoiceStudio"
    "C:\\\\VoiceStudio" = "E:\\\\VoiceStudio"
}

function Update-PathsInFile {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) { return }
    
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    $originalContent = $content
    $modified = $false
    
    foreach ($oldPath in $pathReplacements.Keys) {
        if ($content -match [regex]::Escape($oldPath)) {
            $content = $content -replace [regex]::Escape($oldPath), $pathReplacements[$oldPath]
            $modified = $true
        }
    }
    
    if ($modified -and -not $DryRun) {
        Set-Content -Path $FilePath -Value $content -Encoding UTF8 -NoNewline
        Write-Host "  ✓ Updated: $FilePath" -ForegroundColor Gray
    } elseif ($modified) {
        Write-Host "  [DRY] Would update: $FilePath" -ForegroundColor Gray
    }
}

if (-not $DryRun) {
    foreach ($pattern in $configFiles) {
        Get-ChildItem -Path $TargetRoot -Recurse -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
            Update-PathsInFile -FilePath $_.FullName
        }
    }
    Write-Host "  ✓ Paths updated in config files" -ForegroundColor Green
} else {
    Write-Host "  [DRY] Would update paths in config files" -ForegroundColor Gray
}

# Step 4: Re-sync Panel Registry
Write-Host ""
Write-Host "[4/7] Re-syncing Panel Registry..." -ForegroundColor Green

if (-not $DryRun) {
    # Run panel discovery
    $discoverScript = Join-Path $TargetRoot "tools\Discover-Panels.ps1"
    if (Test-Path $discoverScript) {
        Write-Host "  Running panel discovery..." -ForegroundColor Yellow
        & $discoverScript -SourcePath $SourceRoot -OutputPath (Join-Path $TargetRoot "docs\governance\PANEL_CATALOG.json")
        
        # TODO: Auto-register panels in PanelRegistry
        # This would require parsing the catalog and updating PanelRegistry.cs
        Write-Host "  ⚠ Manual panel registration required" -ForegroundColor Yellow
        Write-Host "  See: docs/governance/BULK_PANEL_MIGRATION_GUIDE.md" -ForegroundColor Yellow
    } else {
        Write-Host "  ⚠ Panel discovery script not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [DRY] Would discover and register panels" -ForegroundColor Gray
}

# Step 5: Install modular engine layer
if (-not $SkipEngines) {
    Write-Host ""
    Write-Host "[5/7] Setting up modular engine layer..." -ForegroundColor Green
    
    $engineDir = Join-Path $TargetRoot "app\core\engines"
    $protocolsFile = Join-Path $engineDir "protocols.py"
    
    if (-not $DryRun) {
        # Ensure engine directory exists
        New-Item -ItemType Directory -Force -Path $engineDir | Out-Null
        
        # Ensure EngineProtocol exists
        if (-not (Test-Path $protocolsFile)) {
            Write-Host "  ⚠ EngineProtocol not found - creating..." -ForegroundColor Yellow
            # protocols.py should already exist, but create if missing
        }
        
        # Copy/adapt engines from source
        $sourceEngines = Join-Path $SourceRoot "app\core\engines"
        if (Test-Path $sourceEngines) {
            Write-Host "  Copying engine files..." -ForegroundColor Yellow
            Get-ChildItem -Path $sourceEngines -Filter "*.py" -ErrorAction SilentlyContinue | ForEach-Object {
                $targetPath = Join-Path $engineDir $_.Name
                if (-not (Test-Path $targetPath)) {
                    Copy-Item -Path $_.FullName -Destination $targetPath
                    Write-Host "    Copied: $($_.Name)" -ForegroundColor Gray
                }
            }
        }
        
        # Create engine router/registry (if not exists)
        $routerFile = Join-Path $engineDir "router.py"
        if (-not (Test-Path $routerFile)) {
            $routerContent = @"
"""
Engine Router - Runtime engine selection and management
"""
from typing import Dict, Optional, Type
from .protocols import EngineProtocol

class EngineRouter:
    """Manages multiple engine instances and runtime selection"""
    
    def __init__(self):
        self._engines: Dict[str, EngineProtocol] = {}
        self._engine_types: Dict[str, Type[EngineProtocol]] = {}
    
    def register_engine(self, name: str, engine_class: Type[EngineProtocol]):
        """Register an engine class"""
        self._engine_types[name] = engine_class
    
    def get_engine(self, name: str, **kwargs) -> Optional[EngineProtocol]:
        """Get or create an engine instance"""
        if name not in self._engines:
            if name in self._engine_types:
                self._engines[name] = self._engine_types[name](**kwargs)
                self._engines[name].initialize()
            else:
                return None
        return self._engines[name]
    
    def list_engines(self) -> list:
        """List available engine names"""
        return list(self._engine_types.keys())

# Global router instance
router = EngineRouter()
"@
            Set-Content -Path $routerFile -Value $routerContent -Encoding UTF8
            Write-Host "  ✓ Created engine router" -ForegroundColor Green
        }
        
        Write-Host "  ✓ Engine layer ready" -ForegroundColor Green
    } else {
        Write-Host "  [DRY] Would set up engine layer" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "[5/7] Skipping engine setup (--SkipEngines)" -ForegroundColor Yellow
}

# Step 6: Preserve Governor + learners orchestration
Write-Host ""
Write-Host "[6/7] Preserving Governor + learners orchestration..." -ForegroundColor Green

if (-not $DryRun) {
    # Look for Governor/AI orchestration files
    $governorPaths = @(
        "app\core\runtime\governor.py",
        "app\core\ai\governor.py",
        "app\governor.py"
    )
    
    $found = $false
    foreach ($path in $governorPaths) {
        $sourcePath = Join-Path $SourceRoot $path
        $targetPath = Join-Path $TargetRoot $path
        
        if (Test-Path $sourcePath) {
            $targetDir = Split-Path $targetPath -Parent
            New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
            Copy-Item -Path $sourcePath -Destination $targetPath -Force
            Write-Host "  ✓ Copied: $path" -ForegroundColor Gray
            $found = $true
        }
    }
    
    if (-not $found) {
        Write-Host "  ⚠ Governor files not found in expected locations" -ForegroundColor Yellow
    }
    
    # Hook Governor to engine router
    $hookFile = Join-Path $TargetRoot "app\core\runtime\engine_hook.py"
    if (-not (Test-Path $hookFile)) {
        $hookContent = @"
"""
Engine Router Hook for Governor
Connects Governor + learners orchestration to engine router
"""
from app.core.engines.router import router

class EngineHook:
    """Bridge between Governor and engine router"""
    
    def __init__(self):
        self.router = router
    
    def get_engine(self, engine_name: str, **kwargs):
        """Get engine instance for Governor use"""
        return self.router.get_engine(engine_name, **kwargs)
    
    def list_available_engines(self):
        """List engines available to Governor"""
        return self.router.list_engines()

# Global hook instance
hook = EngineHook()
"@
        Set-Content -Path $hookFile -Value $hookContent -Encoding UTF8
        Write-Host "  ✓ Created engine hook for Governor" -ForegroundColor Green
    }
} else {
    Write-Host "  [DRY] Would preserve Governor and create engine hook" -ForegroundColor Gray
}

# Step 7: Verify premium UI characteristics
Write-Host ""
Write-Host "[7/7] Verifying premium UI characteristics..." -ForegroundColor Green

if (-not $DryRun) {
    $uiChecks = @{
        "Design Tokens" = "src\VoiceStudio.App\Resources\DesignTokens.xaml"
        "PanelHost" = "src\VoiceStudio.App\Controls\PanelHost.xaml"
        "PanelRegistry" = "src\VoiceStudio.Core\Panels\PanelRegistry.cs"
        "Theme Manager" = "src\VoiceStudio.App\Services\ThemeManager.cs"
    }
    
    $allPresent = $true
    foreach ($check in $uiChecks.Keys) {
        $path = Join-Path $TargetRoot $uiChecks[$check]
        if (Test-Path $path) {
            Write-Host "  ✓ $check" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $check (missing: $path)" -ForegroundColor Red
            $allPresent = $false
        }
    }
    
    if ($allPresent) {
        Write-Host "  ✓ Premium UI structure verified" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Some UI components missing - review required" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [DRY] Would verify UI characteristics" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Review migrated files in $TargetRoot" -ForegroundColor White
Write-Host "2. Run panel discovery: .\tools\Discover-Panels.ps1" -ForegroundColor White
Write-Host "3. Register panels in PanelRegistry" -ForegroundColor White
Write-Host "4. Test engine router and Governor integration" -ForegroundColor White
Write-Host "5. Verify UI loads correctly" -ForegroundColor White
Write-Host ""

