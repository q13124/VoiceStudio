"""
Enhanced bootstrap launcher with all real engine adapters
Swaps stub adapters with real implementations and runs the Voice Engine Router
"""

from __future__ import annotations
import uvicorn

from workers.ops.voice_engine_router import app, REGISTRY, CONFIG

# Import all real adapters
try:
    from services.adapters.engine_xtts import XTTSRealAdapter

    REGISTRY._adapters["xtts"] = XTTSRealAdapter()
    print("✅ Loaded real XTTS adapter")
except Exception as e:
    print(f"⚠️  Could not load XTTS adapter: {e}")

try:
    from services.adapters.engine_openvoice import OpenVoiceRealAdapter

    REGISTRY._adapters["openvoice"] = OpenVoiceRealAdapter()
    print("✅ Loaded real OpenVoice adapter")
except Exception as e:
    print(f"⚠️  Could not load OpenVoice adapter: {e}")

try:
    from services.adapters.engine_coqui import CoquiRealAdapter

    REGISTRY._adapters["coqui"] = CoquiRealAdapter()
    print("✅ Loaded real Coqui adapter")
except Exception as e:
    print(f"⚠️  Could not load Coqui adapter: {e}")

try:
    from services.adapters.engine_tortoise import TortoiseRealAdapter

    REGISTRY._adapters["tortoise"] = TortoiseRealAdapter()
    print("✅ Loaded real Tortoise adapter")
except Exception as e:
    print(f"⚠️  Could not load Tortoise adapter: {e}")

print(f"\n🚀 Starting VoiceStudio Router on {CONFIG.host}:{CONFIG.port}")
print("Available engines:", list(REGISTRY._adapters.keys()))

if __name__ == "__main__":
    uvicorn.run(app, host=CONFIG.host, port=CONFIG.port, log_level="info")
