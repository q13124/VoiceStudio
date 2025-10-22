"""
Bootstrap launcher that swaps the stub XTTS adapter with the real Coqui XTTS v2 adapter
and then runs the Voice Engine Router on the configured host/port.
"""

from __future__ import annotations
import uvicorn
from services.api.voice_engine_router import app, REGISTRY, CONFIG
from services.adapters.engine_xtts import XTTSRealAdapter

# Replace the stub adapter with the real one
REGISTRY._adapters["xtts"] = XTTSRealAdapter()

if __name__ == "__main__":
    print(f"Starting VoiceStudio Voice Engine Router on {CONFIG.host}:{CONFIG.port}")
    print(f"Available engines: {list(REGISTRY._adapters.keys())}")
    uvicorn.run(app, host=CONFIG.host, port=CONFIG.port, log_level="info")
