# VoiceStudio Ultimate Setup & Test Guide
# Complete setup for VoiceStudio with real XTTS v2 integration

# 0) Activate your Python 3.10 venv first
# python -m venv venv
# venv\Scripts\activate

# 1) Ensure deps (pinned stack)
pip install TTS==0.24.1 torch==2.2.2+cu121 torchaudio==2.2.2+cu121 -f https://download.pytorch.org/whl/torch_stable.html
pip install soundfile fastapi uvicorn pydantic==1.* pytest

# 2) Optional: tweak config/voicestudio.yaml (model path, speaker refs)

# 3) Start router with real XTTS
python -m services.run_router_with_xtts

# 4) Quick health check (new terminal)
curl http://127.0.0.1:5090/health

# 5) Smoke test sync TTS (returns base64 WAV)
curl -X POST http://127.0.0.1:5090/tts -H "content-type: application/json" `
  -d '{ "text":"Hello VoiceStudio", "language":"en", "quality":"balanced", "mode":"sync" }'

# 6) Tests
pytest -q

# Additional Testing Commands:
# Test multilingual support
curl -X POST http://127.0.0.1:5090/tts -H "content-type: application/json" `
  -d '{ "text":"Hola mundo", "language":"es", "quality":"balanced", "mode":"sync" }'

# Test A/B testing
curl -X POST http://127.0.0.1:5090/abtest -H "content-type: application/json" `
  -d '{ "text":"A/B test", "language":"en", "quality":"balanced" }'

# Test async mode
curl -X POST http://127.0.0.1:5090/tts -H "content-type: application/json" `
  -d '{ "text":"Async test", "language":"en", "quality":"balanced", "mode":"async" }'

# Test with voice profile
curl -X POST http://127.0.0.1:5090/tts -H "content-type: application/json" `
  -d '{ "text":"Voice profile test", "language":"en", "quality":"balanced", "voice_profile":{"voice_id":"test"}, "mode":"sync" }'
