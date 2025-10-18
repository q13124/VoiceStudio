$OutDir = Join-Path (Get-Location) "logs"
$Report = Join-Path $OutDir "change-audit.md"

$content = @()
$content += "# VoiceStudio Change Audit"
$content += "Generated: $(Get-Date -Format s)"
$content += "Repo: $(Get-Location)"
$content += ""

$content += "## Git status"
$content += "``````"
$gitStatus = git status -s 2>$null
if ($gitStatus) {
    $content += $gitStatus
}
$content += "``````"
$content += ""

$content += "## Endpoint health"
$content += "``````"
$endpoints = @(
    "http://127.0.0.1:5080/health",
    "http://127.0.0.1:5080/autofix/status",
    "http://127.0.0.1:5080/discovery",
    "http://127.0.0.1:5080/metrics",
    "http://127.0.0.1:5081/health",
    "http://127.0.0.1:5081/status",
    "http://127.0.0.1:5090/health",
    "http://127.0.0.1:5090/settings",
    "http://127.0.0.1:5090/weights"
)
foreach ($url in $endpoints) {
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        $content += "$url  ->  $($resp.StatusCode)  $($resp.StatusDescription)"
    } catch {
        if ($null -ne $_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            $statusDesc = $_.Exception.Response.StatusDescription
            $content += "$url  ->  $statusCode  $statusDesc"
        } else {
            $content += "$url  ->  0  Connection refused"
        }
    }
}
$content += "``````"

Set-Content -Encoding UTF8 $Report ($content -join "`n")
Write-Host "Wrote $Report" -ForegroundColor Green
