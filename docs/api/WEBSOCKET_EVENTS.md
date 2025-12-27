# VoiceStudio Quantum+ WebSocket Events

Real-time updates via WebSocket connections.

## Overview

VoiceStudio supports WebSocket connections for real-time updates including:
- VU meter updates
- Training progress
- Batch job progress
- General events

## Connection

### Legacy Endpoint (Heartbeat Only)

**URL:** `ws://localhost:8000/ws/events`

**Purpose:** Simple heartbeat for connection testing

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events');
```

### Enhanced Endpoint (Real-time Updates)

**URL:** `ws://localhost:8000/ws/realtime?topics=meters,training,batch`

**Query Parameters:**
- `topics` (optional): Comma-separated list of topics to subscribe to
  - `meters`: VU meter updates
  - `training`: Training progress updates
  - `batch`: Batch job progress updates
  - `general`: General events
  - `quality`: Real-time quality preview updates (IDEA 69)
  - Omit for all topics

**Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/realtime?topics=meters,training');
```

## Event Format

All events follow this format:

```json
{
  "topic": "event_topic",
  "payload": {
    // Event-specific data
  },
  "timestamp": "2025-01-27T12:00:00Z"
}
```

## Event Topics

### Meters

**Topic:** `meters`

**Purpose:** Real-time VU meter updates

**Payload:**
```json
{
  "project_id": "project-123",
  "channels": {
    "track-1": {
      "left": -12.5,
      "right": -12.3,
      "peak_left": -3.0,
      "peak_right": -3.0
    },
    "track-2": {
      "left": -18.2,
      "right": -18.0,
      "peak_left": -6.0,
      "peak_right": -6.0
    }
  },
  "master": {
    "left": -6.5,
    "right": -6.3,
    "peak_left": -1.0,
    "peak_right": -1.0
  }
}
```

**Update Frequency:** ~30 Hz (30 updates per second)

**Example:**
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.topic === 'meters') {
    updateVUMeters(data.payload);
  }
};
```

### Training

**Topic:** `training`

**Purpose:** Training job progress updates

**Payload:**
```json
{
  "training_id": "training-123",
  "status": "running",
  "progress": 0.65,
  "epoch": 32,
  "total_epochs": 50,
  "loss": 0.0234,
  "validation_loss": 0.0289,
  "eta_seconds": 1200,
  "message": "Training epoch 32/50"
}
```

**Status Values:**
- `pending`: Waiting to start
- `running`: Currently training
- `completed`: Training finished
- `failed`: Training failed
- `cancelled`: Training cancelled

**Update Frequency:** ~1 Hz (1 update per second) or on epoch completion

**Example:**
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.topic === 'training') {
    updateTrainingProgress(data.payload);
  }
};
```

### Batch

**Topic:** `batch`

**Purpose:** Batch job progress updates

**Payload:**
```json
{
  "job_id": "batch-123",
  "status": "running",
  "progress": 0.45,
  "current_item": 9,
  "total_items": 20,
  "completed_items": 8,
  "failed_items": 1,
  "eta_seconds": 300,
  "current_text": "Processing item 9 of 20"
}
```

**Status Values:**
- `pending`: Waiting in queue
- `running`: Currently processing
- `completed`: All items processed
- `failed`: Job failed
- `cancelled`: Job cancelled

**Update Frequency:** On each item completion or periodically

**Example:**
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.topic === 'batch') {
    updateBatchProgress(data.payload);
  }
};
```

### General

**Topic:** `general`

**Purpose:** General application events

**Payload Examples:**

**Engine Status:**
```json
{
  "event_type": "engine_status",
  "engine": "chatterbox",
  "status": "ready",
  "message": "Engine initialized"
}
```

**Error:**
```json
{
  "event_type": "error",
  "error_code": "ENGINE_ERROR",
  "message": "Engine initialization failed",
  "details": {}
}
```

**Info:**
```json
{
  "event_type": "info",
  "message": "Synthesis completed",
  "audio_id": "audio-123"
}
```

