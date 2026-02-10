# VoiceStudio Update Mechanism

**Phase 9 Gap Resolution - COND-3**  
**Date**: 2026-02-10  
**Version**: 1.0.1

---

## Overview

VoiceStudio implements a secure, user-controlled update mechanism that respects offline-first principles. Updates are optional and never forced.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     VoiceStudio App                       │
│  ┌─────────────────┐    ┌──────────────────────────────┐ │
│  │  UpdateService  │───▶│  UpdateViewModel             │ │
│  └────────┬────────┘    └──────────────────────────────┘ │
│           │                                               │
│           ▼                                               │
│  ┌─────────────────┐                                      │
│  │  GitHub Releases│ (api.github.com)                     │
│  │  Check API      │                                      │
│  └────────┬────────┘                                      │
│           │                                               │
│           ▼                                               │
│  ┌─────────────────┐    ┌──────────────────────────────┐ │
│  │  Download       │───▶│  Installer Verification      │ │
│  │  Manager        │    │  (SHA256 + Code Signing)     │ │
│  └─────────────────┘    └──────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

## Update Flow

### 1. Check for Updates

```
User Action: Help > Check for Updates
    │
    ▼
┌─────────────────────────────────────────┐
│ GET github.com/api/repos/.../releases   │
│ Headers: User-Agent: VoiceStudio/1.0.1  │
│ No authentication required              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Parse latest release:                   │
│ - Version tag (semver)                  │
│ - Release notes (markdown)              │
│ - Asset URLs (installer, checksums)     │
│ - Minimum supported version             │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Compare versions:                       │
│ Current: 1.0.1                          │
│ Latest:  1.0.2                          │
│ Update available: YES                   │
└─────────────────────────────────────────┘
```

### 2. Download Update

```
User clicks "Download Update"
    │
    ▼
┌─────────────────────────────────────────┐
│ Download installer to temp directory:   │
│ %TEMP%\VoiceStudio\Updates\             │
│ File: VoiceStudio-1.0.2-Setup.exe       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Verify integrity:                       │
│ 1. Download SHA256 checksum file        │
│ 2. Compute hash of installer            │
│ 3. Compare hashes                       │
│ 4. Verify code signature (Authenticode) │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
 PASS                      FAIL
    │                         │
    ▼                         ▼
Show "Install"          Show error,
button                  delete file
```

### 3. Install Update

```
User clicks "Install Now"
    │
    ▼
┌─────────────────────────────────────────┐
│ Save current work:                      │
│ - Auto-save open projects               │
│ - Preserve window state                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Launch installer with args:             │
│ /SILENT /NORESTART                      │
│ /DIR="{current install path}"           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Close VoiceStudio                       │
│ Installer performs update               │
│ Restart VoiceStudio                     │
└─────────────────────────────────────────┘
```

---

## Configuration

### Settings Location

User preferences stored in:
```
%APPDATA%\VoiceStudio\settings.json
```

### Update Settings

```json
{
  "updates": {
    "checkOnStartup": true,
    "autoDownload": false,
    "channel": "stable",
    "lastCheckTime": "2026-02-10T15:30:00Z",
    "skipVersion": null,
    "proxy": null
  }
}
```

### Update Channels

| Channel | Description | Check Frequency |
|---------|-------------|-----------------|
| `stable` | Production releases | Daily |
| `beta` | Pre-release testing | Daily |
| `canary` | Bleeding edge | Hourly |

---

## Security

### Verification Steps

1. **TLS 1.3**: All connections use TLS 1.3
2. **Certificate Pinning**: GitHub API certificates validated
3. **Checksum Verification**: SHA256 hash comparison
4. **Code Signing**: Authenticode signature verification

### Code Signing Certificate

```
Subject: CN=VoiceStudio, O=VoiceStudio Project
Issuer: DigiCert Trusted G4 Code Signing RSA4096 SHA384
Thumbprint: [certificate thumbprint]
Valid: 2025-01-01 to 2028-01-01
```

### Checksum File Format

```
# SHA256 checksums for VoiceStudio 1.0.2
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  VoiceStudio-1.0.2-Setup.exe
a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a  VoiceStudio-1.0.2-portable.zip
```

---

## Offline Operation

VoiceStudio is designed for offline-first operation:

### When Offline

- Update check silently fails (no error shown)
- All features continue to work
- Last known version info displayed

### Offline Update Process

1. Download installer on another machine
2. Verify checksum manually
3. Run installer: `VoiceStudio-X.X.X-Setup.exe /SILENT`

---

## Rollback

### Automatic Backup

Before update, a backup is created:
```
%APPDATA%\VoiceStudio\Backup\pre-update-{version}\
```

Contains:
- Settings
- Profiles
- Custom presets
- Project cache

### Manual Rollback

1. Uninstall current version
2. Download previous version from GitHub Releases
3. Install previous version
4. Restore backup if needed

### Rollback via Installer

```powershell
# Rollback to previous version
VoiceStudio-1.0.1-Setup.exe /SILENT /ROLLBACK
```

---

## API Reference

### Check for Updates (C#)

```csharp
// IUpdateService interface
public interface IUpdateService
{
    Task<UpdateInfo?> CheckForUpdatesAsync();
    Task<string> DownloadUpdateAsync(UpdateInfo update, IProgress<double> progress);
    Task<bool> VerifyInstallerAsync(string path);
    Task InstallUpdateAsync(string installerPath);
}

// UpdateInfo model
public record UpdateInfo(
    string Version,
    string ReleaseNotes,
    string DownloadUrl,
    string Checksum,
    DateTime ReleaseDate,
    bool IsMandatory
);
```

### Usage Example

```csharp
var updateService = App.GetService<IUpdateService>();

// Check for updates
var update = await updateService.CheckForUpdatesAsync();
if (update != null)
{
    // Download with progress
    var progress = new Progress<double>(p => DownloadProgress = p);
    var installerPath = await updateService.DownloadUpdateAsync(update, progress);
    
    // Verify and install
    if (await updateService.VerifyInstallerAsync(installerPath))
    {
        await updateService.InstallUpdateAsync(installerPath);
    }
}
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Network error" | Firewall blocking | Allow github.com access |
| "Verification failed" | Corrupted download | Re-download installer |
| "Installation failed" | Permissions | Run as Administrator |
| "Update loop" | Version mismatch | Clear %TEMP%\VoiceStudio |

### Log Files

Update logs are stored at:
```
%APPDATA%\VoiceStudio\Logs\update-{date}.log
```

### Debug Mode

Enable verbose logging:
```powershell
VoiceStudio.exe --update-debug
```

---

## Related Documentation

- [UPDATES.md](UPDATES.md) - User guide for updates
- [INSTALLATION.md](INSTALLATION.md) - Installation guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - General troubleshooting

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-30 | Initial update mechanism |
| 1.0.1 | 2026-02-09 | Added rollback support, offline mode |
