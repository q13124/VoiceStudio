param(
  [Parameter(Mandatory=$true)][string]$JsonPath,
  [string]$KeyDir = "$env:ProgramData\VoiceStudio\keys"
)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force -Path $KeyDir | Out-Null
$priv = Join-Path $KeyDir 'ed25519.key'
$pub  = Join-Path $KeyDir 'ed25519.pub'

# Provide a C# wrapper over .NET 8 Ed25519 Span-based APIs for PowerShell
$code = @"
using System;
using System.Security.Cryptography;

public static class Ed25519Helper
{
    public static byte[] GeneratePrivateKey(out byte[] publicKey)
    {
        publicKey = new byte[32];
        var privateKey = new byte[64];
        Ed25519.GenerateKey(publicKey, privateKey);
        return privateKey;
    }

    public static byte[] Sign(byte[] data, byte[] privateKey)
    {
        var sig = new byte[64];
        Ed25519.Sign(data, privateKey, sig);
        return sig;
    }

    public static bool Verify(byte[] data, byte[] signature, byte[] publicKey)
    {
        return Ed25519.Verify(signature, data, publicKey);
    }
}
"@

try { Add-Type -TypeDefinition $code -Language CSharp -ErrorAction Stop } catch { }
if(-not ([type]::GetType('Ed25519Helper'))){
  throw "Ed25519 not available. Use PowerShell 7.4+ / .NET 8+."
}

# Generate key if missing
if(!(Test-Path $priv) -or !(Test-Path $pub)){
  $sk = [Ed25519Helper]::GeneratePrivateKey([ref]([byte[]]$pkOut))
  [IO.File]::WriteAllBytes($priv, $sk)
  [IO.File]::WriteAllBytes($pub,  $pkOut)
}

$sk = [IO.File]::ReadAllBytes($priv)
$pk = [IO.File]::ReadAllBytes($pub)
$bytes = [IO.File]::ReadAllBytes($JsonPath)
$sig = [Ed25519Helper]::Sign($bytes, $sk)
$sigPath = "$JsonPath.sig"
[IO.File]::WriteAllBytes($sigPath, $sig)
Write-Host "Signed $JsonPath" -ForegroundColor Green
Write-Host "Sig: $sigPath" -ForegroundColor Green
Write-Host "Pub: $pub" -ForegroundColor Green
