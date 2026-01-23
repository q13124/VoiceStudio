# Known Issues

This document lists known issues in VoiceStudio Quantum+ and their workarounds (if available).

**Last Updated:** 2025-01-27  
**Version:** 1.0.0

---

## Critical Issues

### None

No critical issues are currently known.

---

## High Priority Issues

### None

No high priority issues are currently known.

---

## Medium Priority Issues

### GPU Memory Management

**Issue:** Engines may consume significant GPU memory, especially with large models.

**Symptoms:**
- Out of memory errors during synthesis
- Slow performance after multiple operations
- GPU memory not released after operations

**Workaround:**
- Restart the application periodically
- Use CPU mode for less memory-intensive operations
- Close unused engines
- Reduce batch size for batch processing

**Planned Fix:** Improved memory management in v1.1.0

**Status:** Under investigation

---

### First-Time Engine Initialization

**Issue:** First-time engine initialization can be slow, especially for large models.

**Symptoms:**
- Long loading times on first use
- Application appears frozen during initialization

**Workaround:**
- Wait for initialization to complete
- Pre-load engines on startup (if option available)
- Use smaller models for faster initialization

**Planned Fix:** Background initialization and progress indicators in v1.1.0

**Status:** Planned

---

### Large Audio File Processing

**Issue:** Processing very large audio files (>1 hour) may cause performance issues.

**Symptoms:**
- Slow processing times
- High memory usage
- Application may become unresponsive

**Workaround:**
- Split large files into smaller segments
- Process in batch mode
- Use lower quality settings for preview
- Increase available RAM

**Planned Fix:** Streaming processing for large files in v1.2.0

**Status:** Planned

---

## Low Priority Issues

### UI Scaling on High DPI Displays

**Issue:** Some UI elements may appear small on high DPI displays (4K, 5K monitors).

**Symptoms:**
- Text appears small
- Controls difficult to click
- Icons appear pixelated

**Workaround:**
- Adjust Windows display scaling
- Use lower resolution display mode
- Zoom in browser/documentation views

**Planned Fix:** Improved DPI scaling in v1.1.0

**Status:** Planned

---

### Python Package Installation

**Issue:** Python package installation may fail if Python is not in PATH.

**Symptoms:**
- "Python not found" errors
- Package installation fails
- Backend fails to start

**Workaround:**
- Add Python to system PATH
- Install Python packages manually
- Use full path to Python executable
- Reinstall Python with "Add to PATH" option

**Planned Fix:** Better Python detection and installation guidance in v1.1.0

**Status:** Planned

---

### File Association on First Launch

**Issue:** File associations (.voiceproj, .vprofile) may not work immediately after installation.

**Symptoms:**
- Double-clicking project files doesn't open VoiceStudio
- "Open with" dialog appears

**Workaround:**
- Restart Windows after installation
- Manually associate file types in Windows Settings
- Re-run installer

**Planned Fix:** Improved file association handling in v1.1.0

**Status:** Planned

---

## Minor Issues

### Tooltip Display Delay

**Issue:** Tooltips may have a slight delay before appearing.

**Symptoms:**
- Tooltips don't appear immediately on hover
- Inconsistent tooltip timing

**Workaround:**
- Hover longer over controls
- Use keyboard shortcuts instead

**Planned Fix:** Optimized tooltip timing in v1.1.0

**Status:** Low priority

---

### Status Bar Update Frequency

**Issue:** Status bar updates may not reflect real-time changes immediately.

**Symptoms:**
- Status bar shows outdated information
- Updates appear delayed

**Workaround:**
- Refresh view manually
- Check logs for detailed information

**Planned Fix:** Improved status bar update mechanism in v1.1.0

**Status:** Low priority

---

## Platform-Specific Issues

### Windows 10 Version 1903-1909

**Issue:** Some WinUI 3 features may not be fully available on older Windows 10 versions.

**Symptoms:**
- Some UI elements may not render correctly
- Performance may be reduced

**Workaround:**
- Update to Windows 10 version 2004 or later
- Update to Windows 11

**Planned Fix:** Improved compatibility in v1.1.0

**Status:** Under investigation

---

### Windows 11 on ARM

**Issue:** Application may not run natively on ARM-based Windows 11 devices.

**Symptoms:**
- Application fails to start
- Performance issues
- Compatibility warnings

**Workaround:**
- Use x64 emulation (if available)
- Wait for ARM64 build

**Planned Fix:** ARM64 build in v2.0.0

**Status:** Planned

---

## Engine-Specific Issues

### XTTS v2 - Model Download

**Issue:** XTTS v2 models may not download automatically on first use.

**Symptoms:**
- "Model not found" errors
- Engine fails to initialize

**Workaround:**
- Manually download models
- Check model path configuration
- Verify internet connection

**Planned Fix:** Automatic model download in v1.1.0

**Status:** Planned

---

### Chatterbox TTS - GPU Requirements

**Issue:** Chatterbox TTS requires GPU for optimal performance.

**Symptoms:**
- Very slow synthesis on CPU
- High CPU usage
- Timeout errors

**Workaround:**
- Use GPU-enabled system
- Use alternative engines (XTTS, Tortoise) for CPU
- Reduce quality settings

**Planned Fix:** CPU optimization in v1.2.0

**Status:** Under investigation

---

### Tortoise TTS - Memory Usage

**Issue:** Tortoise TTS may use significant memory, especially in HQ mode.

**Symptoms:**
- High memory usage
- Out of memory errors
- Slow performance

**Workaround:**
- Use standard quality mode
- Process smaller batches
- Close other applications

**Planned Fix:** Memory optimization in v1.1.0

**Status:** Planned

---

## Reporting Issues

If you encounter an issue not listed here:

1. **Check Documentation**
   - Review [Troubleshooting Guide](docs/user/TROUBLESHOOTING.md)
   - Check [User Manual](docs/user/USER_MANUAL.md)

2. **Search Existing Issues**
   - Check GitHub Issues (if available)
   - Search known issues database

3. **Report New Issue**
   - Include version number
   - Describe steps to reproduce
   - Include error messages
   - Attach log files (if applicable)
   - Provide system information

---

## Issue Status Definitions

- **Under Investigation:** Issue is being investigated
- **Planned:** Fix is planned for a future release
- **Fixed:** Issue has been fixed (will be removed in next release)
- **Won't Fix:** Issue will not be fixed (with explanation)
- **Duplicate:** Issue is a duplicate of another issue

---

## Version-Specific Issues

### Version 1.0.0

All known issues for version 1.0.0 are listed above.

---

**Note:** This document is updated with each release. Check the version number to ensure you have the latest information.

