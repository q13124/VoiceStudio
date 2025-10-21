param(
    [string]$OutDir = "$(Join-Path $env:ProgramData 'VoiceStudio\artifacts\sbom')"
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "== SBOM: .NET (CycloneDX) ==" -ForegroundColor Cyan
try {
    dotnet tool update --global CycloneDX | Out-Null
}
catch {
    dotnet tool install --global CycloneDX | Out-Null
}
$env:PATH = "$env:PATH;$([Environment]::GetFolderPath('UserProfile'))\.dotnet\tools"

# Generate for each .csproj we find
Get-ChildItem -Path (Get-Location) -Recurse -Filter *.csproj | ForEach-Object {
    $proj = $_.FullName
    Write-Host "  - $proj"
    & dotnet CycloneDX "$proj" -o $OutDir --output-format Json | Out-Null
}

Write-Host "== SBOM: Python (cyclonedx-bom) ==" -ForegroundColor Cyan
$py = "$env:ProgramData\VoiceStudio\pyenv\Scripts\python.exe"
if (!(Test-Path $py)) { throw "Python venv not found at $py" }
& $py -m pip install --upgrade cyclonedx-bom > $null
# Try from requirements file
$req = Join-Path $env:ProgramData 'VoiceStudio\requirements-engines.txt'
if (Test-Path $req) {
    & $py -m cyclonedx_py requirements $req --output-file (Join-Path $OutDir 'python-requirements.bom.json')
}
# Try site-packages inventory
& $py -m cyclonedx_py environment --output-file (Join-Path $OutDir 'python-sitepackages.bom.json')

Write-Host "SBOM written to $OutDir" -ForegroundColor Green
