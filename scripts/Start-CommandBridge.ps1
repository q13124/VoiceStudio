<#
 Start-CommandBridge.ps1
 A minimal, safe HTTP bridge so a browser page can trigger whitelisted commands on Windows.

 Defaults:
 - Listens on http://127.0.0.1:5088/ (change $BindAddress if you want LAN access)
 - Requires Bearer token (pairing) for /run
 - Allows only whitelisted actions (edit $AllowList to add your own)
 - CORS restricted to $AllowedOrigins

 Tested: PowerShell 5.1+ (no external modules)
#>

[CmdletBinding()]
param(
    [int]$Port = 5088,
    [string]$BindAddress = '127.0.0.1',           # change to '0.0.0.0' ONLY if you understand the risks (then add a firewall rule)
    [string[]]$AllowedOrigins = @('http://localhost:5173', 'http://localhost:3000'), # add your web app origins here
    [string]$DataRoot = "$env:APPDATA\CursorCommandBridge"
)

$ErrorActionPreference = 'Stop'
$nl = [Environment]::NewLine
$prefix = "http://$BindAddress`:$Port/"
$tokenPath = Join-Path $DataRoot 'token.txt'
$logPath = Join-Path $DataRoot 'bridge.log'

# --- Utils ---
function Write-BridgeLog($msg) {
    $ts = (Get-Date).ToString('s')
    "$ts $msg" | Add-Content -Path $logPath -Encoding UTF8
}

# Ensure folders
$null = New-Item -ItemType Directory -Force -Path $DataRoot | Out-Null

# Create or load pairing token
if (Test-Path $tokenPath) {
    $PAIR_TOKEN = Get-Content $tokenPath -Raw
}
else {
    $PAIR_TOKEN = [Guid]::NewGuid().ToString('N')
    Set-Content -Path $tokenPath -Value $PAIR_TOKEN -Encoding UTF8
}

# ---- ALLOW-LISTED COMMANDS (EDIT ME) ----------------------------------------
# Add your own safe commands here. Each key maps to a ScriptBlock that receives
# a single parameter $Body (hashtable) from JSON with optional args.

$RepoRoot = (Test-Path 'C:\VoiceStudio') ? 'C:\VoiceStudio' : ((Test-Path 'C:\TylersVoiceCloner') ? 'C:\TylersVoiceCloner' : 'C:\VoiceStudio')

