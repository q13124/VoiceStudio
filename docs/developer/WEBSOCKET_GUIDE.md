# WebSocket Guide

> **Version**: 1.0.0  
> **Last Updated**: 2026-02-04  
> **Status**: Active

## Overview

VoiceStudio uses WebSocket connections for real-time communication between the UI and backend. This guide documents the WebSocket architecture, topics, and integration patterns.

## Architecture

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   WinUI 3 UI    │◄──────────────────►│  FastAPI Backend │
│  (C# Client)    │    /ws/realtime    │  (Python Server) │
└─────────────────┘                    └─────────────────┘
        │                                       │
        │  Publishes/Subscribes                 │  Broadcasts Events
        │  to Topics                            │  from Services
        ▼                                       ▼
   ┌─────────┐                           ┌─────────────┐
   │ Topics  │                           │ Event Bus   │
   └─────────┘                           └─────────────┘
```

## Topics

### Synthesis Topics

| Topic | Direction | Description |
|-------|-----------|-------------|
| `synthesis/start` | Client→Server | Start synthesis job |
| `synthesis/progress` | Server→Client | Progress updates (0-100%) |
| `synthesis/complete` | Server→Client | Job completed with audio URL |
| `synthesis/error` | Server→Client | Job failed with error |

### Transcription Topics

| Topic | Direction | Description |
|-------|-----------|-------------|
| `transcription/start` | Client→Server | Start transcription |
| `transcription/progress` | Server→Client | Progress updates |
| `transcription/segment` | Server→Client | Real-time segment |
| `transcription/complete` | Server→Client | Full transcription |

### Engine Topics

| Topic | Direction | Description |
|-------|-----------|-------------|
| `engine/status` | Server→Client | Engine availability changes |
| `engine/telemetry` | Server→Client | Performance metrics |
| `engine/preflight` | Server→Client | Preflight check results |

### Job Topics

| Topic | Direction | Description |
|-------|-----------|-------------|
| `job/created` | Server→Client | New job queued |
| `job/progress` | Server→Client | Job progress update |
| `job/completed` | Server→Client | Job finished |
| `job/failed` | Server→Client | Job failed |

## Message Format

### Client to Server

```json
{
  "topic": "synthesis/start",
  "payload": {
    "text": "Hello world",
    "voice_id": "voice_001",
    "options": {
      "speed": 1.0,
      "pitch": 0.0
    }
  },
  "request_id": "uuid-1234"
}
```

### Server to Client

```json
{
  "topic": "synthesis/progress",
  "payload": {
    "job_id": "job_abc123",
    "progress": 45,
    "stage": "inference",
    "eta_seconds": 3.5
  },
  "timestamp": "2026-02-04T12:00:00Z"
}
```

## Backend Implementation

### WebSocket Endpoint

```python
# backend/api/ws/realtime.py
from fastapi import WebSocket
from app.core.events import EventBus

@router.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    async def on_event(topic: str, payload: dict):
        await websocket.send_json({
            "topic": topic,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    EventBus.subscribe("*", on_event)
    
    try:
        while True:
            data = await websocket.receive_json()
            topic = data.get("topic")
            payload = data.get("payload", {})
            
            await handle_client_message(topic, payload)
    except WebSocketDisconnect:
        EventBus.unsubscribe(on_event)
```

### Event Bus

```python
# app/core/events.py
class EventBus:
    _subscribers: Dict[str, List[Callable]] = {}
    
    @classmethod
    def publish(cls, topic: str, payload: dict):
        for subscriber in cls._subscribers.get(topic, []):
            asyncio.create_task(subscriber(topic, payload))
        for subscriber in cls._subscribers.get("*", []):
            asyncio.create_task(subscriber(topic, payload))
    
    @classmethod
    def subscribe(cls, topic: str, callback: Callable):
        cls._subscribers.setdefault(topic, []).append(callback)
```

## Frontend Implementation

### WebSocket Service

```csharp
// src/VoiceStudio.App/Services/WebSocketService.cs
public class WebSocketService : IWebSocketService
{
    private ClientWebSocket _socket;
    private readonly ConcurrentDictionary<string, Action<JsonElement>> _handlers;

    public async Task ConnectAsync(string url)
    {
        _socket = new ClientWebSocket();
        await _socket.ConnectAsync(new Uri(url), CancellationToken.None);
        _ = ReceiveLoopAsync();
    }

    public void Subscribe(string topic, Action<JsonElement> handler)
    {
        _handlers[topic] = handler;
    }

    private async Task ReceiveLoopAsync()
    {
        var buffer = new byte[4096];
        while (_socket.State == WebSocketState.Open)
        {
            var result = await _socket.ReceiveAsync(buffer, CancellationToken.None);
            if (result.MessageType == WebSocketMessageType.Text)
            {
                var message = JsonSerializer.Deserialize<WebSocketMessage>(buffer[..result.Count]);
                if (_handlers.TryGetValue(message.Topic, out var handler))
                {
                    handler(message.Payload);
                }
            }
        }
    }
}
```

### ViewModel Integration

```csharp
public class SynthesisViewModel : BaseViewModel
{
    private readonly IWebSocketService _ws;

    public SynthesisViewModel(IWebSocketService ws)
    {
        _ws = ws;
        _ws.Subscribe("synthesis/progress", OnProgress);
        _ws.Subscribe("synthesis/complete", OnComplete);
    }

    private void OnProgress(JsonElement payload)
    {
        var progress = payload.GetProperty("progress").GetInt32();
        DispatcherQueue.TryEnqueue(() => Progress = progress);
    }
}
```

## Connection Management

### Reconnection

The WebSocket service implements automatic reconnection:

```csharp
private async Task ReconnectLoopAsync()
{
    while (!_disposed)
    {
        if (_socket?.State != WebSocketState.Open)
        {
            try
            {
                await ConnectAsync(_serverUrl);
                await ResubscribeAllAsync();
            }
            catch (Exception ex)
            {
                _logger.LogWarning("Reconnect failed: {Error}", ex.Message);
                await Task.Delay(_reconnectDelay);
                _reconnectDelay = Math.Min(_reconnectDelay * 2, MaxReconnectDelay);
            }
        }
        await Task.Delay(1000);
    }
}
```

### Heartbeat

```json
{
  "topic": "system/ping",
  "payload": {},
  "request_id": "heartbeat-123"
}

{
  "topic": "system/pong",
  "payload": {
    "server_time": "2026-02-04T12:00:00Z"
  }
}
```

## Best Practices

1. **Use topic namespacing** - Organize topics by feature (e.g., `synthesis/`, `job/`)
2. **Include request_id** - Enable request/response correlation
3. **Handle disconnections** - Implement reconnection with backoff
4. **Validate messages** - Verify topic and payload structure
5. **Log events** - Track message flow for debugging

## Related Documentation

- [WebSocket Events Reference](../api/WEBSOCKET_EVENTS.md)
- [Real-time Architecture](../architecture/REALTIME_ARCHITECTURE.md)
- [Backend Services](SERVICE_ARCHITECTURE.md)
