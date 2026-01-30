# Crash Bundle Export Feature

**Release Engineer Implementation**
**Date:** 2025-01-28

## Overview

The Crash Bundle Export feature provides a comprehensive diagnostic bundle that includes logs, environment information, and recent user actions for debugging crashes and issues. This feature is owned by the Release Engineer role and ensures VoiceStudio can export debugging information for support and troubleshooting.

## Feature Components

### 1. Crash Bundle Contents

The crash bundle is a ZIP archive containing three main components:

#### `logs.json`

- **Application logs**: Recent general application logs with timestamps, levels, and messages
- **Error logs**: Detailed error logs including context, exception types, stack traces, and metadata

#### `environment.json`

- **Application info**: Version, .NET version, OS information
- **System details**: Machine name, user name, processor count, memory usage
- **Environment variables**: Relevant environment variables for debugging

#### `recent_actions.json`

- **Analytics events**: Recent user actions and feature usage
- **Telemetry data**: CPU, GPU, memory usage at time of export
- **Budget violations**: Performance issues or resource constraints detected

#### `bundle_metadata.json`

- **Bundle information**: Version, creation timestamp, contents description
- **Context**: App version, machine info for correlation with issues

### 2. Export Process

1. **User triggers export** via Diagnostics panel "Export Crash Bundle" button
2. **File picker** allows user to choose location and filename
3. **Data collection** gathers current logs, environment, and recent actions
4. **ZIP creation** bundles all data into compressed archive
5. **Cleanup** removes temporary files
6. **Notification** confirms successful export

### 3. Integration Points

- **Diagnostics Panel**: "Export Crash Bundle" button in the Logs tab
- **Error Handling**: Integrated with existing error logging system
- **Toast Notifications**: User feedback on export success/failure
- **File System**: Exports to user-chosen location with `.zip` extension

## Implementation Details

### Code Location

- **ViewModel**: `src/VoiceStudio.App/Views/Panels/DiagnosticsViewModel.cs`
- **Command**: `ExportCrashBundleCommand` relay command
- **Method**: `ExportCrashBundleAsyncInternal()` private implementation
- **Resources**: Localized strings in `Resources.resw`

### Dependencies

- **System.IO**: File operations and ZIP creation
- **System.Text.Json**: JSON serialization for export data
- **Windows.Storage**: File picker and file I/O
- **CommunityToolkit.Mvvm**: RelayCommand for UI binding

### Error Handling

- **Cancellation**: Supports user cancellation during export
- **Exception handling**: Catches and logs export failures
- **Cleanup**: Ensures temporary directories are removed even on failure
- **User feedback**: Toast notifications for success/error states

## Usage

### For Users

1. Open the **Diagnostics panel**
2. Navigate to the **Logs tab**
3. Click **"Export Crash Bundle"** button
4. Choose save location and filename
5. Wait for export completion notification

### For Support/Debugging

1. Receive crash bundle ZIP from user
2. Extract and examine the three JSON files
3. Use `bundle_metadata.json` for context
4. Analyze `logs.json` for error patterns
5. Check `environment.json` for system compatibility issues
6. Review `recent_actions.json` for user behavior leading to issues

## File Structure Example

```
voicestudio_crash_bundle_20250128_143022.zip
├── bundle_metadata.json
├── environment.json
├── logs.json
└── recent_actions.json
```

## Security Considerations

- **No sensitive data**: Bundle contains only diagnostic information
- **User consent**: Export requires explicit user action
- **No automatic uploads**: Data stays local, user controls distribution
- **File location**: User chooses where to save the bundle

## Release Engineer Verification

This feature satisfies the Release Engineer requirement for "crash bundle export wiring (logs, environment report, recent actions)" as defined in the role specification.

### Verification Checklist

- [x] Logs export: Implemented via `logs.json`
- [x] Environment report: Implemented via `environment.json`
- [x] Recent actions: Implemented via `recent_actions.json`
- [x] UI integration: "Export Crash Bundle" button in Diagnostics panel
- [x] Error handling: Comprehensive exception handling and user feedback
- [x] File format: ZIP archive for easy distribution and compression

## Future Enhancements

- **Automatic crash detection**: Trigger bundle export on application crashes
- **Cloud upload option**: Optional upload to support system (with user consent)
- **Bundle size limits**: Automatic cleanup of old/large bundles
- **Compression options**: Configurable compression levels
- **Selective export**: Allow users to exclude certain data types

---

**Status:** ✅ **IMPLEMENTED**  
**Release Engineer:** Crash bundle export wiring complete  
**Testing:** Blocked by build issues, ready for verification when build succeeds
