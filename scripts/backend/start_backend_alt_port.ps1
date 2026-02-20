# Start backend on alternative port (8001)
# This script starts on 8001 when 8000 is occupied
cd E:\VoiceStudio
$env:PYTHONPATH = "E:\VoiceStudio"
uvicorn backend.api.main:app --reload --port 8001 --host 0.0.0.0

