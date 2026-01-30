# Request Reproduction Tools

Tools for recording and replaying HTTP requests for debugging and regression testing.

## Overview

These tools help developers:
1. **Record** requests made to the backend during debugging
2. **Replay** recorded sessions to reproduce bugs
3. **Compare** responses to detect regressions

## Quick Start

### Recording Requests

Add the middleware to your FastAPI app:

```python
from tools.repro import RequestRecorderMiddleware

app.add_middleware(RequestRecorderMiddleware)
```

Enable recording programmatically:

```python
from tools.repro import enable_recording, disable_recording

# Start recording
session_id = enable_recording()

# ... perform actions ...

# Stop and save
session_file = disable_recording()
print(f"Session saved to: {session_file}")
```

Or via API endpoint (if configured):

```bash
# Start recording
curl -X POST http://localhost:8001/api/debug/recording/start

# Stop recording
curl -X POST http://localhost:8001/api/debug/recording/stop
```

### Replaying Sessions

```bash
# Replay a session
python -m tools.repro.request_replayer session_20260129_123456.json.gz

# With options
python -m tools.repro.request_replayer session.json.gz \
    --base-url http://localhost:8001 \
    --verbose \
    --stop-on-error \
    --output report.json
```

## Session Files

Sessions are saved as gzipped JSON files in `.buildlogs/repro_sessions/`:

```json
{
  "session_id": "20260129_123456",
  "started_at": "2026-01-29T12:34:56.789Z",
  "ended_at": "2026-01-29T12:35:00.123Z",
  "exchange_count": 5,
  "metadata": {},
  "exchanges": [
    {
      "request": {
        "timestamp": "2026-01-29T12:34:56.789Z",
        "method": "POST",
        "path": "/api/voice/synthesize",
        "query_string": "",
        "headers": {"content-type": "application/json"},
        "body": "{\"text\": \"Hello\", \"engine_id\": \"xtts\"}",
        "correlation_id": "cor_20260129123456_abc12345"
      },
      "response": {
        "status_code": 200,
        "headers": {"content-type": "application/json"},
        "body": null,
        "duration_ms": 1234.5
      },
      "error": null
    }
  ]
}
```

## API Reference

### RequestRecorderMiddleware

```python
RequestRecorderMiddleware(
    app,
    exclude_paths=["/api/health", "/api/docs", "/api/openapi.json"],
    max_body_size=1024*1024  # 1MB
)
```

### enable_recording

```python
enable_recording(
    session_id=None,      # Auto-generated if not provided
    output_dir=None,      # Default: .buildlogs/repro_sessions
    metadata=None,        # Additional metadata
) -> str  # Returns session_id
```

### disable_recording

```python
disable_recording() -> Optional[Path]  # Returns path to saved session
```

### replay_session

```python
replay_session(
    session_path: Path,
    base_url: str = "http://localhost:8001",
    timeout: float = 30.0,
    stop_on_error: bool = False,
    verbose: bool = False,
) -> SessionReplayReport
```

## Use Cases

### Debugging a Bug

1. Enable recording before reproducing the bug
2. Perform the actions that trigger the bug
3. Stop recording
4. Share the session file with the team
5. Replay to reproduce the exact sequence

### Regression Testing

1. Record a session with expected behavior
2. Add to test suite
3. Replay after changes to verify behavior is preserved

### Creating Golden Tests

1. Record a synthesis session
2. Extract successful exchanges
3. Add as golden test cases
