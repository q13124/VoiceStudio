# VoiceStudio Quantum+ API Migration Guide

Guide for developers migrating API calls to VoiceStudio Quantum+.

## Overview

This guide helps developers migrate API calls when upgrading VoiceStudio Quantum+ or adopting new API endpoints.

**Note:** This is the initial release (v1.0.0). No migration from previous versions is required. This guide is prepared for future API changes.

---

## API Versioning

### Current Version

**API Version:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**API Prefix:** `/api`

### Version Strategy

**Future Versions:**
- API versioning will be used for breaking changes
- Version specified in URL: `/api/v2/...`
- Deprecated endpoints marked in documentation
- Migration guides provided for major changes

---

## API Changes

### Version 1.0.0 (Initial Release)

**No Breaking Changes:** This is the initial release.

**New Endpoints:**
- All endpoints are new in this version
- See [ENDPOINTS.md](ENDPOINTS.md) for complete list

---

## Migration Scenarios

### Scenario 1: Adopting New Endpoints

**Example: Adding Quality Features**

**Before (Manual Quality Testing):**
```python
# Manual quality testing
result1 = synthesize(profile_id, text, engine="xtts")
result2 = synthesize(profile_id, text, engine="chatterbox")
# Manually compare results
```

**After (Using A/B Testing API):**
```python
# Use A/B Testing endpoint
response = requests.post(
    "http://localhost:8000/api/voice/ab-test",
    json={
        "profile_id": profile_id,
        "text": text,
        "engine_a": "xtts",
        "engine_b": "chatterbox"
    }
)
# Automatic comparison with metrics
winner = response.json()["winner"]
```

**Migration Steps:**
1. Identify manual processes
2. Find equivalent API endpoints
3. Update code to use new endpoints
4. Test thoroughly
5. Remove old code

### Scenario 2: Updating Request/Response Models

**Example: Enhanced Voice Synthesis Response**

**Before (Basic Response):**
```python
{
    "audio_id": "audio-123",
    "success": true
}
```

**After (Enhanced Response with Quality Metrics):**
```python
{
    "audio_id": "audio-123",
    "success": true,
    "quality_metrics": {
        "mos_score": 4.2,
        "similarity": 0.95,
        "naturalness": 0.92,
        "snr": 28.5,
        "artifacts": []
    }
}
```

**Migration Steps:**
1. Review new response structure
2. Update code to handle new fields
3. Use new fields if needed
4. Handle optional fields gracefully

### Scenario 3: Endpoint Deprecation

**Future Scenario: Endpoint Deprecated**

**Before (Deprecated Endpoint):**
```python
# Old endpoint (deprecated)
response = requests.get(
    "http://localhost:8000/api/old-endpoint"
)
```

**After (New Endpoint):**
```python
# New endpoint
response = requests.get(
    "http://localhost:8000/api/v2/new-endpoint"
)
```

**Migration Steps:**
1. Check deprecation notices
2. Find replacement endpoint
3. Update endpoint URL
4. Update request/response handling
5. Test thoroughly

---

## Code Examples

### Python (requests)

**Basic Request:**
```python
import requests

# Voice synthesis
response = requests.post(
    "http://localhost:8000/api/voice/synthesize",
    json={
        "profile_id": "profile-123",
        "text": "Hello, world!",
        "engine": "xtts"
    }
)

result = response.json()
audio_id = result["audio_id"]
```

**With Error Handling:**
```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(
        "http://localhost:8000/api/voice/synthesize",
        json={"profile_id": "profile-123", "text": "Hello"},
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")
```

### C# (HttpClient)

**Basic Request:**
```csharp
using System.Net.Http;
using System.Text;
using System.Text.Json;

var client = new HttpClient();
var request = new
{
    profile_id = "profile-123",
    text = "Hello, world!",
    engine = "xtts"
};

var json = JsonSerializer.Serialize(request);
var content = new StringContent(json, Encoding.UTF8, "application/json");

var response = await client.PostAsync(
    "http://localhost:8000/api/voice/synthesize",
    content
);

var result = await response.Content.ReadAsStringAsync();
var synthesizeResponse = JsonSerializer.Deserialize<VoiceSynthesizeResponse>(result);
```

**With Error Handling:**
```csharp
try
{
    var response = await client.PostAsync(url, content);
    response.EnsureSuccessStatusCode();
    var result = await response.Content.ReadAsStringAsync();
    return JsonSerializer.Deserialize<VoiceSynthesizeResponse>(result);
}
catch (HttpRequestException e)
{
    Console.WriteLine($"HTTP Error: {e.Message}");
    throw;
}
```

### JavaScript (fetch)

**Basic Request:**
```javascript
// Voice synthesis
const response = await fetch('http://localhost:8000/api/voice/synthesize', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        profile_id: 'profile-123',
        text: 'Hello, world!',
        engine: 'xtts'
    })
});

const result = await response.json();
const audioId = result.audio_id;
```

**With Error Handling:**
```javascript
try {
    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return result;
} catch (error) {
    console.error('Request failed:', error);
    throw error;
}
```

