# VoiceStudio Quantum+ Upgrade, Rollback, and Migration Notes

**Version:** 1.0.0  
**Date:** 2025-01-28  
**Gate:** H (Packaging and upgrades)

---

## Upgrade Procedure

### Supported Upgrade Paths

- **From:** Any previous version of VoiceStudio Quantum+
- **To:** Version 1.0.0 or later

### Upgrade Steps

1. **Backup User Data (Recommended)**

   - Location: `%APPDATA%\VoiceStudio\`
   - Backup: Copy entire `VoiceStudio` folder to safe location
   - Includes: Settings, projects, profiles, layouts, logs

2. **Run Installer**

   - Execute: `VoiceStudio-Setup-v1.0.0.exe`
   - Installer detects existing installation
   - Choose "Upgrade" option when prompted

3. **Data Preservation**

   - User data preserved automatically:
     - `%APPDATA%\VoiceStudio\settings.json`
     - `%APPDATA%\VoiceStudio\projects\` (all project files)
     - `%APPDATA%\VoiceStudio\profiles\` (all voice profiles)
     - `%APPDATA%\VoiceStudio\layouts\` (UI layouts)
     - `%PROGRAMDATA%\VoiceStudio\models\` (engine models)
     - `%PROGRAMDATA%\VoiceStudio\cache\` (cache files)

4. **Post-Upgrade Verification**
   - Launch application
   - Verify projects load correctly
   - Verify profiles are accessible
   - Verify settings are preserved
   - Test basic engine operation

### Version Compatibility Matrix

| From Version | To Version | Upgrade Supported | Data Migration Required                        |
| ------------ | ---------- | ----------------- | ---------------------------------------------- |
| 0.x.x        | 1.0.0      | Yes               | Automatic                                      |
| 1.0.0        | 1.0.1+     | Yes               | Automatic                                      |
| 1.x.x        | 2.0.0+     | Yes               | May require manual steps (see Migration Notes) |

---

## Rollback Procedure

### When to Rollback

- Application fails to launch after upgrade
- Critical functionality broken after upgrade
- Data corruption detected
- Performance degradation

### Rollback Steps

1. **Uninstall Current Version**

   - Control Panel → Programs → VoiceStudio Quantum+
   - Click "Uninstall"
   - **Important:** User data is preserved by default (installer/uninstaller does not prompt during uninstall)
   - User data in `%APPDATA%\VoiceStudio\` and `%PROGRAMDATA%\VoiceStudio\` is preserved

2. **Install Previous Version**

   - Locate previous version installer
   - Run installer: `VoiceStudio-Setup-v<previous-version>.exe`
   - Install to same location (default: `C:\Program Files\VoiceStudio`)

3. **Verify Data Recovery**
   - Launch application
   - Verify projects load
   - Verify profiles accessible
   - Verify settings restored

### Rollback Limitations

- **Engine Models:** If engine model format changed between versions, models may need to be regenerated
- **Project Format:** If project schema changed, older projects may require migration (see Migration Notes)
- **Settings:** Settings format changes may require manual reconfiguration

### Supported Rollback Versions

- Rollback to any previous version is supported
- User data is preserved across rollbacks
- Application files are replaced, user data remains intact

---

## Migration Notes

### Settings Migration

**Location:** `%APPDATA%\VoiceStudio\settings.json`

**Automatic Migration:**

- Settings format is versioned
- Installer automatically migrates settings to new format
- Backward compatibility maintained for 2 major versions

**Manual Migration (if needed):**

1. Backup `settings.json`
2. Review new settings format in documentation
3. Manually update settings if automatic migration fails
4. Restore from backup if issues occur

### Project Format Migration

**Location:** `%APPDATA%\VoiceStudio\projects\`

**Automatic Migration:**

- Projects are versioned
- Application automatically migrates projects on first open
- Original project files backed up with `.backup` extension

**Manual Migration (if needed):**

1. Projects are stored as `.voiceproj` files
2. If automatic migration fails:
   - Backup project files
   - Open project in new version
   - Application will prompt for migration
   - Follow on-screen instructions

### Profile Format Migration

**Location:** `%APPDATA%\VoiceStudio\profiles\`

**Automatic Migration:**

- Voice profiles are versioned
- Application automatically migrates profiles on first access
- Original profiles backed up

**Manual Migration (if needed):**

1. Profiles stored as `.vprofile` files
2. If automatic migration fails:
   - Backup profile files
   - Import profiles in new version
   - Application will migrate automatically

### Engine Model Migration

**Location:** `%PROGRAMDATA%\VoiceStudio\models\`

**Automatic Migration:**

- Engine models are cached by content hash
- Models are automatically revalidated after upgrade
- Invalid models are automatically regenerated

**Manual Migration (if needed):**

1. If models fail validation:
   - Delete `%PROGRAMDATA%\VoiceStudio\models\` folder
   - Application will regenerate models on first use
   - Models will be re-downloaded if needed (if network enabled)

### Cache Migration

**Location:** `%PROGRAMDATA%\VoiceStudio\cache\`

**Automatic Migration:**

- Cache is content-addressed
- Cache entries are automatically revalidated
- Invalid cache entries are automatically cleared

**Manual Migration (if needed):**

1. If cache issues occur:
   - Delete `%PROGRAMDATA%\VoiceStudio\cache\` folder
   - Application will rebuild cache on first use
   - No data loss (cache is performance optimization only)

---

## Data Locations

### Application Installation

- **Default:** `C:\Program Files\VoiceStudio\`
- **Components:**
  - `App\` - Frontend application
  - `Backend\` - Python backend
  - `Core\` - Engine core files
  - `Engines\` - Engine manifests
  - `Docs\` - Documentation

### User Data (Preserved on Upgrade/Rollback)

- **Settings:** `%APPDATA%\VoiceStudio\settings.json`
- **Projects:** `%APPDATA%\VoiceStudio\projects\`
- **Profiles:** `%APPDATA%\VoiceStudio\profiles\`
- **Layouts:** `%APPDATA%\VoiceStudio\layouts\`
- **Logs:** `%APPDATA%\VoiceStudio\logs\`

### Program Data (Preserved on Upgrade/Rollback)

- **Models:** `%PROGRAMDATA%\VoiceStudio\models\`
- **Cache:** `%PROGRAMDATA%\VoiceStudio\cache\`

---

## Troubleshooting

### Upgrade Fails

1. **Check Disk Space**

   - Ensure at least 2GB free space
   - Clear temporary files if needed

2. **Check Permissions**

   - Run installer as Administrator
   - Ensure write access to installation directory

3. **Check Antivirus**

   - Temporarily disable antivirus
   - Add installer to exclusions if needed

4. **Manual Upgrade**
   - Uninstall previous version
   - Install new version
   - User data is preserved

### Rollback Fails

1. **Data Backup**

   - Manually backup `%APPDATA%\VoiceStudio\` before rollback
   - Manually backup `%PROGRAMDATA%\VoiceStudio\` before rollback

2. **Clean Uninstall**

   - Use Control Panel to uninstall
   - Choose "Remove user data" only if you have backup
   - Reinstall previous version

3. **Data Restoration**
   - Restore from backup if needed
   - Verify data integrity

### Migration Issues

1. **Settings Migration Fails**

   - Backup `settings.json`
   - Delete `settings.json`
   - Application will create default settings
   - Manually reconfigure if needed

2. **Project Migration Fails**

   - Backup project files
   - Open project in new version
   - Application will attempt migration
   - Restore from backup if migration fails

3. **Profile Migration Fails**
   - Backup profile files
   - Import profiles in new version
   - Application will attempt migration
   - Restore from backup if migration fails

---

## Best Practices

### Before Upgrade

1. **Backup User Data**

   - Copy `%APPDATA%\VoiceStudio\` to safe location
   - Copy `%PROGRAMDATA%\VoiceStudio\` to safe location (optional, can regenerate)

2. **Close Application**

   - Ensure VoiceStudio is not running
   - Close all related processes

3. **Check System Requirements**
   - Verify .NET 8.0 Runtime installed
   - Verify Python 3.10+ installed (if backend required)
   - Verify sufficient disk space

### After Upgrade

1. **Verify Installation**

   - Launch application
   - Verify projects load
   - Verify profiles accessible
   - Test basic functionality

2. **Report Issues**
   - If issues occur, report immediately
   - Include version information
   - Include error logs from `%APPDATA%\VoiceStudio\logs\`

### Before Rollback

1. **Backup Current Data**

   - Copy current user data to safe location
   - Note current version for reference

2. **Document Issues**
   - Note what functionality is broken
   - Note when issues started
   - Collect error logs

---

## Version History

### Version 1.0.0 (2025-01-28)

- Initial release
- Upgrade from 0.x.x supported
- Automatic data migration
- Rollback to previous versions supported

---

**Last Updated:** 2025-01-28  
**Maintained By:** Release Engineer  
**Gate:** H (Packaging and upgrades)
