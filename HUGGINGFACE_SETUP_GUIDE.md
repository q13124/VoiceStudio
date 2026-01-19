# HuggingFace API Token Setup Guide

## Problem

You're getting this error:
```
You are currently unauthenticated and will get rate limited. To reduce rate limiting, login with your API Token and consider subscribing to PRO: https://huggingface.co/pricing#pro
```

This happens because VoiceStudio downloads and uses AI models from HuggingFace, but without an API token, you're limited to anonymous requests which get rate limited.

## Solution

### Quick Setup (Recommended)

1. **Run the setup script:**
   ```powershell
   .\setup_huggingface_token.ps1
   ```
   Or use the batch version:
   ```cmd
   setup_huggingface_token.bat
   ```

2. **Get your token:**
   - Go to: https://huggingface.co/settings/tokens
   - Click "New token"
   - Name: "VoiceStudio" (or whatever you want)
   - Role: "Read" (free)
   - Click "Create token"
   - Copy the token (starts with `hf_`)

3. **Enter the token when prompted by the script**

4. **Restart VoiceStudio** (backend and frontend)

### Manual Setup

If you prefer to set it manually:

1. **Get your token** from https://huggingface.co/settings/tokens (see above)

2. **Set environment variables:**
   ```powershell
   # PowerShell (run as administrator)
   [Environment]::SetEnvironmentVariable("HF_TOKEN", "hf_your_token_here", "User")
   [Environment]::SetEnvironmentVariable("HUGGINGFACE_HUB_TOKEN", "hf_your_token_here", "User")
   ```

   Or via System Properties:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Add new user variables: `HF_TOKEN` and `HUGGINGFACE_HUB_TOKEN`

3. **Restart VoiceStudio**

### Verify Setup

After setup, check that the token is set:
```powershell
# PowerShell
[Environment]::GetEnvironmentVariable("HF_TOKEN", "User")
```

Or run the backend and check the logs - you should no longer see rate limiting messages.

## Why This Happens

- VoiceStudio uses AI models from HuggingFace for voice cloning, TTS, and other features
- Without authentication, HuggingFace limits anonymous requests to prevent abuse
- The free API token removes these limits and allows reliable model downloads

## Pro Subscription

If you plan to use VoiceStudio heavily, consider the HuggingFace Pro subscription ($9/month) which provides:
- Higher rate limits
- Priority access
- Commercial usage rights
- Support

But the free token should be sufficient for most personal use!