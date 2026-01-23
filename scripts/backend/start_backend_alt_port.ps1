# Start backend on alternative port (8001)
cd E:\VoiceStudio
$env:PYTHONPATH = "E:\VoiceStudio"
uvicorn backend.api.main:app --reload --port 8001 --host 0.0.0.0

