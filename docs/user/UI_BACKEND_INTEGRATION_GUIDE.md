# UI Backend Integration Guide
## VoiceStudio Quantum+ - User Guide

**Date:** 2025-01-28  
**Version:** 1.0  
**Status:** Complete

---

## Overview

This guide explains how the VoiceStudio Quantum+ UI integrates with the backend API, how data flows between the UI and backend, and how to troubleshoot common integration issues.

---

## Architecture Overview

### MVVM Pattern

VoiceStudio Quantum+ uses the **Model-View-ViewModel (MVVM)** pattern:

- **View (XAML)**: UI layout and presentation
- **ViewModel (C#)**: Business logic and data binding
- **Model**: Data structures and backend API responses

**Data Flow:**
```
User Input (UI) → ViewModel Property → Backend API → Response → ViewModel Property → UI Update
```

---

## Backend API Integration

### IBackendClient Service

All UI panels use the `IBackendClient` service to communicate with the backend API.

**Key Features:**
- Automatic retry logic (3 retries with 1-second delay)
- Circuit breaker pattern (prevents cascading failures)
- Connection status tracking
- WebSocket support for real-time updates
- Error handling and user-friendly error messages

### API Call Patterns

#### GET Requests
```csharp
var profiles = await _backendClient.GetAsync<List<VoiceProfile>>("/api/profiles");
```

#### POST Requests
```csharp
var request = new SynthesisRequest { Text = "Hello", ProfileId = "profile123" };
var response = await _backendClient.SendRequestAsync<SynthesisRequest, SynthesisResponse>(
    "/api/synthesize", 
    request
);
```

#### File Uploads
```csharp
var fileStream = File.OpenRead(filePath);
var response = await _backendClient.UploadFileAsync(
    "/api/profiles/upload", 
    fileStream, 
    "audio.wav"
);
```

---

## Data Binding

### Two-Way Binding (Input Controls)

**TextBox:**
```xml
<TextBox Text="{x:Bind ViewModel.Text, Mode=TwoWay}" />
```

**ComboBox:**
```xml
<ComboBox SelectedItem="{x:Bind ViewModel.SelectedProfile, Mode=TwoWay}" 
          ItemsSource="{x:Bind ViewModel.Profiles, Mode=OneWay}" />
```

### One-Way Binding (Display Controls)

**TextBlock:**
```xml
<TextBlock Text="{x:Bind ViewModel.StatusMessage, Mode=OneWay}" />
```

**ListView:**
```xml
<ListView ItemsSource="{x:Bind ViewModel.Items, Mode=OneWay}" />
```

---

## Error Handling

### Error Display

All panels use the `ErrorMessage` control to display errors consistently:

```xml
<controls:ErrorMessage 
    Message="{x:Bind ViewModel.ErrorMessage, Mode=OneWay}" 
    Visibility="{x:Bind ViewModel.HasError, Mode=OneWay, Converter={StaticResource BooleanToVisibilityConverter}}" />
```

### Error Types

**Network Errors:**
- Connection failures
- Timeout errors
- Service unavailable

**HTTP Errors:**
- 4xx (Client errors): Invalid input, not found, unauthorized
- 5xx (Server errors): Internal server error, service unavailable

**Validation Errors:**
- Invalid input format
- Missing required fields
- Out-of-range values

### Error Recovery

**Retry Logic:**
- Automatic retry (3 attempts)
- Manual retry via ErrorMessage control
- Circuit breaker prevents repeated failures

---

## Loading States

### LoadingOverlay Control

All panels use the `LoadingOverlay` control to show loading states:

```xml
<controls:LoadingOverlay 
    IsLoading="{x:Bind ViewModel.IsLoading, Mode=OneWay}" 
    LoadingMessage="Loading data..." />
```

### Loading State Management

**ViewModel Pattern:**
```csharp
private async Task LoadDataAsync()
{
    try
    {
        IsLoading = true;
        ErrorMessage = null;
        HasError = false;
        
        var data = await _backendClient.GetAsync<List<Item>>("/api/items");
        Items.Clear();
        foreach (var item in data)
        {
            Items.Add(item);
        }
    }
    catch (Exception ex)
    {
        ErrorMessage = ErrorHandler.GetUserFriendlyMessage(ex);
        HasError = true;
    }
    finally
    {
        IsLoading = false;
    }
}
```

---

## Real-Time Updates

### WebSocket Integration

VoiceStudio Quantum+ supports real-time updates via WebSocket:

**Connection:**
```csharp
var webSocketService = _backendClient.WebSocketService;
if (webSocketService != null)
{
    await webSocketService.ConnectAsync(new[] { "synthesis_status", "job_progress" });
    webSocketService.MessageReceived += OnWebSocketMessage;
}
```

**Message Handling:**
```csharp
private void OnWebSocketMessage(object sender, WebSocketMessage message)
{
    if (message.Topic == "synthesis_status")
    {
        var status = JsonSerializer.Deserialize<SynthesisStatus>(message.Data);
        UpdateUI(status);
    }
}
```

---

## Input Validation

### Validation Patterns

**Before Backend Call:**
```csharp
var validation = InputValidator.ValidateSynthesisText(Text);
if (!validation.IsValid)
{
    ErrorMessage = validation.ErrorMessage;
    HasError = true;
    return;
}
```

**Command CanExecute:**
```csharp
public bool CanSynthesize => 
    SelectedProfile != null && 
    !string.IsNullOrWhiteSpace(Text) && 
    !IsLoading;

SynthesizeCommand = new AsyncRelayCommand(SynthesizeAsync, () => CanSynthesize);
```

### Available Validators

- `ValidateSynthesisText(string text)` - Validates text for synthesis
- `ValidateProfileName(string name)` - Validates profile name
- `ValidateProjectName(string name)` - Validates project name
- `ValidateLanguageCode(string language)` - Validates language code
- `ValidateFilePath(string path)` - Validates file path
- `ValidateAudioFileExtension(string filename)` - Validates audio file extension

---

## Common Workflows

### Voice Synthesis Workflow

1. **Select Profile**: User selects voice profile from ComboBox
2. **Enter Text**: User enters text in TextBox
3. **Click Synthesize**: Button triggers SynthesizeCommand
4. **Validation**: ViewModel validates input
5. **API Call**: Backend API called with synthesis request
6. **Response**: Backend returns audio URL/ID
7. **UI Update**: Audio player enabled, quality metrics displayed

### Profile Creation Workflow

1. **Click Create**: User clicks Create Profile button
2. **Upload Audio**: File picker opens, user selects audio file
3. **Validation**: File validated (extension, size)
4. **Upload**: File uploaded to backend
5. **Processing**: Backend processes audio and creates profile
6. **Response**: Profile data returned
7. **UI Update**: Profile added to list, available for use

### Training Workflow

1. **Create Dataset**: User creates training dataset
2. **Add Audio Files**: User adds audio file IDs
3. **Start Training**: User clicks Start Training button
4. **Job Creation**: Backend creates training job
5. **Status Updates**: Job status updates via polling or WebSocket
6. **UI Update**: Training progress displayed, logs shown

---

## Troubleshooting

### Common Issues

#### "Failed to connect to backend"
**Solution:** 
- Check backend service is running
- Verify backend URL in settings
- Check network connection
- Review connection status in Diagnostics panel

#### "Operation timed out"
**Solution:**
- Check backend is processing requests
- Verify network connection
- Try again (automatic retry will attempt 3 times)
- Check backend logs for issues

#### "Invalid response format"
**Solution:**
- Backend may have returned unexpected data
- Check backend API version compatibility
- Review error logs for details
- Contact support if issue persists

#### "Validation failed"
**Solution:**
- Review error message for specific validation issue
- Check input format requirements
- Verify required fields are filled
- Check input length limits

---

## Best Practices

### For Users

1. **Wait for Loading**: Don't click buttons multiple times during loading
2. **Check Errors**: Read error messages carefully for guidance
3. **Validate Input**: Ensure input meets requirements before submitting
4. **Retry on Failure**: Use retry button if operation fails
5. **Check Connection**: Verify backend connection in Diagnostics panel

### For Developers

1. **Always Validate**: Validate input before sending to backend
2. **Handle Errors**: Always use try-catch blocks for async operations
3. **Show Loading**: Always set IsLoading during async operations
4. **Clear Errors**: Clear error state on successful operations
5. **Use Commands**: Use IAsyncRelayCommand for async operations

---

## API Usage Patterns

### Standard CRUD Operations

**Create:**
```csharp
var request = new CreateRequest { Name = "Item", Description = "Description" };
var response = await _backendClient.SendRequestAsync<CreateRequest, CreateResponse>(
    "/api/items", 
    request
);
```

**Read:**
```csharp
var items = await _backendClient.GetAsync<List<Item>>("/api/items");
```

**Update:**
```csharp
var request = new UpdateRequest { Id = "item123", Name = "Updated Name" };
var response = await _backendClient.PutAsync<UpdateRequest, UpdateResponse>(
    "/api/items/item123", 
    request
);
```

**Delete:**
```csharp
await _backendClient.DeleteAsync("/api/items/item123");
```

---

## Summary

VoiceStudio Quantum+ UI integrates seamlessly with the backend API through:

- **IBackendClient**: Centralized API communication
- **MVVM Pattern**: Clean separation of concerns
- **Data Binding**: Automatic UI updates
- **Error Handling**: User-friendly error messages
- **Loading States**: Clear operation feedback
- **Input Validation**: Prevents invalid data submission
- **WebSocket**: Real-time updates support

All panels follow consistent patterns for reliability and user experience.

---

**Last Updated:** 2025-01-28  
**Version:** 1.0

