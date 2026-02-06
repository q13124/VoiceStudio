# Secrets Rotation Guide

> Version: 1.0.0 | Last Updated: 2026-02-05 | Owner: Core Platform Team

This guide documents procedures for rotating API keys, tokens, and other secrets used by VoiceStudio.

---

## Table of Contents

1. [Overview](#overview)
2. [Secret Types and Storage](#secret-types-and-storage)
3. [Windows Credential Manager Rotation](#windows-credential-manager-rotation)
4. [Environment Variable Rotation](#environment-variable-rotation)
5. [API Key Rotation by Service](#api-key-rotation-by-service)
6. [Emergency Rotation Procedure](#emergency-rotation-procedure)
7. [Rotation Schedule](#rotation-schedule)
8. [Verification After Rotation](#verification-after-rotation)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### Why Rotate Secrets?

Secret rotation is a critical security practice that:

- **Limits exposure window**: Compromised secrets become useless after rotation
- **Ensures compliance**: Many security standards require periodic rotation
- **Detects unauthorized access**: Rotation can reveal if secrets were being used maliciously
- **Maintains security hygiene**: Regular rotation prevents credential stagnation

### When to Rotate

| Trigger | Action | Timeline |
|---------|--------|----------|
| Scheduled rotation | Planned rotation | Per schedule |
| Team member departure | Rotate shared secrets | Immediately |
| Suspected compromise | Emergency rotation | Immediately |
| Third-party breach notification | Rotate affected service | Within 24 hours |
| Security audit finding | Address per finding | Per SLA |

---

## Secret Types and Storage

### VoiceStudio Secret Inventory

| Secret Type | Storage Location | Rotation Frequency |
|-------------|------------------|-------------------|
| API keys (third-party) | Windows Credential Manager | 90 days |
| IPC signing key | Environment variable | 180 days |
| CI/CD tokens | GitHub Secrets | 90 days |
| Database credentials | Environment variable | 90 days |
| Encryption keys | Windows Credential Manager | 365 days |

### Storage Hierarchy

```
Priority 1: Windows Credential Manager (production secrets)
Priority 2: Environment Variables (runtime configuration)
Priority 3: config/api-keys.json (development reference only)
```

> **Important**: `config/api-keys.json` is for development reference only. Production secrets should NEVER be stored in files. See `.cursor/rules/security/api-key-management.mdc`.

---

## Windows Credential Manager Rotation

### Prerequisites

- Administrator access on the Windows machine
- New secret value from the service provider

### Rotation Steps

#### Using PowerShell (Recommended)

```powershell
# 1. View existing credential
cmdkey /list:VoiceStudio_ServiceName

# 2. Delete old credential
cmdkey /delete:VoiceStudio_ServiceName

# 3. Add new credential
cmdkey /add:VoiceStudio_ServiceName /user:api_key /pass:"NEW_SECRET_VALUE"

# 4. Verify
cmdkey /list:VoiceStudio_ServiceName
```

#### Using Credential Manager GUI

1. Open **Control Panel** → **Credential Manager**
2. Select **Windows Credentials**
3. Find the credential (e.g., `VoiceStudio_ElevenLabs`)
4. Click **Edit**
5. Update the password field with the new secret
6. Click **Save**

### Credentials Used by VoiceStudio

| Credential Name | Purpose | Service |
|-----------------|---------|---------|
| `VoiceStudio_ElevenLabs` | Voice synthesis | ElevenLabs API |
| `VoiceStudio_HuggingFace` | Model downloads | Hugging Face |
| `VoiceStudio_OpenAI` | AI features | OpenAI API |
| `VoiceStudio_IPCKey` | UI-Backend signing | Internal |

---

## Environment Variable Rotation

### System Environment Variables

Used for secrets that need to be available system-wide.

```powershell
# 1. Set new environment variable (requires restart)
[System.Environment]::SetEnvironmentVariable(
    "VOICESTUDIO_IPC_SECRET",
    "NEW_BASE64_ENCODED_SECRET",
    [System.EnvironmentVariableTarget]::Machine
)

# 2. Verify (in new PowerShell session)
[System.Environment]::GetEnvironmentVariable(
    "VOICESTUDIO_IPC_SECRET",
    [System.EnvironmentVariableTarget]::Machine
)

# 3. Restart VoiceStudio services to pick up new value
```

### User Environment Variables

For development or user-specific secrets:

```powershell
# Set for current user
[System.Environment]::SetEnvironmentVariable(
    "HUGGINGFACE_TOKEN",
    "hf_xxxxxxxxxxxxx",
    [System.EnvironmentVariableTarget]::User
)
```

### Session Environment Variables

For temporary rotation during testing:

```powershell
# Set for current session only (does not persist)
$env:VOICESTUDIO_IPC_SECRET = "NEW_TEST_SECRET"

# Run application
.\VoiceStudio.exe

# Secret is cleared when session ends
```

### Environment Variables Used by VoiceStudio

| Variable | Purpose | Scope |
|----------|---------|-------|
| `VOICESTUDIO_IPC_SECRET` | HMAC request signing | Machine |
| `VOICESTUDIO_IPC_SIGNING_ENABLED` | Enable/disable signing | Machine |
| `HUGGINGFACE_TOKEN` | HuggingFace authentication | User |
| `ELEVENLABS_API_KEY` | ElevenLabs API | User |
| `OPENAI_API_KEY` | OpenAI API (optional) | User |

---

## API Key Rotation by Service

### ElevenLabs

1. **Generate new key**:
   - Log in to [ElevenLabs Dashboard](https://elevenlabs.io/app)
   - Navigate to **Profile** → **API Keys**
   - Click **Create new API key**
   - Copy the new key

2. **Update VoiceStudio**:
   ```powershell
   cmdkey /delete:VoiceStudio_ElevenLabs
   cmdkey /add:VoiceStudio_ElevenLabs /user:api_key /pass:"xi_xxxxxxx"
   ```

3. **Revoke old key**:
   - In ElevenLabs Dashboard, delete the old API key

4. **Verify**:
   - Test voice synthesis in VoiceStudio

### Hugging Face

1. **Generate new token**:
   - Log in to [Hugging Face Settings](https://huggingface.co/settings/tokens)
   - Click **New token**
   - Set permissions (read is usually sufficient)
   - Copy the token

2. **Update VoiceStudio**:
   ```powershell
   [System.Environment]::SetEnvironmentVariable(
       "HUGGINGFACE_TOKEN",
       "hf_xxxxxxx",
       [System.EnvironmentVariableTarget]::User
   )
   ```

3. **Revoke old token**:
   - Delete the old token in Hugging Face settings

4. **Verify**:
   - Test model download in VoiceStudio

### IPC Signing Key (Internal)

1. **Generate new key**:
   ```powershell
   # Generate a new 256-bit key
   $bytes = New-Object byte[] 32
   [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
   $newKey = [Convert]::ToBase64String($bytes)
   Write-Host "New IPC Key: $newKey"
   ```

2. **Update both sides**:
   - Backend (Python) and Frontend (C#) must use the same key
   ```powershell
   [System.Environment]::SetEnvironmentVariable(
       "VOICESTUDIO_IPC_SECRET",
       $newKey,
       [System.EnvironmentVariableTarget]::Machine
   )
   ```

3. **Restart services**:
   - Restart VoiceStudio backend
   - Restart VoiceStudio UI

4. **Verify**:
   - Test API calls from UI to backend

---

## Emergency Rotation Procedure

Use this procedure when a secret is suspected or confirmed compromised.

### Immediate Actions (Within 1 Hour)

1. **Assess scope**:
   - Which secrets are affected?
   - What data/systems are at risk?
   - When did the compromise occur?

2. **Revoke immediately**:
   - Log into the affected service
   - Revoke/delete the compromised credential
   - Do NOT wait to generate a new one first

3. **Generate replacement**:
   - Create new credentials
   - Update VoiceStudio configuration

4. **Restart services**:
   - Restart all services using the rotated secret

### Documentation (Within 24 Hours)

5. **Document the incident**:
   - What was compromised
   - When it was discovered
   - Actions taken
   - Timeline of events

6. **Review logs**:
   - Check for unauthorized usage
   - Identify potential data access

7. **Notify stakeholders**:
   - Team members
   - Security team (if applicable)
   - Affected third parties (if required)

### Follow-Up (Within 1 Week)

8. **Root cause analysis**:
   - How was the secret exposed?
   - What controls failed?

9. **Preventive measures**:
   - Update procedures to prevent recurrence
   - Enhance monitoring if needed

### Emergency Rotation Script

```powershell
# emergency-rotate.ps1
# Run with Administrator privileges

param(
    [Parameter(Mandatory=$true)]
    [string]$SecretName
)

Write-Host "EMERGENCY ROTATION: $SecretName" -ForegroundColor Red
Write-Host "================================" -ForegroundColor Red

# Step 1: Revoke old credential
Write-Host "Step 1: Revoking old credential..."
cmdkey /delete:VoiceStudio_$SecretName

# Step 2: Generate new secret
Write-Host "Step 2: Generating new secret..."
$bytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$newSecret = [Convert]::ToBase64String($bytes)

# Step 3: Store new credential
Write-Host "Step 3: Storing new credential..."
cmdkey /add:VoiceStudio_$SecretName /user:api_key /pass:$newSecret

# Step 4: Log rotation
$logEntry = @{
    timestamp = Get-Date -Format "o"
    secret = $SecretName
    action = "emergency_rotation"
    user = $env:USERNAME
}
$logEntry | ConvertTo-Json | Out-File -Append ".buildlogs/security/rotation-log.json"

Write-Host "Step 4: Logged rotation event"
Write-Host ""
Write-Host "NEW SECRET VALUE:" -ForegroundColor Yellow
Write-Host $newSecret
Write-Host ""
Write-Host "IMPORTANT: Update the third-party service with this new value!" -ForegroundColor Red
Write-Host "IMPORTANT: Restart VoiceStudio services!" -ForegroundColor Red
```

---

## Rotation Schedule

### Recommended Schedule

| Secret Category | Rotation Frequency | Next Rotation |
|-----------------|-------------------|---------------|
| Third-party API keys | Every 90 days | Track in calendar |
| IPC signing key | Every 180 days | Track in calendar |
| CI/CD tokens | Every 90 days | Track in calendar |
| Encryption keys | Every 365 days | Track in calendar |

### Setting Up Reminders

Create calendar reminders for secret rotation:

```powershell
# Calculate next rotation dates
$now = Get-Date
$rotations = @{
    "API Keys (90 days)" = $now.AddDays(90)
    "IPC Key (180 days)" = $now.AddDays(180)
    "Encryption Keys (365 days)" = $now.AddDays(365)
}

$rotations | Format-Table -AutoSize
```

### Rotation Tracking File

Maintain a rotation log at `.buildlogs/security/rotation-schedule.json`:

```json
{
  "rotations": [
    {
      "secret": "ELEVENLABS_API_KEY",
      "last_rotated": "2026-02-05T10:00:00Z",
      "next_rotation": "2026-05-06T10:00:00Z",
      "rotated_by": "admin"
    }
  ]
}
```

---

## Verification After Rotation

### Immediate Verification

After rotating any secret, verify the application still functions:

1. **Backend health check**:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **UI-to-backend communication**:
   - Open VoiceStudio
   - Navigate to any panel that calls the backend
   - Verify no authentication errors

3. **Third-party service calls**:
   - Test the specific service whose key was rotated
   - E.g., for ElevenLabs: test voice synthesis

### Automated Verification Script

```python
# scripts/verify_secrets.py
"""Verify all secrets are properly configured after rotation."""

import os
import subprocess
import sys

def check_env_var(name: str) -> bool:
    """Check if environment variable is set."""
    value = os.environ.get(name)
    if value:
        print(f"  [OK] {name} is set ({len(value)} chars)")
        return True
    else:
        print(f"  [FAIL] {name} is not set")
        return False

def check_credential(name: str) -> bool:
    """Check if Windows credential exists."""
    result = subprocess.run(
        ["cmdkey", f"/list:VoiceStudio_{name}"],
        capture_output=True,
        text=True
    )
    if "VoiceStudio_" in result.stdout:
        print(f"  [OK] VoiceStudio_{name} credential exists")
        return True
    else:
        print(f"  [FAIL] VoiceStudio_{name} credential not found")
        return False

def main():
    print("VoiceStudio Secrets Verification")
    print("=" * 40)
    
    all_ok = True
    
    print("\nEnvironment Variables:")
    all_ok &= check_env_var("VOICESTUDIO_IPC_SECRET")
    all_ok &= check_env_var("HUGGINGFACE_TOKEN")
    
    print("\nWindows Credentials:")
    all_ok &= check_credential("ElevenLabs")
    
    print("\n" + "=" * 40)
    if all_ok:
        print("All secrets verified successfully!")
        return 0
    else:
        print("Some secrets are missing or misconfigured!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## Troubleshooting

### Common Issues

#### "Invalid API key" after rotation

**Cause**: Application is using cached old key.

**Solution**:
1. Restart VoiceStudio application completely
2. If using backend service, restart the backend process
3. Verify the new key is correctly stored

#### "Signature verification failed" after IPC key rotation

**Cause**: Frontend and backend are using different keys.

**Solution**:
1. Ensure both use the same `VOICESTUDIO_IPC_SECRET`
2. Restart both frontend and backend
3. Check for typos in the key value

#### Credential Manager not updating

**Cause**: Credential Manager GUI caches credentials.

**Solution**:
1. Use PowerShell commands instead of GUI
2. Or close and reopen Credential Manager
3. Log out and log back in to Windows

#### Environment variable not picked up

**Cause**: Process started before variable was set.

**Solution**:
1. Set variable at Machine or User level (not session)
2. Start a new terminal/PowerShell session
3. Restart the application

---

## References

- [Dependency Policy](../governance/DEPENDENCY_POLICY.md)
- [API Key Management Rule](../../.cursor/rules/security/api-key-management.mdc)
- [Security Best Practices](./SECURITY_BEST_PRACTICES.md)
- [Secrets Baseline](.secrets.baseline)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-05 | 1.0.0 | Initial guide creation |
