# VoiceStudio Privacy Policy

**Last Updated:** 2026-02-09

VoiceStudio is committed to protecting your privacy. This policy explains what data we collect, how we use it, and how to control your privacy settings.

## Core Privacy Principles

1. **Local-First**: VoiceStudio operates primarily offline. Your audio files, project data, and voice recordings are stored locally on your computer.

2. **Opt-In Only**: Analytics and telemetry are disabled by default. You must explicitly enable them.

3. **No Personal Data**: We never collect personal information, audio content, or project files.

4. **Transparent**: This document clearly describes all data collection.

## Data We Collect (When Enabled)

### Usage Analytics (Opt-In)

When you enable usage analytics, we collect:

| Data Type | Description | Example |
|-----------|-------------|---------|
| Feature Usage | Which panels/tools you use | "Opened Voice Synthesis panel" |
| Performance Metrics | Synthesis times, app startup duration | "Synthesis completed in 2.3s" |
| Engine Selection | Which TTS engines you use | "Selected XTTS engine" |
| Session Duration | How long the app is open | "Session: 45 minutes" |

**We DO NOT collect:**
- Audio files or voice recordings
- Project content or text
- Personal information or identifiers
- File paths or folder names
- Voice profiles or cloning data

### Error Reporting (Opt-In)

When you enable error reporting, we collect:

| Data Type | Description | Example |
|-----------|-------------|---------|
| Crash Reports | Stack traces and error messages | "NullReferenceException in..." |
| System Info | OS version, GPU model | "Windows 11, RTX 3080" |
| App Version | VoiceStudio version | "v1.0.1" |

**We DO NOT collect:**
- Audio files or voice data
- Project content
- Personal files
- Sensitive system information

## Data Storage

All analytics data is stored **locally only** in:
```
%LocalAppData%\VoiceStudio\Analytics\
```

Currently, VoiceStudio does not transmit analytics data to external servers. This local-only storage allows us to:
- Provide usage statistics in-app
- Help diagnose issues during support
- Aggregate anonymous patterns for development prioritization

## How to Control Your Settings

### Enable or Disable Analytics

1. Open **Settings** (⚙️)
2. Navigate to **Privacy**
3. Toggle **Usage Analytics** on or off
4. Toggle **Error Reporting** on or off

### First-Run Consent

On first launch, you'll see a consent dialog asking about analytics. You can:
- Enable analytics
- Decline analytics
- Decide later

Your choice is saved and can be changed anytime in Settings.

### Clear Analytics Data

To delete all locally stored analytics:
1. Close VoiceStudio
2. Delete the folder: `%LocalAppData%\VoiceStudio\Analytics\`
3. Restart VoiceStudio

## Third-Party Services

VoiceStudio is designed to be **offline-capable**. The following optional features may communicate externally:

| Feature | External Service | When Used |
|---------|------------------|-----------|
| Update Check | GitHub Releases | When checking for updates |
| Model Download | Hugging Face | When downloading TTS models |

No analytics or personal data is shared with these services.

## Children's Privacy

VoiceStudio does not knowingly collect information from children under 13. The app does not require account creation or personal information.

## Changes to This Policy

We will update this policy as features evolve. Changes will be noted in the "Last Updated" date and communicated through release notes.

## Contact

For privacy questions or concerns:
- GitHub Issues: [VoiceStudio Repository]
- Email: privacy@voicestudio.dev (when available)

## Your Rights

You have the right to:
- **Opt out** of all data collection at any time
- **Delete** all locally stored analytics data
- **Request information** about what data is stored
- **Use VoiceStudio fully offline** with no data collection

---

## Summary

| Question | Answer |
|----------|--------|
| Is data collection required? | No, completely opt-in |
| Do you collect audio files? | Never |
| Do you collect personal info? | Never |
| Where is data stored? | Locally on your computer |
| Is data sent to servers? | No (currently local-only) |
| Can I delete my data? | Yes, anytime |
| Can I use the app offline? | Yes, fully functional offline |
