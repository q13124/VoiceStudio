@echo off
REM VoiceStudio HuggingFace Token Setup Script
REM Run this script to set up your HuggingFace API token

echo VoiceStudio HuggingFace API Token Setup
echo ==========================================
echo.

REM Check if token is already set
for /f "tokens=*" %%i in ('powershell -command "[Environment]::GetEnvironmentVariable('HF_TOKEN', 'User')"') do set current_token=%%i

if defined current_token (
    echo Current HF_TOKEN is set to: %current_token%
    set /p reset="Do you want to update it? (y/n): "
    if /i not "!reset!"=="y" (
        echo Keeping existing token.
        goto :end
    )
)

echo.
echo To get your HuggingFace token:
echo 1. Go to: https://huggingface.co/settings/tokens
echo 2. Create a new token with 'Read' permissions
echo 3. Copy the token (starts with 'hf_')
echo.

set /p token="Enter your HuggingFace token: "

REM Basic validation - should start with hf_ and contain only alphanumeric chars
echo %token% | findstr /r "^hf_[a-zA-Z0-9]*$" >nul
if errorlevel 1 (
    echo.
    echo ERROR: Invalid token format. Token should start with 'hf_' followed by letters and numbers.
    goto :error
)

REM Set as user environment variable (persistent)
powershell -command "[Environment]::SetEnvironmentVariable('HF_TOKEN', '%token%', 'User')"
powershell -command "[Environment]::SetEnvironmentVariable('HUGGINGFACE_HUB_TOKEN', '%token%', 'User')"

echo.
echo SUCCESS: Token set successfully!
echo Environment variables:
echo   HF_TOKEN=%token%
echo   HUGGINGFACE_HUB_TOKEN=%token%
echo.
echo Note: Restart any running VoiceStudio processes for changes to take effect.
goto :end

:error
echo.
echo Setup failed.
exit /b 1

:end
echo.
pause