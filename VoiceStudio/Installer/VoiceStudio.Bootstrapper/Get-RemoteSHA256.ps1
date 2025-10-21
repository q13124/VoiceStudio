param(
  [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
  [string[]]$Urls
)

# Compute SHA256 for remote file(s) by streaming download; outputs in sha256sum style
# Usage examples:
#   ./Get-RemoteSHA256.ps1 "https://download.visualstudio.microsoft.com/.../VC_redist.x64.exe"
#   ./Get-RemoteSHA256.ps1 "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

$ErrorActionPreference = 'Stop'

function Get-Sha256FromStream {
  param(
    [Parameter(Mandatory = $true)] [System.IO.Stream]$Stream
  )
  $sha256 = [System.Security.Cryptography.SHA256]::Create()
  try {
    $buffer = New-Object byte[] 8192
    while (($read = $Stream.Read($buffer, 0, $buffer.Length)) -gt 0) {
      $sha256.TransformBlock($buffer, 0, $read, $null, 0) | Out-Null
    }
    $sha256.TransformFinalBlock(@(), 0, 0) | Out-Null
    -join ($sha256.Hash | ForEach-Object { $_.ToString('x2') })
  } finally {
    $sha256.Dispose()
  }
}

function Invoke-GetRemoteSha256 {
  param(
    [Parameter(Mandatory = $true)] [string]$Url
  )

  # Use HttpClient for robust streaming with redirects and TLS
  $handler = New-Object System.Net.Http.HttpClientHandler
  $handler.AllowAutoRedirect = $true
  $handler.AutomaticDecompression = [System.Net.DecompressionMethods]::GZip -bor [System.Net.DecompressionMethods]::Deflate
  $client = [System.Net.Http.HttpClient]::new($handler)
  $client.Timeout = [TimeSpan]::FromMinutes(30)

  try {
    $response = $client.GetAsync($Url, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
    if (-not $response.IsSuccessStatusCode) {
      throw "HTTP $($response.StatusCode) from $Url"
    }
    $stream = $response.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
    try {
      $hash = Get-Sha256FromStream -Stream $stream
      # sha256sum-style: "<hash>  <name>". We print URL as the name.
      Write-Output ("{0}  {1}" -f $hash, $Url)
    } finally {
      $stream.Dispose()
    }
  } finally {
    $client.Dispose()
    $handler.Dispose()
  }
}

foreach ($u in $Urls) {
  try {
    Invoke-GetRemoteSha256 -Url $u
  } catch {
    Write-Error "Failed to compute SHA256 for $u: $_"
  }
}