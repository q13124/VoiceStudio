# VoiceStudio Quantum+ Update Guide

Complete guide to updating VoiceStudio Quantum+.

## Table of Contents

1. [Automatic Updates](#automatic-updates)
2. [Manual Update Check](#manual-update-check)
3. [Installing Updates](#installing-updates)
4. [Update Preferences](#update-preferences)
5. [Troubleshooting Updates](#troubleshooting-updates)
6. [Update Information](#update-information)
7. [Manual Update Installation](#manual-update-installation)
8. [Update Best Practices](#update-best-practices)
9. [Rollback Procedures](#rollback-procedures)
10. [Support](#support)

---

## Automatic Updates

### Update Check on Startup

VoiceStudio Quantum+ can automatically check for updates when the application starts.

**Enable Automatic Update Check:**
1. Open Settings
2. Navigate to "Updates" section
3. Enable "Check for updates on startup"
4. Optionally enable "Automatically download updates"

**Update Check Frequency:**
- Checks occur at most once per hour
- Manual checks are always available

### Update Notifications

When an update is available, you'll see:
- **Notification:** Update available notification in the status bar
- **Dialog:** Update dialog with release notes and download options

---

## Manual Update Check

### Check for Updates

**Method 1: Menu**
1. Click "Help" in the menu bar
2. Select "Check for Updates"

**Method 2: Settings**
1. Open Settings
2. Navigate to "Updates" section
3. Click "Check for Updates Now"

**Method 3: Command Palette**
1. Press `Ctrl+Shift+P` (or `F1`)
2. Type "Check for Updates"
3. Press Enter

### Update Check Process

1. **Connecting:** Connects to update server
2. **Checking:** Compares current version with latest
3. **Result:** Shows update available or "You're up to date"

---

## Installing Updates

### Download Update

**When Update Available:**
1. Update dialog appears automatically
2. Review release notes
3. Click "Download Update"
4. Wait for download to complete

**Download Progress:**
- Progress bar shows download percentage
- Download speed displayed
- Can continue using application during download

### Install Update

**After Download:**
1. Click "Install Update" button
2. Confirm installation (UAC prompt may appear)
3. Installer launches
4. Application closes automatically
5. Installer completes installation
6. Restart application

**Installation Process:**
- Installer runs with administrator privileges
- Updates application files
- Preserves user data and settings
- Application restarts automatically

---

## Update Preferences

### Settings

**Update Settings Location:**
- Settings → Updates

**Available Options:**

1. **Check for updates on startup**
   - Automatically check when application starts
   - Default: Enabled

2. **Automatically download updates**
   - Download updates automatically when available
   - Default: Disabled (manual download)

3. **Update check frequency**
   - How often to check for updates
   - Options: Hourly, Daily, Weekly
   - Default: Daily

4. **Include pre-release versions**
   - Check for beta/pre-release updates
   - Default: Disabled

### Update Channel

**Stable Channel (Default):**
- Only stable releases
- Recommended for production use

**Beta Channel:**
- Beta and pre-release versions
- For testing new features
- May be less stable

---

## Troubleshooting Updates

### Update Check Fails

**Symptoms:**
- "Failed to check for updates" error
- Network error messages

**Solutions:**

1. **Check Internet Connection**
   - Verify internet connectivity
   - Check firewall settings
   - Verify proxy settings (if applicable)

2. **Check Update Server**
   - Update server may be temporarily unavailable
   - Try again later

3. **Manual Update**
   - Download installer from website
   - Install manually

### Download Fails

**Symptoms:**
- Download stops or fails
- "Download failed" error

**Solutions:**

1. **Check Disk Space**
   - Ensure sufficient disk space
   - Free up space if needed

2. **Check Network Connection**
   - Verify stable internet connection
   - Check for network interruptions

3. **Retry Download**
   - Click "Download Update" again
   - Download will resume or restart

4. **Manual Download**
   - Download installer from website
   - Install manually

### Installation Fails

**Symptoms:**
- Installer fails to start
- Installation errors

**Solutions:**

1. **Run as Administrator**
   - Right-click installer
   - Select "Run as administrator"

2. **Close Application**
   - Ensure VoiceStudio is closed
   - Close all instances

3. **Check Antivirus**
   - Temporarily disable antivirus
   - Add exception for VoiceStudio

4. **Manual Installation**
   - Download installer from website
   - Run installer manually

### Update Verification Fails

**Symptoms:**
- "Update verification failed" error
- Checksum mismatch

**Solutions:**

1. **Re-download Update**
   - Delete partial download
   - Download again

2. **Check File Integrity**
   - Verify download completed
   - Check file size matches

3. **Contact Support**
   - Report issue
   - Provide error details

---

## Update Information

### Version Numbering

**Format:** `MAJOR.MINOR.PATCH.BUILD`

**Examples:**
- `1.0.0.0` - Initial release
- `1.0.1.0` - Patch release (bug fixes)
- `1.1.0.0` - Minor release (new features)
- `2.0.0.0` - Major release (breaking changes)

### Release Notes

**Viewing Release Notes:**
- Shown in update dialog
- Available on website
- Included in release package

**Release Notes Include:**
- New features
- Improvements
- Bug fixes
- Known issues
- Migration notes (if applicable)

### Update Types

**Patch Updates:**
- Bug fixes only
- No new features
- Safe to install immediately

**Minor Updates:**
- New features
- Improvements
- Backward compatible
- Recommended to install

**Major Updates:**
- Breaking changes possible
- New features
- Review migration notes
- Backup before installing

---

## Manual Update Installation

### Download Installer

1. Visit VoiceStudio website
2. Navigate to Downloads
3. Download latest installer
4. Verify checksum (optional)

### Install Update

1. Close VoiceStudio application
2. Run installer
3. Follow installation wizard
4. Restart application

### Verify Installation

1. Launch VoiceStudio
2. Check version in About dialog
3. Verify features work correctly

---

## Update Best Practices

### Before Updating

1. **Backup Data**
   - Backup projects
   - Backup profiles
   - Backup settings

2. **Close Application**
   - Save all work
   - Close application
   - Ensure no running instances

3. **Review Release Notes**
   - Read release notes
   - Check for breaking changes
   - Review migration notes

### During Update

1. **Don't Interrupt**
   - Let update complete
   - Don't close installer
   - Don't restart computer

2. **Monitor Progress**
   - Watch installation progress
   - Note any errors
   - Take screenshots if issues

### After Updating

1. **Verify Installation**
   - Check version number
   - Test key features
   - Verify data integrity

2. **Report Issues**
   - Report bugs if found
   - Provide version information
   - Include error details

---

## Update Server

### GitHub Releases

VoiceStudio Quantum+ uses GitHub Releases for updates:
- **Repository:** (URL will be provided at release time)
- **API:** GitHub Releases API
- **Format:** Standard GitHub release format

### Custom Update Server

For enterprise deployments, custom update servers can be configured:
- Contact support for configuration
- Requires custom update service implementation

---

## Frequently Asked Questions

### How often should I update?

**Answer:** Update when new versions are available. Patch updates should be installed promptly for security fixes.

### Will updates preserve my data?

**Answer:** Yes, updates preserve all user data including projects, profiles, and settings.

### Can I skip updates?

**Answer:** Yes, but it's recommended to stay updated for bug fixes and security patches.

### What if an update breaks something?

**Answer:** Report the issue immediately. See the [Rollback Procedures](#rollback-procedures) section for reverting to a previous version.

### Do I need to uninstall before updating?

**Answer:** No, the installer handles upgrades automatically. No uninstallation needed.

---

## Rollback Procedures

### When to Rollback

Consider rolling back if:
- Application crashes after update
- Critical features stop working
- Data corruption detected
- Performance severely degraded

### Pre-Rollback Checklist

1. **Backup current state**
   - Export projects: File → Export → Export All Projects
   - Backup settings: Copy `%APPDATA%\VoiceStudio\settings.json`
   - Note current version: Help → About

2. **Document the issue**
   - Screenshot error messages
   - Note steps to reproduce
   - Save relevant log files from `%APPDATA%\VoiceStudio\logs\`

### Rollback Methods

#### Method 1: Windows System Restore (Recommended)

If you have a system restore point from before the update:

1. Open Control Panel → Recovery
2. Click "Open System Restore"
3. Select restore point dated before the update
4. Follow wizard to complete restore

#### Method 2: Previous Installer

1. **Uninstall current version:**
   - Open Settings → Apps → Installed Apps
   - Find "VoiceStudio Quantum+"
   - Click "Uninstall"

2. **Download previous version:**
   - Visit GitHub Releases page
   - Find the previous stable version
   - Download the installer (.exe)

3. **Install previous version:**
   - Run the downloaded installer
   - Follow installation wizard
   - Select same installation directory

4. **Restore data (if needed):**
   - Copy backed-up settings.json to `%APPDATA%\VoiceStudio\`
   - Import projects: File → Import → Import Project

#### Method 3: Side-by-Side Installation (Advanced)

For testing before committing to rollback:

1. Install previous version to a different directory
2. Test functionality
3. If successful, uninstall newer version
4. Optionally move installation

### Post-Rollback Steps

1. **Verify installation:**
   - Launch VoiceStudio
   - Check version: Help → About
   - Test critical features

2. **Restore data:**
   - Verify projects load correctly
   - Check voice profiles are accessible
   - Confirm settings are preserved

3. **Disable auto-update temporarily:**
   - Settings → Updates
   - Disable "Check for updates on startup"
   - Wait for patch release

4. **Report the issue:**
   - File bug report on GitHub Issues
   - Include version you rolled back from
   - Describe the problem and steps to reproduce

### Data Locations Reference

| Data Type | Location |
|-----------|----------|
| Settings | `%APPDATA%\VoiceStudio\settings.json` |
| Projects | `%USERPROFILE%\Documents\VoiceStudio\Projects\` |
| Profiles | `%APPDATA%\VoiceStudio\profiles\` |
| Logs | `%APPDATA%\VoiceStudio\logs\` |
| Models | `%APPDATA%\VoiceStudio\models\` |
| Cache | `%LOCALAPPDATA%\VoiceStudio\cache\` |

### Version History

Previous versions are available on the GitHub Releases page:
- Each release includes installer and release notes
- Checksums provided for verification
- Minimum 3 previous stable versions maintained

---

## Support

**Update Issues:**
- Check troubleshooting section above
- Contact support with error details
- Include version information

**Update Requests:**
- Feature requests: GitHub Issues
- Bug reports: GitHub Issues
- General questions: Support email

---

**Last Updated:** 2026-02-04  
**Version:** 1.1