### Quality Preview

**Topic:** `quality`

**Purpose:** Real-time quality preview updates during synthesis, enhancement, and processing (IDEA 69)

**Payload Examples:**

**Multi-Pass Synthesis Quality Update:**
```json
{
  "process_type": "multipass_synthesis",
  "audio_id": "audio-123",
  "pass_number": 2,
  "total_passes": 3,
  "quality_metrics": {
    "mos_score": 4.2,
    "similarity": 0.85,
    "naturalness": 0.78,
    "artifact_score": 0.1,
    "has_clicks": false,
    "has_distortion": false
  },
  "quality_score": 0.82,
  "improvement": 0.05
}
```

**Artifact Removal Progress:**
```json
{
  "process_type": "artifact_removal",
  "audio_id": "audio-123",
  "artifacts_detected": ["clicks", "pops"],
  "artifacts_removed": ["clicks"],
  "quality_improvement": 0.15,
  "progress": 0.65
}
```

**Post-Processing Stage Update:**
```json
{
  "process_type": "post_processing",
  "audio_id": "audio-123",
  "stage": "denoise",
  "stage_progress": 0.8,
  "quality_before": 0.70,
  "quality_after": 0.78,
  "improvement": 0.08,
  "total_stages": 4,
  "completed_stages": 2
}
```

**Voice Characteristic Analysis:**
```json
{
  "process_type": "characteristic_analysis",
  "audio_id": "audio-123",
  "similarity_score": 0.88,
  "preservation_score": 0.92,
  "recommendations": ["Consider prosody control", "High pitch variation detected"]
}
```

**Update Frequency:** Real-time during processing (varies by process type)

**Example:**
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.topic === 'quality') {
    updateQualityPreview(data.payload);
  }
};
```

### Heartbeat

**Topic:** `heartbeat`

**Purpose:** Connection keepalive (legacy endpoint only)

**Payload:**
```json
{
  "n": 42
}
```

**Update Frequency:** Every 2 seconds

## Connection Lifecycle

### Connecting

1. **Create WebSocket:**
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/realtime?topics=meters,training');
   ```

2. **Handle Open:**
   ```javascript
   ws.onopen = () => {
     console.log('WebSocket connected');
   };
   ```

3. **Handle Messages:**
   ```javascript
   ws.onmessage = (event) => {
     const data = JSON.parse(event.data);
     handleEvent(data);
   };
   ```

4. **Handle Errors:**
   ```javascript
   ws.onerror = (error) => {
     console.error('WebSocket error:', error);
   };
   ```

5. **Handle Close:**
   ```javascript
   ws.onclose = () => {
     console.log('WebSocket closed');
     // Reconnect logic
   };
   ```

### Reconnection

**Recommended:** Implement exponential backoff reconnection

```javascript
function reconnect() {
  let delay = 1000;
  const maxDelay = 30000;
  
  const attempt = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/realtime');
    
    ws.onopen = () => {
      delay = 1000; // Reset delay on success
    };
    
    ws.onclose = () => {
      setTimeout(attempt, delay);
      delay = Math.min(delay * 2, maxDelay);
    };
  };
  
  attempt();
}
```

## Error Handling

### Connection Errors

**Error Types:**
- Connection refused (backend not running)
- Network errors
- Timeout errors

**Handling:**
- Implement retry logic
- Show user-friendly error messages
- Fall back to polling if WebSocket unavailable

### Message Errors

**Invalid JSON:**
- Log error
- Continue listening for next message

**Unknown Topic:**
- Ignore if not subscribed
- Log warning if subscribed

## Best Practices

1. **Subscribe Only to Needed Topics:**
   - Reduces bandwidth
   - Improves performance
   - Example: `?topics=meters` for meters only

2. **Handle Disconnections:**
   - Implement reconnection logic
   - Show connection status to user
   - Cache last known state

