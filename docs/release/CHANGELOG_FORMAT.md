# VoiceStudio Quantum+ Changelog Format

This document defines the standard format for changelogs in VoiceStudio Quantum+.

**Last Updated:** 2025-01-28  
**Version:** 1.0

---

## Overview

VoiceStudio Quantum+ follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format with some customizations for our project.

---

## Changelog Structure

### File Location

- **Main Changelog:** `CHANGELOG.md` (root directory)
- **Release-Specific:** `docs/release/CHANGELOG_v[VERSION].md`

### Format

```markdown
# Changelog

All notable changes to VoiceStudio Quantum+ will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features that are not yet released

### Changed
- Changes to existing features

### Deprecated
- Features that will be removed in a future release

### Removed
- Features that have been removed

### Fixed
- Bug fixes

### Security
- Security fixes

## [1.1.0] - 2025-02-15

### Added
- New voice synthesis engine: Whisper TTS
- Batch processing for multiple files
- Export to MP3 format

### Changed
- Improved timeline performance by 30%
- Updated UI theme colors

### Fixed
- Fixed crash when loading large audio files
- Fixed memory leak in effects chain

### Security
- Fixed XSS vulnerability in search feature

## [1.0.0] - 2025-01-15

### Added
- Initial release
- Voice cloning with multiple engines
- Timeline editing
- Effects processing
```

---

## Change Categories

### Added

New features, capabilities, or functionality.

**Examples:**
- New voice synthesis engine
- New audio effect
- New export format
- New keyboard shortcut
- New API endpoint

**Format:**
```markdown
### Added
- New feature name
  - Description of what it does
  - How to use it
  - Any important notes
```

### Changed

Changes to existing features that are backward compatible.

**Examples:**
- Performance improvements
- UI/UX improvements
- API improvements (non-breaking)
- Default behavior changes

**Format:**
```markdown
### Changed
- Feature name
  - What changed
  - Why it changed
  - Impact on users
```

### Deprecated

Features that are still available but will be removed in a future release.

**Examples:**
- Old API endpoints
- Legacy features
- Deprecated configuration options

**Format:**
```markdown
### Deprecated
- Feature name
  - Why it's deprecated
  - Migration path
  - Removal timeline
```

### Removed

Features that have been removed in this release.

**Examples:**
- Removed features
- Removed API endpoints
- Removed configuration options

**Format:**
```markdown
### Removed
- Feature name
  - Why it was removed
  - Migration path (if applicable)
```

### Fixed

Bug fixes and issue resolutions.

**Examples:**
- Crash fixes
- Memory leak fixes
- UI bug fixes
- Performance fixes

**Format:**
```markdown
### Fixed
- Issue description
  - What was broken
  - How it was fixed
  - Impact on users
```

### Security

Security vulnerabilities that have been fixed.

**Examples:**
- XSS vulnerabilities
- SQL injection fixes
- Authentication fixes
- Data encryption improvements

**Format:**
```markdown
### Security
- Security issue description
  - Vulnerability type
  - Impact
  - Fix details
```

---

## Version Format

### Semantic Versioning

VoiceStudio Quantum+ uses **Semantic Versioning** (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes (backward compatible)

### Pre-release Versions

- `1.0.0-alpha.1` - Alpha release
- `1.0.0-beta.1` - Beta release
- `1.0.0-rc.1` - Release candidate

### Date Format

Use ISO 8601 format: `YYYY-MM-DD`

**Example:** `2025-02-15`

---

## Writing Guidelines

### Be Specific

❌ **Bad:**
```markdown
- Fixed bugs
```

✅ **Good:**
```markdown
- Fixed crash when loading audio files larger than 500MB
```

### Be User-Focused

❌ **Bad:**
```markdown
- Refactored audio processing pipeline
```

✅ **Good:**
```markdown
- Improved audio processing performance by 30%, reducing synthesis time
```

### Group Related Changes

```markdown
### Added
- New voice synthesis engine: Whisper TTS
  - Supports 50+ languages
  - Improved quality over previous engines
  - Available in Voice Synthesis panel
```

### Link to Issues

When possible, link to GitHub issues or pull requests:

```markdown
- Fixed crash when loading large audio files ([#123](https://github.com/voicestudio/issues/123))
```

---

## Examples

### Example 1: Minor Release

```markdown
## [1.1.0] - 2025-02-15

### Added
- New voice synthesis engine: Whisper TTS
  - Supports 50+ languages
  - Improved quality and naturalness
  - Available in Voice Synthesis panel

- Batch processing for multiple files
  - Process up to 100 files at once
  - Progress tracking and error handling
  - Available in Batch Processing panel

### Changed
- Improved timeline performance by 30%
  - Faster rendering of large projects
  - Smoother scrubbing and playback
  - Reduced memory usage

### Fixed
- Fixed crash when loading audio files larger than 500MB
- Fixed memory leak in effects chain
- Fixed UI glitch in mixer panel
```

### Example 2: Patch Release

```markdown
## [1.0.1] - 2025-01-20

### Fixed
- Fixed crash when exporting to MP3 format
- Fixed incorrect quality metrics calculation
- Fixed UI text overflow in Profiles panel

### Security
- Fixed XSS vulnerability in search feature
  - Input sanitization improved
  - No user action required
```

### Example 3: Major Release

```markdown
## [2.0.0] - 2025-03-01

### Added
- New project format (v2)
  - Improved performance
  - Better compatibility
  - See migration guide for details

### Changed
- Project file format updated (breaking change)
  - Old projects automatically migrated on first open
  - Backup recommended before upgrading
  - See MIGRATION_GUIDE.md for details

### Removed
- Legacy project format (v1)
  - No longer supported
  - Use migration tool to convert old projects
```

---

## Automation

### Generate Changelog Entry

Use the provided PowerShell script to generate changelog entries:

```powershell
.\scripts\generate-changelog-entry.ps1 -Version "1.1.0" -Date "2025-02-15"
```

### Validate Changelog Format

```powershell
.\scripts\validate-changelog.ps1 -ChangelogPath "CHANGELOG.md"
```

---

## Best Practices

1. **Update Frequently**
   - Add entries as changes are made
   - Don't wait until release

2. **Be Consistent**
   - Use same format for all entries
   - Follow the same structure

3. **Be Clear**
   - Write for users, not just developers
   - Explain impact and benefits

4. **Link to Details**
   - Link to issues, PRs, or documentation
   - Provide migration guides for breaking changes

5. **Review Before Release**
   - Check for completeness
   - Verify accuracy
   - Ensure consistency

---

## Checklist

Before adding a changelog entry:

- [ ] Change is categorized correctly
- [ ] Description is clear and user-focused
- [ ] Impact is explained
- [ ] Links to related issues/PRs (if applicable)
- [ ] Migration steps included (for breaking changes)
- [ ] Formatting is consistent

---

**Last Updated:** 2025-01-28  
**Version:** 1.0

