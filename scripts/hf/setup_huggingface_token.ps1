# VoiceStudio HuggingFace Token Setup Script
# Run this script to set up your HuggingFace API token

Write-Host "VoiceStudio HuggingFace API Token Setup" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check if token is already set
$currentToken = [Environment]::GetEnvironmentVariable("HF_TOKEN", "User")
if ($currentToken) {
    Write-Host "Current HF_TOKEN is set to: $currentToken" -ForegroundColor Yellow
    $reset = Read-Host "Do you want to update it? (y/n)"
    if ($reset -ne "y") {
        Write-Host "Keeping existing token." -ForegroundColor Cyan
        exit 0
    }
}

Write-Host ""
Write-Host "To get your HuggingFace token:" -ForegroundColor Cyan
Write-Host "1. Go to: https://huggingface.co/settings/tokens" -ForegroundColor White
Write-Host "2. Create a new token with 'Read' permissions" -ForegroundColor White
Write-Host "3. Copy the token (starts with 'hf_')" -ForegroundColor White
Write-Host ""

$token = Read-Host "Enter your HuggingFace token"

if ($token -match "^hf_[a-zA-Z0-9]+$") {
    # Set as user environment variable (persistent)
    [Environment]::SetEnvironmentVariable("HF_TOKEN", $token, "User")
    [Environment]::SetEnvironmentVariable("HUGGINGFACE_HUB_TOKEN", $token, "User")

    Write-Host ""
    Write-Host "✅ Token set successfully!" -ForegroundColor Green
    Write-Host "Environment variables:" -ForegroundColor Cyan
    Write-Host "  HF_TOKEN=$token" -ForegroundColor White
    Write-Host "  HUGGINGFACE_HUB_TOKEN=$token" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: Restart any running VoiceStudio processes for changes to take effect." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Invalid token format. Token should start with 'hf_' followed by letters and numbers." -ForegroundColor Red
    exit 1
}