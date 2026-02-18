# {{DISPLAY_NAME}} Engine Adapter Template

Thin adapter plugin template for wrapping existing `EngineProtocol`
implementations with plugin lifecycle and manifest metadata.

## Structure

- `manifest.json` - plugin metadata/capabilities
- `adapter.py` - engine wrapper
- `plugin.py` - plugin API + FastAPI routes

## Usage

1. Replace template tokens.
2. Wire `EngineProtocol` implementation in `plugin.py`.
3. Expose `/synthesize` and `/health`.
4. Keep all model/runtime logic in existing engine module.
