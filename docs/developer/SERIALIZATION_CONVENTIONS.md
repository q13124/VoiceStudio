# Serialization Conventions

This document defines the JSON serialization conventions used for communication between the VoiceStudio C# frontend and Python backend.

## Overview

VoiceStudio uses a hybrid architecture with:
- **Frontend**: WinUI 3 (C#) with `System.Text.Json`
- **Backend**: FastAPI (Python) with Pydantic models

Both sides must serialize and deserialize JSON in a consistent manner to ensure reliable data exchange.

## Property Naming Convention: snake_case

**All JSON properties use `snake_case` naming.**

| C# Property Name | JSON Property Name | Python Property Name |
|------------------|-------------------|----------------------|
| `VoiceProfileId` | `voice_profile_id` | `voice_profile_id` |
| `IsActive` | `is_active` | `is_active` |
| `SampleCount` | `sample_count` | `sample_count` |
| `CreatedAt` | `created_at` | `created_at` |

### C# Implementation

The `SnakeCaseJsonNamingPolicy` in `VoiceStudio.App.Utilities` handles conversion:

```csharp
// Use JsonSerializerOptionsFactory for consistent options
var options = JsonSerializerOptionsFactory.BackendApi;
var json = JsonSerializer.Serialize(myObject, options);
```

### Python Implementation

Pydantic models automatically use snake_case. FastAPI responses serialize correctly by default:

```python
from pydantic import BaseModel

class VoiceProfile(BaseModel):
    voice_profile_id: str
    is_active: bool
    sample_count: int
```

## DateTime Format: ISO 8601 with Z Suffix

**All datetime values use ISO 8601 format with UTC timezone.**

### Canonical Format

```
yyyy-MM-ddTHH:mm:ssZ
```

Examples:
- `2024-01-15T10:30:00Z`
- `2024-06-20T14:45:30Z`

### With Microseconds

```
yyyy-MM-ddTHH:mm:ss.ffffffZ
```

Examples:
- `2024-01-15T10:30:00.123456Z`

### Accepted Formats (Reading)

The C# deserializer accepts all common ISO 8601 variants:

| Format | Example | Accepted |
|--------|---------|----------|
| Z suffix | `2024-01-15T10:30:00Z` | ✅ |
| +00:00 offset | `2024-01-15T10:30:00+00:00` | ✅ |
| With microseconds | `2024-01-15T10:30:00.123456Z` | ✅ |
| With timezone offset | `2024-01-15T10:30:00+05:30` | ✅ |

### C# Implementation

Use `Iso8601DateTimeConverter` from `VoiceStudio.App.Utilities`:

```csharp
// Already included in JsonSerializerOptionsFactory.BackendApi
options.Converters.Add(new Iso8601DateTimeConverter());
options.Converters.Add(new Iso8601NullableDateTimeConverter());
```

### Python Implementation

Use the datetime utilities in `backend.api.utils.datetime_utils`:

```python
from backend.api.utils.datetime_utils import (
    utc_now,
    to_iso8601,
    to_iso8601_with_micros,
    from_iso8601,
    timestamp_now,
)

# Generate current timestamp
ts = timestamp_now()  # "2024-01-15T10:30:00Z"

# Convert datetime to ISO 8601
dt = utc_now()
iso_str = to_iso8601(dt)

# Parse ISO 8601 string
dt = from_iso8601("2024-01-15T10:30:00Z")
```

## Numeric Values

### Integers

Serialized as JSON numbers:

```json
{ "sample_count": 42 }
```

### Floating-Point Numbers

Serialized as JSON numbers with reasonable precision:

```json
{ "start_time": 10.123456, "duration": 5.5 }
```

### Numbers as Strings (Parsing)

The C# client accepts numbers serialized as strings for robustness:

```json
{ "sample_rate": "22050" }
```

This is enabled via:
```csharp
options.NumberHandling = JsonNumberHandling.AllowReadingFromString;
```

## Boolean Values

Use lowercase JSON booleans:

```json
{ "is_active": true, "streaming": false }
```

## Null Handling

### Serialization

Null values are **omitted** from JSON output by default:

```csharp
options.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
```

### Deserialization

Null values and missing fields are handled gracefully:

```json
{ "id": "test", "emotion": null }
```

```csharp
public class VoiceProfile
{
    public string Id { get; set; }
    public string? Emotion { get; set; }  // Will be null
    public string Language { get; set; } = "en";  // Uses default
}
```

## Enum Values

**Enums are serialized as lowercase strings.**

### C# Implementation

```csharp
options.Converters.Add(new JsonStringEnumConverter());
```

### Python Implementation

```python
from enum import Enum

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
```

### JSON Output

```json
{ "status": "active" }
```

## Collections

### Lists/Arrays

Serialized as JSON arrays:

```json
{ "tags": ["premium", "female", "narrator"] }
```

Empty lists are serialized as empty arrays:

```json
{ "tags": [] }
```

### Dictionaries

Serialized as JSON objects:

```json
{
  "metadata": {
    "engine": "xtts_v2",
    "sample_rate": 22050
  }
}
```

## Common JSON Serializer Options

### C# (JsonSerializerOptionsFactory.BackendApi)

```csharp
new JsonSerializerOptions
{
    PropertyNamingPolicy = SnakeCaseJsonNamingPolicy.Instance,
    PropertyNameCaseInsensitive = true,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    NumberHandling = JsonNumberHandling.AllowReadingFromString,
    Converters =
    {
        new JsonStringEnumConverter(),
        new Iso8601DateTimeConverter(),
        new Iso8601NullableDateTimeConverter(),
    }
};
```

### Python (Pydantic Model)

```python
from pydantic import BaseModel
from datetime import datetime

class ApiModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        }
```

## Testing Serialization

### Python Tests

Run serialization round-trip tests:

```bash
python -m pytest tests/contract/test_serialization_roundtrip.py -v
```

### C# Tests

Run C# serialization tests:

```bash
dotnet test tests/contract/VoiceStudio.ContractTests.csproj --filter "FullyQualifiedName~SerializationRoundTripTests"
```

## Troubleshooting

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Property not mapped | Case mismatch | Ensure snake_case on both sides |
| DateTime parse error | Wrong format | Use ISO 8601 with Z suffix |
| Number parse error | String value | Enable `AllowReadingFromString` |
| Null field present | Different null handling | Check `DefaultIgnoreCondition` |

### Debugging Tips

1. **Log raw JSON**: Add logging to capture actual JSON exchanged
2. **Use round-trip tests**: Test serialization → deserialization → serialization
3. **Check property names**: Verify snake_case conversion for complex names
4. **Validate datetime format**: Ensure all dates use ISO 8601 UTC format

## Related Documentation

- [API Contract Evolution](CONTRACT_EVOLUTION_POLICY.md) - Breaking change guidelines
- [Backend API Reference](../REFERENCE/BACKEND_API.md) - API endpoints
- [MCP Optimization Guide](MCP_OPTIMIZATION_GUIDE.md) - Development tools
