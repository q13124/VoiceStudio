$env:COQUI_TOS_AGREED = '1'
cd e:\VoiceStudio
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8001
