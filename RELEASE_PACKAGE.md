# VoiceStudio Quantum+ Release Package

Complete guide to creating and distributing the release package.

**Version:** 1.0.0  
**Release Date:** 2025-01-27

---

## Release Package Contents

### Required Files

1. **Installer**
   - `VoiceStudio-Setup-v1.0.0.exe` (Inno Setup installer)
   - `VoiceStudio-Setup-v1.0.0.msi` (WiX installer, optional)
   - Checksums (SHA256)

2. **Documentation**
   - `README.md` - Project overview
   - `RELEASE_NOTES.md` - Release notes
   - `CHANGELOG.md` - Complete changelog
   - `KNOWN_ISSUES.md` - Known issues
   - `LICENSE` - License file
   - `THIRD_PARTY_LICENSES.md` - Third-party licenses

3. **Checksums**
   - `SHA256SUMS.txt` - SHA256 checksums for all files

4. **Release Information**
   - Version number
   - Release date
   - System requirements
   - Installation instructions

---

## Creating the Release Package

### Step 1: Build Installer

**Using Build Script:**
```powershell
.\installer\build-installer.ps1 -InstallerType InnoSetup -Version 1.0.0
```

**Output:**
- `installer\Output\VoiceStudio-Setup-v1.0.0.exe`

### Step 2: Generate Checksums

**Create SHA256 Checksums:**
```powershell
Get-ChildItem installer\Output\*.exe | ForEach-Object {
    $hash = Get-FileHash $_.FullName -Algorithm SHA256
    "$($hash.Hash)  $($_.Name)" | Out-File -Append SHA256SUMS.txt
}
```

**Output:**
- `SHA256SUMS.txt`

### Step 3: Prepare Documentation

**Copy Documentation Files:**
- `README.md`
- `RELEASE_NOTES.md`
- `CHANGELOG.md`
- `KNOWN_ISSUES.md`
- `LICENSE`
- `THIRD_PARTY_LICENSES.md`

### Step 4: Create Release Archive

**Create ZIP Archive:**
```powershell
$releaseFiles = @(
    "installer\Output\VoiceStudio-Setup-v1.0.0.exe",
    "SHA256SUMS.txt",
    "README.md",
    "RELEASE_NOTES.md",
    "CHANGELOG.md",
    "KNOWN_ISSUES.md",
    "LICENSE",
    "THIRD_PARTY_LICENSES.md"
)

Compress-Archive -Path $releaseFiles -DestinationPath "VoiceStudio-v1.0.0-Release.zip"
```

**Output:**
- `VoiceStudio-v1.0.0-Release.zip`

---

## Release Package Structure

```
VoiceStudio-v1.0.0-Release/
├── VoiceStudio-Setup-v1.0.0.exe    # Main installer
├── SHA256SUMS.txt                   # Checksums
├── README.md                        # Project overview
├── RELEASE_NOTES.md                 # Release notes
├── CHANGELOG.md                     # Changelog
├── KNOWN_ISSUES.md                  # Known issues
├── LICENSE                          # License
└── THIRD_PARTY_LICENSES.md         # Third-party licenses
```

---

## Distribution

### GitHub Releases

**Create Release:**
1. Go to GitHub repository
2. Click "Releases" → "Draft a new release"
3. Tag: `v1.0.0`
4. Title: `VoiceStudio Quantum+ v1.0.0`
5. Description: Copy from `RELEASE_NOTES.md`
6. Upload files:
   - `VoiceStudio-Setup-v1.0.0.exe`
   - `SHA256SUMS.txt`
   - `VoiceStudio-v1.0.0-Release.zip` (optional)

### Website Distribution

**Upload Files:**
- Installer to downloads section
- Documentation to docs section
- Checksums for verification

### Direct Distribution

**Provide:**
- Download link to installer
- Checksums for verification
- Documentation links

---

## Verification

### Verify Checksums

**Windows PowerShell:**
```powershell
$expectedHash = (Get-Content SHA256SUMS.txt | Select-String "VoiceStudio-Setup-v1.0.0.exe").ToString().Split()[0]
$actualHash = (Get-FileHash VoiceStudio-Setup-v1.0.0.exe -Algorithm SHA256).Hash
if ($expectedHash -eq $actualHash) {
    Write-Host "Checksum verified!" -ForegroundColor Green
} else {
    Write-Host "Checksum mismatch!" -ForegroundColor Red
}
```

**Linux/Mac:**
```bash
sha256sum -c SHA256SUMS.txt
```

---

## Release Checklist

### Pre-Release

- [ ] All tests passing
- [ ] Documentation complete
- [ ] Known issues documented
- [ ] Release notes written
- [ ] Changelog updated
- [ ] Version numbers updated
- [ ] License files included
- [ ] Third-party licenses documented

### Build

- [ ] Frontend builds successfully
- [ ] Backend builds successfully
- [ ] Installer builds successfully
- [ ] Installer tested on clean system
- [ ] Uninstaller tested
- [ ] Upgrade path tested

### Package

- [ ] Installer file created
- [ ] Checksums generated
- [ ] Documentation included
- [ ] Release archive created
- [ ] Files verified

### Distribution

- [ ] GitHub release created
- [ ] Files uploaded
- [ ] Release notes published
- [ ] Website updated (if applicable)
- [ ] Announcement prepared

### Post-Release

- [ ] Monitor for issues
- [ ] Respond to user feedback
- [ ] Update documentation as needed
- [ ] Plan next release

---

## Release Notes Template

```markdown
# VoiceStudio Quantum+ v1.0.0

## What's New

- Feature 1
- Feature 2
- Feature 3

## Improvements

- Improvement 1
- Improvement 2

## Bug Fixes

- Fix 1
- Fix 2

## Known Issues

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md)

## System Requirements

- Windows 10 version 1903 or later
- .NET 8.0 Runtime
- Python 3.10+ (optional)

## Installation

1. Download `VoiceStudio-Setup-v1.0.0.exe`
2. Verify checksum (optional)
3. Run installer
4. Follow installation wizard

## Documentation

- [User Manual](docs/user/USER_MANUAL.md)
- [Getting Started](docs/user/GETTING_STARTED.md)
- [API Documentation](docs/api/API_REFERENCE.md)

## Support

- [Troubleshooting](docs/user/TROUBLESHOOTING.md)
- [Known Issues](KNOWN_ISSUES.md)
- Contact: (URL will be provided at release time)
```

---

## Version Numbering

**Format:** `MAJOR.MINOR.PATCH.BUILD`

**Examples:**
- `1.0.0.0` - Initial release
- `1.0.1.0` - Patch release
- `1.1.0.0` - Minor release
- `2.0.0.0` - Major release

---

## Code Signing

### Sign Installer

**Using SignTool:**
```powershell
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com VoiceStudio-Setup-v1.0.0.exe
```

### Sign Executables

**Sign Application:**
```powershell
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com VoiceStudioApp.exe
```

---

## Security

### Verify Signatures

**Check Signature:**
```powershell
Get-AuthenticodeSignature VoiceStudio-Setup-v1.0.0.exe
```

### Verify Checksums

Always verify checksums before installation to ensure file integrity.

---

## Support

For release-related questions:
- Check release notes
- Review known issues
- Contact support

---

**Last Updated:** 2025-01-27  
**Version:** 1.0.0

