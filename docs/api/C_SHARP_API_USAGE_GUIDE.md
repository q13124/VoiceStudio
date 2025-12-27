# VoiceStudio Quantum+ C# API Usage Guide

Complete guide for using the VoiceStudio API from C# applications.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Backend Client Setup](#backend-client-setup)
3. [Authentication](#authentication)
4. [Common Operations](#common-operations)
5. [Error Handling](#error-handling)
6. [Best Practices](#best-practices)
7. [Code Examples](#code-examples)

---

## Getting Started

### Prerequisites

- .NET 8.0 or later
- VoiceStudio.BackendClient NuGet package (or generated client)
- Backend API running (default: `http://localhost:8000`)

### Installation

The C# backend client is generated from the OpenAPI schema. See `scripts/generate_csharp_client.ps1` for generation instructions.

---

## Backend Client Setup

### Basic Setup

```csharp
using VoiceStudio.Core.Services;
using VoiceStudio.App.Services;

// Get backend client from service provider
var backendClient = ServiceProvider.GetBackendClient();

// Or inject via dependency injection
public class MyService
{
    private readonly IBackendClient _backendClient;

    public MyService(IBackendClient backendClient)
    {
        _backendClient = backendClient;
    }
}
```

### Configuration

```csharp
// Configure base address
var httpClient = new HttpClient
{
    BaseAddress = new Uri("http://localhost:8000")
};

var backendClient = new BackendClient(httpClient);
```

---

## Authentication

Currently, VoiceStudio API does not require authentication for local use. All endpoints are accessible without API keys.

**Future Authentication Support:**

When authentication is implemented, it will use API key authentication:

```csharp
// Future implementation
var httpClient = new HttpClient
{
    BaseAddress = new Uri("https://api.voicestudio.com")
};

httpClient.DefaultRequestHeaders.Add("X-API-Key", "your-api-key-here");
var backendClient = new BackendClient(httpClient);
```

---

## Common Operations

### Voice Profiles

#### List Profiles

```csharp
var profiles = await _backendClient.GetProfilesAsync(cancellationToken);

foreach (var profile in profiles)
{
    Console.WriteLine($"Profile: {profile.Name} (Quality: {profile.QualityScore})");
}
```

#### Create Profile

```csharp
var request = new ProfileCreateRequest
{
    Name = "My Voice",
    Language = "en",
    Emotion = "neutral",
    Tags = new List<string> { "male", "professional" }
};

var profile = await _backendClient.CreateProfileAsync(request, cancellationToken);
Console.WriteLine($"Created profile: {profile.Id}");
```

#### Get Profile

```csharp
var profile = await _backendClient.GetProfileAsync("profile_123", cancellationToken);
Console.WriteLine($"Profile: {profile.Name}");
```

#### Update Profile

```csharp
var request = new ProfileUpdateRequest
{
    Name = "Updated Name",
    Tags = new List<string> { "updated", "tags" }
};

var updatedProfile = await _backendClient.UpdateProfileAsync("profile_123", request, cancellationToken);
```

#### Delete Profile

```csharp
var success = await _backendClient.DeleteProfileAsync("profile_123", cancellationToken);
if (success)
{
    Console.WriteLine("Profile deleted successfully");
}
```

### Voice Synthesis

#### Synthesize Voice

```csharp
var request = new VoiceSynthesizeRequest
{
    Text = "Hello, this is a test of voice synthesis.",
    VoiceProfileId = "profile_123",
    Language = "en",
    Speed = 1.0,
    Pitch = 0.0,
    Emotion = "neutral"
};

var response = await _backendClient.SynthesizeVoiceAsync(request, cancellationToken);
Console.WriteLine($"Audio URL: {response.AudioUrl}");
Console.WriteLine($"MOS Score: {response.QualityMetrics?.MosScore}");
```

### Projects

#### List Projects

```csharp
var projects = await _backendClient.GetProjectsAsync(cancellationToken);

foreach (var project in projects)
{
    Console.WriteLine($"Project: {project.Name}");
}
```

#### Create Project

```csharp
var request = new ProjectCreateRequest
{
    Name = "My Project",
    Description = "A voice cloning project",
    VoiceProfileIds = new List<string> { "profile_123" }
};

var project = await _backendClient.CreateProjectAsync(request, cancellationToken);
Console.WriteLine($"Created project: {project.Id}");
```

### Batch Jobs

#### List Jobs

```csharp
var jobs = await _backendClient.SendRequestAsync<object, Job[]>(
    "/api/jobs?status=running",
    null,
    HttpMethod.Get,
    cancellationToken
);

foreach (var job in jobs)
{
    Console.WriteLine($"Job {job.Id}: {job.Status} ({job.Progress}%)");
}
```

#### Get Job Status

```csharp
var job = await _backendClient.GetJobAsync("job_123", cancellationToken);
Console.WriteLine($"Job Status: {job.Status}, Progress: {job.Progress}%");
```

#### Cancel Job

```csharp
var success = await _backendClient.CancelJobAsync("job_123", cancellationToken);
```

### Quality Dashboard

#### Get Quality Dashboard

```csharp
var dashboard = await _backendClient.GetQualityDashboardAsync(cancellationToken);
Console.WriteLine($"Average MOS: {dashboard.OverallQuality?.AverageMos}");
Console.WriteLine($"Trend: {dashboard.OverallQuality?.Trend}");
```

#### Get Quality Presets

```csharp
var presets = await _backendClient.GetQualityPresetsAsync(cancellationToken);

foreach (var preset in presets)
{
    Console.WriteLine($"Preset: {preset.Name} - {preset.Description}");
}
```

### Training Datasets

#### List Training Datasets

```csharp
var datasets = await _backendClient.GetTrainingDatasetsAsync(cancellationToken);

foreach (var dataset in datasets)
{
    Console.WriteLine($"Dataset: {dataset.Name} (Size: {dataset.Size})");
}
```

#### Get Training Dataset

```csharp
var dataset = await _backendClient.GetTrainingDatasetAsync("dataset_123", cancellationToken);
Console.WriteLine($"Dataset: {dataset.Name}, Quality: {dataset.QualityScore}");
```

### Telemetry

#### Get Telemetry

```csharp
var telemetry = await _backendClient.GetTelemetryAsync(cancellationToken);
Console.WriteLine($"CPU Usage: {telemetry.System?.CpuUsage}%");
Console.WriteLine($"GPU Usage: {telemetry.System?.GpuUsage}%");
```

### Health Check

#### Get API Health

```csharp
var health = await _backendClient.GetApiHealthAsync(cancellationToken);
Console.WriteLine($"Status: {health.Status}, Version: {health.Version}");
```

---

## Error Handling

### Standard Error Handling

```csharp
try
{
    var profile = await _backendClient.GetProfileAsync("invalid_id", cancellationToken);
}
catch (HttpRequestException ex)
{
    // Handle HTTP errors (404, 500, etc.)
    Console.WriteLine($"HTTP Error: {ex.Message}");
}
catch (Exception ex)
{
    // Handle other errors
    Console.WriteLine($"Error: {ex.Message}");
}
```

### Retry Logic

The `BackendClient` includes built-in retry logic with exponential backoff:

```csharp
// Retry is automatic for transient failures
// Configure retry settings in BackendClient constructor
var backendClient = new BackendClient(httpClient)
{
    MaxRetries = 3,
    RetryDelay = TimeSpan.FromSeconds(1)
};
```

### Error Response Format

All errors follow a standardized format:

```json
{
  "error": {
    "code": "PROFILE_NOT_FOUND",
    "message": "Profile with ID 'profile_123' not found",
    "details": {},
    "recovery_suggestion": "Verify the profile ID and try again"
  }
}
```

---

## Best Practices

### 1. Use Cancellation Tokens

Always pass cancellation tokens for async operations:

```csharp
var profile = await _backendClient.GetProfileAsync("profile_123", cancellationToken);
```

### 2. Handle Errors Gracefully

```csharp
try
{
    var response = await _backendClient.SynthesizeVoiceAsync(request, cancellationToken);
    // Process response
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
{
    // Handle not found
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.BadRequest)
{
    // Handle bad request
}
catch (Exception ex)
{
    // Log and handle other errors
    _logger.LogError(ex, "Error synthesizing voice");
}
```

### 3. Use Dependency Injection

```csharp
// Register in DI container
services.AddSingleton<IBackendClient>(sp =>
{
    var httpClient = new HttpClient
    {
        BaseAddress = new Uri("http://localhost:8000")
    };
    return new BackendClient(httpClient);
});
```

### 4. Monitor Connection Status

```csharp
if (_backendClient.IsConnected)
{
    // Proceed with API calls
}
else
{
    // Handle disconnected state
}
```

### 5. Use BaseAddress Property

```csharp
var baseAddress = _backendClient.BaseAddress;
Console.WriteLine($"Connected to: {baseAddress}");
```

---

## Code Examples

### Complete Example: Voice Synthesis Workflow

```csharp
using VoiceStudio.Core.Services;
using System.Net.Http;

public class VoiceSynthesisService
{
    private readonly IBackendClient _backendClient;

    public VoiceSynthesisService(IBackendClient backendClient)
    {
        _backendClient = backendClient;
    }

    public async Task<string> SynthesizeTextAsync(
        string text,
        string profileId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Check connection
            if (!_backendClient.IsConnected)
            {
                throw new InvalidOperationException("Backend client is not connected");
            }

            // Create synthesis request
            var request = new VoiceSynthesizeRequest
            {
                Text = text,
                VoiceProfileId = profileId,
                Language = "en",
                Speed = 1.0,
                Pitch = 0.0
            };

            // Synthesize
            var response = await _backendClient.SynthesizeVoiceAsync(request, cancellationToken);

            // Check quality
            if (response.QualityMetrics?.MosScore < 3.0)
            {
                // Log warning for low quality
                _logger.LogWarning(
                    "Low quality synthesis: MOS Score {MosScore}",
                    response.QualityMetrics.MosScore
                );
            }

            return response.AudioUrl;
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error during voice synthesis");
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during voice synthesis");
            throw;
        }
    }
}
```

### Example: Batch Job Monitoring

```csharp
public async Task MonitorJobAsync(string jobId, CancellationToken cancellationToken)
{
    while (!cancellationToken.IsCancellationRequested)
    {
        var job = await _backendClient.GetJobAsync(jobId, cancellationToken);

        Console.WriteLine($"Job {job.Id}: {job.Status} ({job.Progress}%)");

        if (job.Status == "completed" || job.Status == "failed")
        {
            break;
        }

        await Task.Delay(TimeSpan.FromSeconds(2), cancellationToken);
    }
}
```

### Example: Quality Dashboard Monitoring

```csharp
public async Task MonitorQualityAsync(CancellationToken cancellationToken)
{
    var dashboard = await _backendClient.GetQualityDashboardAsync(cancellationToken);

    Console.WriteLine($"Overall Quality: {dashboard.OverallQuality?.AverageMos}");
    Console.WriteLine($"Trend: {dashboard.OverallQuality?.Trend}");

    foreach (var engine in dashboard.EnginePerformance ?? Enumerable.Empty<EnginePerformance>())
    {
        Console.WriteLine($"{engine.Engine}: MOS {engine.AverageMos} (Used {engine.UsageCount} times)");
    }
}
```

---

## Additional Resources

- **OpenAPI Schema:** `docs/api/openapi.json`
- **API Reference:** `docs/api/API_REFERENCE.md`
- **Error Codes:** `docs/api/ERROR_CODES.md`
- **Python Examples:** `docs/api/EXAMPLES.md`

---

**Last Updated:** 2025-01-28  
**Version:** 1.0.0