3. **Throttle Updates:**
   - For high-frequency topics (meters)
   - Update UI at reasonable rate (30 FPS max)
   - Batch updates if needed

4. **Error Recovery:**
   - Handle connection errors gracefully
   - Fall back to polling if WebSocket fails
   - Log errors for debugging

## Examples

### Python Client

```python
import asyncio
import websockets
import json

async def listen_events():
    uri = "ws://localhost:8000/ws/realtime?topics=meters,training,quality"
    
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data["topic"] == "meters":
                print(f"Meters: {data['payload']}")
            elif data["topic"] == "training":
                print(f"Training: {data['payload']}")
            elif data["topic"] == "quality":
                print(f"Quality: {data['payload']}")

asyncio.run(listen_events())
```

### C# Client

```csharp
using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

public class WebSocketClient
{
    private ClientWebSocket ws;
    private CancellationTokenSource cts;

    public async Task ConnectAsync()
    {
        ws = new ClientWebSocket();
        cts = new CancellationTokenSource();
        
        var uri = new Uri("ws://localhost:8000/ws/realtime?topics=meters,training");
        await ws.ConnectAsync(uri, cts.Token);
        
        _ = Task.Run(ReceiveLoop);
    }

    private async Task ReceiveLoop()
    {
        var buffer = new byte[4096];
        
        while (ws.State == WebSocketState.Open)
        {
            var result = await ws.ReceiveAsync(
                new ArraySegment<byte>(buffer), 
                cts.Token
            );
            
            if (result.MessageType == WebSocketMessageType.Text)
            {
                var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                var data = JsonSerializer.Deserialize<WebSocketEvent>(message);
                HandleEvent(data);
            }
        }
    }
}
```

### JavaScript/TypeScript Client

```typescript
class VoiceStudioWebSocket {
  private ws: WebSocket;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;

  connect(topics: string[] = []) {
    const topicParam = topics.length > 0 
      ? `?topics=${topics.join(',')}` 
      : '';
    const url = `ws://localhost:8000/ws/realtime${topicParam}`;
    
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => {
      console.log('Connected');
      this.reconnectDelay = 1000;
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleEvent(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onclose = () => {
      console.log('Disconnected, reconnecting...');
      this.reconnect();
    };
  }

  private handleEvent(data: WebSocketEvent) {
    switch (data.topic) {
      case 'meters':
        this.onMetersUpdate(data.payload);
        break;
      case 'training':
        this.onTrainingUpdate(data.payload);
        break;
      case 'batch':
        this.onBatchUpdate(data.payload);
        break;
      case 'quality':
        this.onQualityUpdate(data.payload);
        break;
    }
  }

  private reconnect() {
    setTimeout(() => {
      this.connect();
      this.reconnectDelay = Math.min(
        this.reconnectDelay * 2,
        this.maxReconnectDelay
      );
    }, this.reconnectDelay);
  }
}
```

## Testing

### Test Connection

```bash
# Using wscat (install: npm install -g wscat)
wscat -c ws://localhost:8000/ws/realtime?topics=meters
```

### Test Heartbeat (Legacy)

```bash
wscat -c ws://localhost:8000/ws/events
```

## Limitations

1. **Connection Limits:**
   - Multiple connections supported
   - Each connection independent

2. **Message Size:**
   - Keep payloads reasonable (< 1 MB)
   - Large payloads may be split

3. **Rate Limiting:**
   - No rate limiting currently
   - High-frequency updates may impact performance

## Troubleshooting

### Connection Fails

- Verify backend is running
- Check firewall settings
- Verify port 8000 is accessible
- Check backend logs

### No Messages Received

- Verify topics subscribed
- Check backend is sending events
- Verify WebSocket state (should be OPEN)
- Check browser console for errors

### High CPU Usage

- Reduce update frequency
- Subscribe to fewer topics
- Throttle UI updates
- Use requestAnimationFrame for UI updates

---

**For more information:**
- [API Reference](API_REFERENCE.md)
- [Code Examples](EXAMPLES.md)

