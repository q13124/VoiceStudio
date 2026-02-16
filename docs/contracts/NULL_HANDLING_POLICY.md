# VoiceStudio Null Handling Policy

**GAP-I16: Contract Consistency - Null Handling**

## Overview

This document defines the canonical policy for handling null/None values across
the VoiceStudio codebase boundary between C# frontend and Python backend.

## Rule: Null Values Are OMITTED from JSON Payloads

All API payloads (requests and responses) follow a consistent serialization
policy where `null` and `None` values are **omitted** from the JSON output
rather than being explicitly included.

## Field State Mapping

| Field State | JSON Representation | C# Handling | Python Handling |
|-------------|---------------------|-------------|-----------------|
| Value present | `"field": "value"` | Property set to value | Field populated |
| Null/None | Field **omitted** | Property uses `default` or `HasValue` check | Field is `None` or uses `Field()` default |
| Empty string | `"field": ""` | Empty string | Empty string |
| Empty array | `"field": []` | Empty collection | Empty list |
| Zero/False | `"field": 0` / `"field": false` | Explicit zero/false | Explicit zero/false |

## Implementation

### Python Backend

**Base Model Configuration:**

All Pydantic models should inherit from `VoiceStudioBaseModel`:

```python
from backend.api.models import VoiceStudioBaseModel

class MyResponse(VoiceStudioBaseModel):
    required_field: str
    optional_field: str | None = None  # Omitted from JSON when None
    optional_int: int | None = None    # Omitted from JSON when None
```

**VoiceStudioBaseModel Features:**
- Overrides `model_dump()` to use `exclude_none=True` by default
- Overrides `model_dump_json()` to use `exclude_none=True` by default
- Uses `use_enum_values=True` for consistent enum serialization
- Uses `validate_assignment=True` for early error detection

**Manual Serialization:**

When manually constructing responses, use the serialization utility:

```python
from backend.api.serialization import serialize_response

# Returns dict with None values excluded
result = serialize_response(model)
```

### C# Frontend

**JSON Serializer Configuration:**

The frontend uses `JsonSerializerOptionsFactory` with `WhenWritingNull`:

```csharp
options.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
```

This matches the Python backend behavior.

**Receiving Optional Fields:**

When deserializing, optional fields may be absent from the JSON:

```csharp
public class MyResponse
{
    public string RequiredField { get; set; } = "";
    
    // May be null if omitted from JSON
    public string? OptionalField { get; set; }
    
    // Use property for default when absent
    public int OptionalInt { get; set; } = 0;
}
```

## Rationale

1. **Reduced Payload Size**: Omitting null values reduces JSON payload size,
   which is beneficial for network performance and logging.

2. **Clear Semantics**: The distinction between "not set" (field absent) and
   "explicitly empty" (empty string/array) is preserved.

3. **Cross-Language Consistency**: Both C# (`WhenWritingNull`) and Python
   (`exclude_none=True`) use the same behavior, eliminating serialization
   mismatches.

4. **Backward Compatibility**: Consumers can use default values when fields
   are absent, making API evolution safer.

## Migration Guide

### Migrating Python Models

**Before:**
```python
class SynthesisResponse(BaseModel):
    audio_path: str
    duration: Optional[float] = None
    
    def serialize(self):
        return self.model_dump()  # May include None values
```

**After:**
```python
from backend.api.models import VoiceStudioBaseModel

class SynthesisResponse(VoiceStudioBaseModel):
    audio_path: str
    duration: float | None = None
    
    # model_dump() now excludes None by default
```

### Key Changes

1. Inherit from `VoiceStudioBaseModel` instead of `BaseModel`
2. Use modern union syntax (`str | None`) instead of `Optional[str]`
3. Remove explicit `exclude_none=True` from `model_dump()` calls (now default)

## Exceptions

In rare cases where `null` must be explicitly serialized (e.g., to indicate
"clear this field"), use:

```python
# Python: Explicit include_none
model.model_dump(exclude_none=False)

# C#: Explicit JsonIgnoreCondition.Never on the property
[JsonIgnore(Condition = JsonIgnoreCondition.Never)]
public string? FieldThatMustSerializeNull { get; set; }
```

Document any such exceptions in the relevant API specification.

## References

- **ADR**: Future ADR to be created for cross-boundary serialization
- **C# JsonSerializerOptionsFactory**: `src/VoiceStudio.App/Utilities/JsonSerializerOptionsFactory.cs`
- **Python VoiceStudioBaseModel**: `backend/api/models.py`
- **Python Serialization Utilities**: `backend/api/serialization.py`

---

*Last updated: 2026-02-16*
*GAP Reference: GAP-I16 (Null Handling Inconsistent Across Boundaries)*
