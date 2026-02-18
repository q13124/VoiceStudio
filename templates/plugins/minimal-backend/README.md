# {{DISPLAY_NAME}}

A minimal VoiceStudio backend plugin template.

## Quick Start

### 1. Customize for Your Plugin

Edit the following files and replace template tokens:

- `manifest.json` — Update name, version, author, description
  - `{{PLUGIN_NAME}}` → lowercase_identifier
  - `{{DISPLAY_NAME}}` → Human Readable Name
  - `{{VERSION}}` → e.g., 1.0.0
  - `{{AUTHOR}}` → Your Name

- `plugin.py` — Replace `{{CLASS_NAME}}` with capitalized plugin name
  - Search and replace `{{CLASS_NAME}}` with your class name

### 2. Add Dependencies

Edit `requirements.txt` if your plugin needs external packages:

```
requests>=2.28.0
numpy>=1.20.0
```

Then install:

```bash
pip install -r requirements.txt
```

### 3. Customize Endpoints

Add your own API routes by adding methods to `{{CLASS_NAME}}Plugin`:

```python
@router.post("/my_endpoint")
async def my_endpoint(self, request: MyRequest) -> MyResponse:
    # Your logic here
    return MyResponse(...)
```

### 4. Update Permissions

In `manifest.json`, add permissions your plugin needs:

```json
{
  "permissions": [
    "filesystem.read.workspace",
    "network.localhost"
  ]
}
```

See the best practices guide for all available permissions.

## Testing

Run tests:

```bash
pytest tests/ -v
```

Tests use FastAPI TestClient to verify routes work correctly.

## API Endpoints

This template provides:

### GET /api/plugin/{{PLUGIN_NAME}}/status

Get plugin status.

**Response**:
```json
{
  "status": "active",
  "plugin_name": "{{PLUGIN_NAME}}",
  "version": "{{VERSION}}"
}
```

### POST /api/plugin/{{PLUGIN_NAME}}/message

Process a message.

**Request**:
```json
{
  "message": "hello world"
}
```

**Response**:
```json
{
  "message": "Received: hello world",
  "processed_at": "2025-02-16T10:30:45.123456"
}
```

## Code Organization

- `manifest.json` — Plugin metadata
- `plugin.py` — Main plugin implementation
- `tests/` — Unit tests
- `requirements.txt` — Python dependencies

## Next Steps

1. **Rename your plugin** — Follow the customization steps above
2. **Add your logic** — Implement your business logic in `plugin.py`
3. **Write tests** — Add tests to `tests/test_plugin.py`
4. **Configure settings** — Add plugin settings in manifest's `settings_schema`
5. **Request permissions** — Add required permissions to manifest
6. **Test** — Run `pytest tests/ -v`
7. **Deploy** — Place your plugin directory in VoiceStudio's `plugins/` folder

## Resources

- [Getting Started Guide](../../../docs/plugins/getting-started.md)
- [Backend API Reference](../../../docs/plugins/api-reference-backend.md)
- [Best Practices Guide](../../../docs/plugins/best-practices.md)

## License

MIT (update in manifest.json if different)
