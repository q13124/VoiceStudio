<# 
VoiceStudio-QualityReport-Demo.ps1
- Demonstrates calling the quality_report stub
- Assumes Python package layout under ProjectRoot/app
#>
[CmdletBinding()]
param(
  [string]$ProjectRoot = $(Join-Path $env:USERPROFILE "VoiceStudio")
)

$ErrorActionPreference = 'Stop'

function Write-OK($m){ Write-Host "[OK]   $m" -ForegroundColor Green }
function Write-Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Err($m){ Write-Error $m }

$venvPy = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if(-not (Test-Path $venvPy)){ Write-Err "Venv python not found at $venvPy. Run the installer script first."; exit 1 }

# Make a small runner
$runner = Join-Path $ProjectRoot "app\core\pipelines\_qr_demo.py"
@"
from app.core.pipelines.quality_report import analyze, AudioIn
print(analyze(AudioIn(samples=b'0'*44100, sample_rate=44100, channels=1)))
"@ | Set-Content -Path $runner -Encoding UTF8

Push-Location $ProjectRoot
try{
  & $venvPy $runner
} finally {
  Pop-Location
}