---

## Version Compatibility

### Backward Compatibility

**Current Policy:**
- New fields added to responses are optional
- Old endpoints remain functional during deprecation period
- Migration period provided for breaking changes

### Forward Compatibility

**Best Practices:**
- Handle optional fields gracefully
- Don't rely on undocumented fields
- Use versioned endpoints when available
- Test with latest API version

---

## Common Migration Patterns

### Pattern 1: Adding Optional Parameters

**Before:**
```python
response = requests.post(
    "/api/voice/synthesize",
    json={"profile_id": "123", "text": "Hello"}
)
```

**After (With Optional Parameters):**
```python
response = requests.post(
    "/api/voice/synthesize",
    json={
        "profile_id": "123",
        "text": "Hello",
        "quality_preset": "high",  # New optional parameter
        "language": "en"  # New optional parameter
    }
)
```

**Migration:** Add optional parameters as needed, old code continues to work.

### Pattern 2: Response Structure Changes

**Before:**
```python
result = response.json()
audio_id = result["audio_id"]
```

**After (Enhanced Response):**
```python
result = response.json()
audio_id = result["audio_id"]
# New fields available
quality_metrics = result.get("quality_metrics", {})
mos_score = quality_metrics.get("mos_score", 0.0)
```

**Migration:** Use `.get()` for optional fields, provide defaults.

### Pattern 3: Endpoint Consolidation

**Before (Multiple Endpoints):**
```python
# Old: Multiple endpoints
profile = requests.get("/api/profiles/123").json()
audio = requests.get(f"/api/audio/{profile['audio_id']}").json()
```

**After (Consolidated Endpoint):**
```python
# New: Single endpoint with related data
profile = requests.get("/api/v2/profiles/123?include=audio").json()
audio = profile["audio"]  # Included in response
```

**Migration:** Update to use consolidated endpoint, remove multiple calls.

---

## Testing Migration

### Testing Checklist

- [ ] All API calls updated
- [ ] Request formats correct
- [ ] Response handling updated
- [ ] Error handling tested
- [ ] Optional fields handled
- [ ] Backward compatibility verified
- [ ] Performance acceptable
- [ ] Documentation updated

### Testing Tools

**API Testing:**
- Postman - API testing
- curl - Command-line testing
- Python requests - Programmatic testing
- C# HttpClient - .NET testing

**Example Test:**
```python
import requests

def test_synthesis():
    response = requests.post(
        "http://localhost:8000/api/voice/synthesize",
        json={
            "profile_id": "test-profile",
            "text": "Test"
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "audio_id" in result
    assert "quality_metrics" in result
```

---

## Troubleshooting

### Common Issues

#### Issue: 404 Not Found

**Cause:** Endpoint URL incorrect or endpoint removed

**Solution:**
- Check endpoint URL in documentation
- Verify API version
- Check for endpoint deprecation

#### Issue: 400 Bad Request

**Cause:** Request format incorrect

**Solution:**
- Check request body format
- Verify required fields
- Check data types

#### Issue: Response Structure Changed

**Cause:** API response structure updated

**Solution:**
- Review new response structure
- Update code to handle new structure
- Use optional field access

---

## Best Practices

### Migration Planning

1. **Review Changes:**
   - Read migration guide
   - Review API documentation
   - Identify affected code

2. **Test Incrementally:**
   - Migrate one endpoint at a time
   - Test thoroughly
   - Verify functionality

3. **Maintain Compatibility:**
   - Support both old and new during transition
   - Gradual migration
   - Fallback to old if needed

### Code Quality

1. **Error Handling:**
   - Handle all error cases
   - Provide meaningful error messages
   - Log errors appropriately

2. **Type Safety:**
   - Use typed models
   - Validate responses
   - Handle optional fields

3. **Documentation:**
   - Document API usage
   - Update code comments
   - Keep examples current

---

## Resources

### Documentation

- [API Endpoints](ENDPOINTS.md) - Complete endpoint reference
- [API Reference](API_REFERENCE.md) - Detailed API documentation
- [Code Examples](EXAMPLES.md) - API usage examples
- [OpenAPI Specification](OPENAPI_SPECIFICATION.md) - OpenAPI/Swagger spec

### Support

- Check documentation first
- Review code examples
- Search existing issues
- Contact support if needed

---

## Summary

**Migration Steps:**

1. ✅ Review API changes
2. ✅ Identify affected code
3. ✅ Update API calls
4. ✅ Test thoroughly
5. ✅ Deploy gradually

**Key Points:**

- API versioning for breaking changes
- Backward compatibility during deprecation
- Optional fields for enhancements
- Migration guides for major changes

**Support:**

- Documentation: [ENDPOINTS.md](ENDPOINTS.md)
- Examples: [EXAMPLES.md](EXAMPLES.md)
- Reference: [API_REFERENCE.md](API_REFERENCE.md)

---

**Happy Migrating!**

---

**Last Updated:** 2025-01-28  
**API Version:** 1.0.0

