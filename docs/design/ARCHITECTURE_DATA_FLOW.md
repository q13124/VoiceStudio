# VoiceStudio Architecture - Data Flow & Contracts

## Data Flow Architecture

```
[WinUI 3 (VoiceStudio.App)]
      |
      |  JSON over HTTP/WebSocket
      v
[Backend API (Python/Node)]
      |
      |  internal function calls
      v
[MCP Bridge Layer] ---> [MCP Servers (Figma/Magic/Flux/Shadcn/TTS/etc.)]
```

## Communication Protocol

### Frontend → Backend

The WinUI 3 application communicates with the backend via:
- **HTTP REST API** for synchronous operations
- **WebSocket** for real-time updates and streaming

### Backend → MCP Bridge

The backend makes internal function calls to the MCP Bridge layer, which:
- Normalizes requests to MCP protocol
- Routes to appropriate MCP servers
- Transforms responses to shared contract format

### MCP Servers

MCP servers provide:
- **Figma**: Design tokens and UI components
- **Magic UI**: UI component generation
- **Flux UI**: Advanced UI patterns
- **Shadcn**: Component library
- **TTS/VC**: Voice synthesis and cloning models
- **Other**: Additional specialized services

## Shared Contracts

All communication between frontend and backend uses JSON schemas defined in `shared/contracts/`.

### McpOperationRequest

Generic request format for MCP-backed operations:

```json
{
  "title": "McpOperationRequest",
  "type": "object",
  "properties": {
    "requestId": { "type": "string" },
    "operation": { "type": "string" },
    "source": { "type": "string" },
    "payload": { "type": "object" }
  },
  "required": ["requestId", "operation", "payload"]
}
```

**Fields:**
- `requestId`: Unique identifier for request tracking
- `operation`: Operation name (e.g., "analyze_voice", "suggest_chain")
- `source`: Source of request ("ui", "batch", "training")
- `payload`: Operation-specific data

### McpOperationResponse

Generic response format:

```json
{
  "title": "McpOperationResponse",
  "type": "object",
  "properties": {
    "requestId": { "type": "string" },
    "status": { "type": "string", "enum": ["ok", "error"] },
    "data": { "type": "object" },
    "error": { "type": "string" }
  },
  "required": ["requestId", "status"]
}
```

**Fields:**
- `requestId`: Matches the request ID
- `status`: "ok" or "error"
- `data`: Response data (when status is "ok")
- `error`: Error message (when status is "error")

### AnalyzeVoiceRequest

Specific request for voice analysis:

```json
{
  "title": "AnalyzeVoiceRequest",
  "type": "object",
  "properties": {
    "profileId": { "type": "string" },
    "clipId": { "type": "string" },
    "analysisModes": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["profileId", "clipId"]
}
```

**Fields:**
- `profileId`: Voice profile identifier
- `clipId`: Audio clip identifier
- `analysisModes`: Array of analysis types (e.g., ["lufs", "timbre", "similarity"])

**Backend Processing:**
The backend maps this to an MCP operation:
```json
{
  "requestId": "...",
  "operation": "analyze_voice",
  "source": "ui",
  "payload": {
    "profileId": "...",
    "clipId": "...",
    "analysisModes": [...]
  }
}
```

## Contract Files

All contract schemas are stored in `shared/contracts/`:

- `mcp_operation.schema.json` - Generic MCP request
- `mcp_operation_response.schema.json` - Generic MCP response
- `analyze_voice_request.schema.json` - Voice analysis request
- `layout_state.schema.json` - Panel layout state (for future use)

## Implementation Notes

### Frontend (VoiceStudio.App)

- Uses `IBackendClient` interface from `VoiceStudio.Core`
- Sends requests as JSON over HTTP/WebSocket
- Receives responses and updates UI accordingly
- No direct MCP communication (goes through backend)

### Backend (Python/Node)

- Receives JSON requests from frontend
- Validates against contract schemas
- Maps to MCP operations
- Calls MCP Bridge layer
- Returns normalized responses

### MCP Bridge

- Translates backend requests to MCP protocol
- Routes to appropriate MCP servers
- Normalizes MCP responses to contract format
- Handles errors and timeouts

## Future Extensions

Additional contract schemas can be added as needed:
- Voice cloning requests
- Training job requests
- Batch processing requests
- Real-time streaming protocols

All new contracts should follow the same pattern:
- Defined in `shared/contracts/`
- JSON Schema format
- Versioned for compatibility
- Documented in this architecture