$AllowList = @{
    'Ping'            = {
        param($Body)
        return @{ ok = $true; echo = $Body.echo; time = (Get-Date).ToString('s') }
    }

    'RunRepoScript'   = {
        param($Body)
        # Runs a script from {RepoRoot}\scripts that exists on disk. Prevents arbitrary paths.
        $name = $Body.name
        if (-not $name) { throw "Missing 'name' for RunRepoScript" }
        if ($name -notmatch '^[A-Za-z0-9._-]+\.ps1$') { throw "Invalid script name." }
        $path = Join-Path $RepoRoot ("scripts\" + $name)
        if (-not (Test-Path $path)) { throw "Script not found: $path" }
        $args = @()
        if ($Body.args -and ($Body.args -is [System.Collections.IEnumerable])) { $args = $Body.args }
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = (Get-Command powershell).Source
        $psi.Arguments = "-ExecutionPolicy Bypass -File `"$path`" " + ($args | ForEach-Object { '"' + ($_ -replace '"', '\"') + '"' } -join ' ')
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.UseShellExecute = $false
        $p = [System.Diagnostics.Process]::Start($psi)
        $p.WaitForExit()
        $out = $p.StandardOutput.ReadToEnd()
        $err = $p.StandardError.ReadToEnd()
        return @{ ok = ($p.ExitCode -eq 0); exitCode = $p.ExitCode; stdout = $out; stderr = $err; script = $path }
    }

    'OpenCursor'      = {
        param($Body)
        # Example: open Cursor/VS Code, adjust path as needed
        $codeExe = "${env:LOCALAPPDATA}\Programs\Microsoft VS Code\Code.exe"
        if (-not (Test-Path $codeExe)) { throw "VS Code not found at $codeExe" }
        $folder = $RepoRoot
        Start-Process -FilePath $codeExe -ArgumentList "`"$folder`""
        return @{ ok = $true; launched = $folder }
    }

    'StartUltraClone' = {
        param($Body)
        # Example: run a known safe launcher in your repo (edit to your actual bootstrap)
        $bootstrap = Join-Path $RepoRoot "UltraClone-SetupAndRun.ps1"
        if (-not (Test-Path $bootstrap)) { throw "Bootstrap not found: $bootstrap" }
        Start-Process -FilePath (Get-Command powershell).Source -ArgumentList "-ExecutionPolicy Bypass -File `"$bootstrap`""
        return @{ ok = $true; started = $bootstrap }
    }
}
# -----------------------------------------------------------------------------

# HttpListener needs URL ACL if not admin. Attempt reservation.
function Ensure-UrlAcl {
    try {
        $listener = New-Object System.Net.HttpListener
        $listener.Prefixes.Add($prefix)
        $listener.Start()
        $listener.Stop()
        $listener.Close()
        return $true
    }
    catch {
        Write-Host "Attempting URL ACL for $prefix (admin required)..." -ForegroundColor Yellow
        $user = "$env:USERDOMAIN\$env:USERNAME"
        $cmd = "http add urlacl url=$prefix user=""$user"""
        Start-Process -FilePath 'netsh' -ArgumentList $cmd -Verb RunAs -Wait
        return $true
    }
}

# CORS helpers
function Add-CorsHeaders([System.Net.HttpListenerResponse]$resp, [string]$origin) {
    if ($origin -and ($AllowedOrigins -contains $origin)) {
        $resp.Headers['Access-Control-Allow-Origin'] = $origin
        $resp.Headers['Vary'] = 'Origin'
    }
    $resp.Headers['Access-Control-Allow-Headers'] = 'authorization, content-type'
    $resp.Headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
}

function Read-JsonBody([System.IO.Stream]$inputStream, [System.Text.Encoding]$enc) {
    $sr = New-Object System.IO.StreamReader($inputStream, $enc)
    $raw = $sr.ReadToEnd()
    if (-not $raw) { return @{} }
    try {
        return ($raw | ConvertFrom-Json -Depth 10) | ForEach-Object { $_ }  # hashtable-like
    }
    catch {
        throw "Invalid JSON body."
    }
}

# Start listener
if (-not (Ensure-UrlAcl)) { throw "Unable to reserve URL for listener." }
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)
$listener.Start()
Write-Host "Command Bridge listening at $prefix" -ForegroundColor Green
Write-Host "Pairing Token (keep secret): $PAIR_TOKEN" -ForegroundColor Yellow
Write-BridgeLog "START at $prefix"

# Request loop
$enc = [System.Text.Encoding]::UTF8
$null = [System.Net.ServicePointManager]::Expect100Continue = $false

try {
    while ($listener.IsListening) {
        $ctx = $listener.GetContext()
        $req = $ctx.Request
        $resp = $ctx.Response
        $origin = $req.Headers['Origin']
        Add-CorsHeaders -resp $resp -origin $origin

        try {
            # Handle preflight
            if ($req.HttpMethod -eq 'OPTIONS') { $resp.StatusCode = 200; $resp.Close(); continue }

            switch ($req.Url.AbsolutePath.ToLower()) {
                '/health' {
                    $payload = @{ ok = $true; bridge = 'CursorCommandBridge'; port = $Port; bind = $BindAddress; repoRoot = $RepoRoot }
                    $bytes = $enc.GetBytes(($payload | ConvertTo-Json -Depth 8))
                    $resp.ContentType = 'application/json'
                    $resp.OutputStream.Write($bytes, 0, $bytes.Length)
                    $resp.StatusCode = 200
                    $resp.Close()
                    continue
                }
                '/pair' {
                    # Return the token so you can paste it into your web app once (or show via QR if you want)
                    $payload = @{ token = $PAIR_TOKEN; note = 'Use as Bearer token in Authorization header.' }
                    $bytes = $enc.GetBytes(($payload | ConvertTo-Json -Depth 5))
                    $resp.ContentType = 'application/json'
                    $resp.OutputStream.Write($bytes, 0, $bytes.Length)
                    $resp.StatusCode = 200
                    $resp.Close()
                    continue
                }
                '/run' {
                    # Auth check
                    $auth = $req.Headers['Authorization']
                    if (-not $auth -or (-not $auth.StartsWith('Bearer '))) { throw "Missing Authorization: Bearer <token>" }
                    $tok = $auth.Substring(7)
                    if ($tok -ne $PAIR_TOKEN) { throw "Invalid token." }

                    $body = @{}
                    if ($req.HasEntityBody) { $body = Read-JsonBody -inputStream $req.InputStream -enc $enc }

                    $action = $body.action
                    if (-not $action) { throw "Missing 'action' in JSON." }
                    if (-not $AllowList.ContainsKey($action)) { throw "Action '$action' not allowed." }

                    Write-BridgeLog "RUN action=$action origin=$origin"
                    $result = & $AllowList[$action] $body
                    $bytes = $enc.GetBytes(($result | ConvertTo-Json -Depth 10))
                    $resp.ContentType = 'application/json'
                    $resp.OutputStream.Write($bytes, 0, $bytes.Length)
                    $resp.StatusCode = 200
                    $resp.Close()
                    continue
                }
                default {
                    $resp.StatusCode = 404
                    $bytes = $enc.GetBytes("{""error"":""Not found""}")
                    $resp.ContentType = 'application/json'
                    $resp.OutputStream.Write($bytes, 0, $bytes.Length)
                    $resp.Close()
                    continue
                }
            }
        }
        catch {
            $msg = $_.Exception.Message
            Write-BridgeLog "ERROR $msg"
            $resp.StatusCode = 400
            $bytes = $enc.GetBytes(("{""error"":""$($msg.Replace('"','\"'))""}"))
            $resp.ContentType = 'application/json'
            $resp.OutputStream.Write($bytes, 0, $bytes.Length)
            $resp.Close()
        }
    }
}
finally {
    $listener.Stop()
    $listener.Close()
    Write-BridgeLog "STOP"
}
