# Batch Panel Migration Script
# Migrates multiple panels from C:\VoiceStudio to E:\VoiceStudio

param(
    [Parameter(Mandatory=$true)]
    [string[]]$PanelNames,
    
    [string]$SourceRoot = "C:\VoiceStudio",
    [string]$TargetRoot = "E:\VoiceStudio",
    [string]$CatalogPath = "E:\VoiceStudio\docs\governance\PANEL_CATALOG.json"
)

Write-Host "Batch Panel Migration" -ForegroundColor Cyan
Write-Host "Migrating $($PanelNames.Count) panels..." -ForegroundColor Yellow

$results = @()

foreach ($panelName in $PanelNames) {
    Write-Host "`nProcessing: $panelName" -ForegroundColor Green
    
    # Load catalog to find panel info
    if (Test-Path $CatalogPath) {
        $catalog = Get-Content $CatalogPath | ConvertFrom-Json
        $panel = $catalog.panels | Where-Object { $_.name -eq $panelName }
        
        if ($panel) {
            $sourcePath = Join-Path $SourceRoot $panel.source
            $targetPath = Join-Path $TargetRoot $panel.target
            
            Write-Host "  Source: $sourcePath" -ForegroundColor Gray
            Write-Host "  Target: $targetPath" -ForegroundColor Gray
            
            if (Test-Path $sourcePath) {
                # Create target directory
                $targetDir = Split-Path $targetPath -Parent
                New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
                
                # Read source file
                $content = Get-Content $sourcePath -Raw -Encoding UTF8
                
                # Basic adaptations (will need manual review)
                $adapted = $content
                
                # Update import paths (example)
                $adapted = $adapted -replace "from ui\.", "from app.ui."
                $adapted = $adapted -replace "import ui\.", "import app.ui."
                
                # Remove C: path references
                $adapted = $adapted -replace "C:\\VoiceStudio", "E:\VoiceStudio"
                $adapted = $adapted -replace "C:/VoiceStudio", "E:/VoiceStudio"
                
                # Save adapted version
                $adapted | Set-Content -Path $targetPath -Encoding UTF8
                
                Write-Host "  ✓ Created: $targetPath" -ForegroundColor Green
                
                $results += @{
                    name = $panelName
                    status = "created"
                    source = $panel.source
                    target = $panel.target
                    note = "Basic adaptation applied - manual review required"
                }
            } else {
                Write-Host "  ✗ Source not found: $sourcePath" -ForegroundColor Red
                $results += @{
                    name = $panelName
                    status = "error"
                    error = "Source file not found"
                }
            }
        } else {
            Write-Host "  ✗ Panel not found in catalog" -ForegroundColor Red
            $results += @{
                name = $panelName
                status = "error"
                error = "Not in catalog"
            }
        }
    } else {
        Write-Host "  ✗ Catalog not found. Run Discover-Panels.ps1 first." -ForegroundColor Red
        break
    }
}

# Summary
Write-Host "`nMigration Summary:" -ForegroundColor Cyan
$created = ($results | Where-Object { $_.status -eq "created" }).Count
$errors = ($results | Where-Object { $_.status -eq "error" }).Count

Write-Host "  Created: $created" -ForegroundColor Green
Write-Host "  Errors: $errors" -ForegroundColor $(if ($errors -gt 0) { "Red" } else { "Green" })

Write-Host "`nNote: All migrated files require manual review and adaptation." -ForegroundColor Yellow
Write-Host "Follow the migration workflow in PANEL_MIGRATION_STRATEGY.md" -ForegroundColor Yellow

