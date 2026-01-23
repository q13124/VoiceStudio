@echo off
echo Fixing Hugging Face API endpoint...
echo.

REM Set environment variables
set HF_INFERENCE_API_BASE=https://router.huggingface.co
set HF_ENDPOINT=https://router.huggingface.co

echo Environment variables set:
echo   HF_INFERENCE_API_BASE = %HF_INFERENCE_API_BASE%
echo   HF_ENDPOINT = %HF_ENDPOINT%
echo.

echo Testing Python environment...
python -c "
import os
print('Python environment variables:')
print('  HF_INFERENCE_API_BASE:', os.environ.get('HF_INFERENCE_API_BASE', 'NOT SET'))
print('  HF_ENDPOINT:', os.environ.get('HF_ENDPOINT', 'NOT SET'))

try:
    from huggingface_hub import InferenceClient
    client = InferenceClient()
    print('PASS: InferenceClient created successfully')
except Exception as e:
    print('WARN: InferenceClient test failed:', str(e))
"

echo.
echo Fix completed! You can now start VoiceStudio.
pause