# VoiceStudio API Conventions

**GAP-INT-003**: Standardized API naming and WebSocket message conventions.

## REST API Naming Conventions

### URL Structure

```
/api/{version}/{resource}/{action}
/api/v1/voice/synthesize
/api/v1/profiles/{profile_id}
```

### HTTP Methods

| Method | Usage | Example |
|--------|-------|---------|
| GET | Retrieve resource(s) | `GET /api/v1/profiles` |
| POST | Create resource or perform action | `POST /api/v1/voice/synthesize` |
| PUT | Update entire resource | `PUT /api/v1/profiles/{id}` |
| PATCH | Partial update | `PATCH /api/v1/profiles/{id}` |
| DELETE | Remove resource | `DELETE /api/v1/profiles/{id}` |

### Naming Rules

1. **Use lowercase with hyphens** for multi-word resources:
   - ✅ `/api/v1/voice-profiles`
   - ❌ `/api/v1/voiceProfiles`
   - ❌ `/api/v1/voice_profiles`

2. **Use plural nouns** for collections:
   - ✅ `/api/v1/profiles`
   - ❌ `/api/v1/profile`

3. **Use verbs for actions** (non-CRUD operations):
   - ✅ `/api/v1/voice/synthesize`
   - ✅ `/api/v1/batch/process`
   - ❌ `/api/v1/voice/synthesis` (noun for action)

4. **Use path parameters** for resource IDs:
   - ✅ `/api/v1/profiles/{profile_id}`
   - ❌ `/api/v1/profiles?id={profile_id}`

5. **Use query parameters** for filtering, sorting, pagination:
   - ✅ `/api/v1/profiles?status=active&limit=10`

### Response Format

All API responses should follow this structure:

```json
{
    "success": true,
    "data": { ... },
    "message": "Optional message",
    "errors": null
}
```

Error responses:

```json
{
    "success": false,
    "data": null,
    "message": "Error description",
    "errors": [
        {
            "code": "VALIDATION_ERROR",
            "field": "text",
            "message": "Text is required"
        }
    ]
}
```

## WebSocket Message Protocol

### Message Format

All WebSocket messages **MUST** follow this structure:

```json
{
    "type": "<message_type>",
    "topic": "<optional_topic>",
    "payload": { ... },
    "timestamp": "<ISO8601>",
    "request_id": "<optional_correlation_id>"
}
```

### Standard Message Types

| Type | Direction | Description |
|------|-----------|-------------|
| `data` | Server→Client | Regular data messages |
| `error` | Server→Client | Error messages |
| `ack` | Server→Client | Acknowledgments |
| `ping` | Client→Server | Heartbeat request |
| `pong` | Server→Client | Heartbeat response |
| `subscribe` | Client→Server | Subscribe to topic |
| `unsubscribe` | Client→Server | Unsubscribe from topic |
| `start` | Both | Start streaming/operation |
| `stop` | Both | Stop streaming/operation |
| `complete` | Server→Client | Operation completed |
| `progress` | Server→Client | Progress updates |

### Domain-Specific Types

#### Audio/Synthesis
- `audio_chunk`: Audio data chunk
- `audio_complete`: Audio processing complete

#### Conversion
- `converted_chunk`: Converted audio chunk

#### Training
- `training_update`: Training progress
- `training_complete`: Training finished

#### Visualization
- `visualization_frame`: Visualization data
- `meters_update`: Audio meters data

### Error Message Format

```json
{
    "type": "error",
    "timestamp": "2025-01-30T12:00:00.000Z",
    "payload": {
        "message": "Human-readable error message",
        "code": "ERROR_CODE",
        "details": { ... }
    }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid input data |
| `ENGINE_ERROR` | Engine processing failed |
| `NOT_FOUND` | Resource not found |
| `UNAVAILABLE` | Service unavailable |
| `RATE_LIMITED` | Rate limit exceeded |
| `UNAUTHORIZED` | Authentication required |
| `INTERNAL_ERROR` | Internal server error |
| `CONNECTION_ERROR` | Connection failed |
| `TIMEOUT` | Operation timed out |

### Progress Message Format

```json
{
    "type": "progress",
    "timestamp": "2025-01-30T12:00:00.000Z",
    "payload": {
        "percent": 50,
        "message": "Processing audio...",
        "stage": "encoding"
    }
}
```

## Implementation

### Python Usage

```python
from backend.api.ws import (
    create_message, create_error, create_ack,
    create_progress, create_complete, MessageType, ErrorCode
)

# Send a data message
await ws.send_json(create_message(MessageType.AUDIO_CHUNK, {"data": chunk}))

# Send an error
await ws.send_json(create_error("Synthesis failed", code=ErrorCode.ENGINE_ERROR))

# Send progress
await ws.send_json(create_progress(50, "Processing audio...", stage="encoding"))

# Send completion
await ws.send_json(create_complete("Synthesis complete", result={"duration": 5.2}))
```

### TypeScript/Frontend Usage

```typescript
interface WebSocketMessage {
    type: string;
    topic?: string;
    payload?: Record<string, unknown>;
    timestamp: string;
    request_id?: string;
}

// Handle incoming message
function handleMessage(msg: WebSocketMessage) {
    switch (msg.type) {
        case 'audio_chunk':
            handleAudioChunk(msg.payload);
            break;
        case 'error':
            handleError(msg.payload);
            break;
        case 'progress':
            updateProgress(msg.payload.percent, msg.payload.message);
            break;
        case 'complete':
            handleComplete(msg.payload);
            break;
    }
}
```

## Migration Guide

When updating existing WebSocket code to use standardized messages:

1. Import the protocol helpers:
   ```python
   from backend.api.ws import create_message, create_error, MessageType
   ```

2. Replace raw dict sends with protocol helpers:
   ```python
   # Before
   await ws.send_json({"type": "error", "message": "Failed"})
   
   # After
   await ws.send_json(create_error("Failed", code=ErrorCode.ENGINE_ERROR))
   ```

3. Update message type strings to use `MessageType` constants:
   ```python
   # Before
   await ws.send_json({"type": "complete", ...})
   
   # After
   await ws.send_json(create_message(MessageType.COMPLETE, payload))
   ```

## References

- Protocol implementation: `backend/api/ws/protocol.py`
- WebSocket module: `backend/api/ws/`
- API routes: `backend/api/routes/`
