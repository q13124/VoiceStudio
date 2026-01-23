# PowerShell script to fix Hugging Face API endpoint
Write-Host "Fixing Hugging Face API endpoint..." -ForegroundColor Green

# Set environment variables
$env:HF_INFERENCE_API_BASE = "https://router.huggingface.co"
$env:HF_ENDPOINT = "https://router.huggingface.co"

Write-Host "Environment variables set:" -ForegroundColor Yellow
Write-Host "  HF_INFERENCE_API_BASE = $env:HF_INFERENCE_API_BASE"
Write-Host "  HF_ENDPOINT = $env:HF_ENDPOINT"

# Test Python import
Write-Host "`nTesting Python environment..." -ForegroundColor Yellow
try {
  python -c "
import os
print('Python environment variables:')
print('  HF_INFERENCE_API_BASE:', os.environ.get('HF_INFERENCE_API_BASE', 'NOT SET'))
print('  HF_ENDPOINT:', os.environ.get('HF_ENDPOINT', 'NOT SET'))

try:
    from huggingface_hub import InferenceClient
    client = InferenceClient()
    print('✓ InferenceClient created successfully')
except Exception as e:
    print('⚠ InferenceClient test failed:', str(e))
"
}
catch {
  Write-Host "Python test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nFix completed! You can now start VoiceStudio." -ForegroundColor Green