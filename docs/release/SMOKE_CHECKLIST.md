# Smoke Test Checklist - VoiceStudio Quantum+

**Last Updated:** 2025-01-28  
**Purpose:** Quick verification checklist to ensure core functionality works before release.

---

## Pre-Release Smoke Tests

### ✅ Application Launch
- [ ] Application starts without errors
- [ ] Main window displays correctly
- [ ] No console errors or warnings on startup
- [ ] All panels load without crashes
- [ ] Status bar shows correct information

### ✅ Backend Connection
- [ ] Backend API is accessible
- [ ] Health check endpoint responds
- [ ] API version matches expected version
- [ ] No connection errors in logs

### ✅ Core Panels
- [ ] **Profiles Panel**
  - [ ] Profiles list loads
  - [ ] Can create new profile
  - [ ] Can edit existing profile
  - [ ] Can delete profile (with confirmation)
  - [ ] Search/filter works

- [ ] **Timeline Panel**
  - [ ] Timeline displays correctly
  - [ ] Can add clips
  - [ ] Can play/pause
  - [ ] Can scrub timeline
  - [ ] Projects list loads

- [ ] **Effects Mixer Panel**
  - [ ] Channels display
  - [ ] Can adjust volume
  - [ ] Can add effects
  - [ ] Routing works

- [ ] **Library Panel**
  - [ ] Audio files list loads
  - [ ] Can preview audio
  - [ ] Can import files
  - [ ] Search works

### ✅ Keyboard Shortcuts
- [ ] Ctrl+P opens Command Palette
- [ ] Ctrl+K opens Global Search
- [ ] Ctrl+1-9 switches panels
- [ ] Ctrl+S saves
- [ ] Escape closes dialogs/overlays

### ✅ Toast Notifications
- [ ] Success toasts appear and auto-dismiss
- [ ] Error toasts appear and require dismissal
- [ ] Warning toasts appear and auto-dismiss
- [ ] Info toasts appear and auto-dismiss
- [ ] Progress toasts show progress

### ✅ Error Handling
- [ ] Network errors display user-friendly messages
- [ ] Validation errors show inline
- [ ] Error messages include retry options when applicable
- [ ] No unhandled exceptions crash the app

### ✅ UI Responsiveness
- [ ] UI doesn't freeze during operations
- [ ] Loading overlays appear for long operations
- [ ] Empty states display when no data
- [ ] Skeleton screens show during loading

### ✅ Settings
- [ ] Settings panel opens
- [ ] Can change settings
- [ ] Settings persist after restart
- [ ] Theme changes apply immediately

### ✅ File Operations
- [ ] Can create new project
- [ ] Can open existing project
- [ ] Can save project
- [ ] Can export audio
- [ ] Can import audio

### ✅ Help & Documentation
- [ ] Help panel opens
- [ ] Keyboard shortcuts reference accessible
- [ ] About dialog shows version
- [ ] Documentation links work

---

## Post-Release Smoke Tests

### ✅ Installation
- [ ] MSIX installer runs without errors
- [ ] Application installs correctly
- [ ] Application appears in Start menu
- [ ] Application can be uninstalled cleanly

### ✅ First Launch
- [ ] Welcome dialog appears (if enabled)
- [ ] Default panels load
- [ ] No errors on first run
- [ ] Settings are initialized

### ✅ Update Mechanism
- [ ] Update check works
- [ ] Update notification appears
- [ ] Update can be downloaded
- [ ] Update can be installed

---

## Critical Path Tests

These must pass for any release:

1. ✅ Application launches
2. ✅ Backend connects
3. ✅ Can create profile
4. ✅ Can synthesize audio
5. ✅ Can play audio
6. ✅ Can save project
7. ✅ No crashes during normal use

---

## Performance Checks

- [ ] Application starts in < 5 seconds
- [ ] Panel switching is instant (< 100ms)
- [ ] No memory leaks after 30 minutes of use
- [ ] CPU usage reasonable (< 20% idle)
- [ ] No excessive disk I/O

---

## Accessibility Checks

- [ ] Screen reader can navigate UI
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] High contrast mode works
- [ ] All interactive elements have tooltips

---

## Platform-Specific Checks

### Windows 10
- [ ] Runs on Windows 10 (19041+)
- [ ] No compatibility warnings

### Windows 11
- [ ] Runs on Windows 11
- [ ] UI scales correctly
- [ ] Dark mode works

---

## Known Issues to Verify

Before release, verify these known issues are either:
- Fixed
- Documented in release notes
- Acceptable for release

---

## Test Environment

- **OS Version:** Windows 10/11
- **Backend:** Running on localhost:8000
- **Test Duration:** 15-30 minutes
- **Tester:** [Name]

---

## Sign-Off

- [ ] All critical path tests pass
- [ ] No blocking issues found
- [ ] Ready for release

**Tester:** _________________  
**Date:** _________________  
**Version:** _________________

---

## Notes

_Add any observations, issues, or notes here:_
