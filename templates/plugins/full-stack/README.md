# {{DISPLAY_NAME}} Full-Stack Plugin Template

A complete VoiceStudio plugin with Python backend and C# WinUI frontend working together.

## Quick Start

### 1. Customize Template Tokens

Replace these tokens in all files:
- `{{PLUGIN_NAME}}` → lowercase_identifier (e.g., `my_plugin`)
- `{{CLASS_NAME}}` → PascalCase (e.g., `MyPlugin`)
- `{{DISPLAY_NAME}}` → Human Readable Name
- `{{VERSION}}` → 1.0.0
- `{{AUTHOR}}` → Your Name
- `{{DESCRIPTION}}` → Plugin description

### 2. Project Structure

```
full-stack/
├── manifest.json          # Plugin metadata (full_stack type)
├── plugin.py              # Python backend with FastAPI routes
├── requirements.txt       # Python dependencies
├── SamplePlugin/
│   ├── Plugin.cs          # C# IPlugin implementation
│   ├── MainPanel.xaml     # WinUI panel layout
│   ├── MainPanel.xaml.cs  # Panel code-behind
│   └── MainPanelViewModel.cs  # MVVM ViewModel
└── tests/
    └── test_backend.py    # Backend tests
```

### 3. How It Works

1. **Backend** (`plugin.py`) — Provides API endpoints at `/api/plugin/{{PLUGIN_NAME}}/`
2. **Frontend** (`Plugin.cs`) — Registers UI panels and connects to backend
3. **Panel** — Uses `IBackendClient` to call backend endpoints

### 4. Backend API

```python
# GET /api/plugin/{{PLUGIN_NAME}}/status
# Returns: {"status": "active" | "inactive"}

# POST /api/plugin/{{PLUGIN_NAME}}/process
# Body: {"data": "..."}
# Returns: {"status": "Processed: ...", "processed_at": "..."}
```

### 5. Frontend Usage

```csharp
// In your ViewModel, call backend:
var result = await _backend.GetAsync<StatusResponse>(
    "/api/plugin/{{PLUGIN_NAME}}/status"
);
```

## Building

### Backend
```bash
pip install -r requirements.txt
```

### Frontend
```bash
cd SamplePlugin
dotnet build
```

## Testing

```bash
# Backend tests
pytest tests/ -v
```

## Resources

- [Getting Started Guide](../../../docs/plugins/getting-started.md)
- [Backend API Reference](../../../docs/plugins/api-reference-backend.md)
- [Frontend API Reference](../../../docs/plugins/api-reference-frontend.md)
- [Best Practices Guide](../../../docs/plugins/best-practices.md)

## License

MIT
