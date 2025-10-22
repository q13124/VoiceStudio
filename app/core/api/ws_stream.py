"""
WebSocket streaming stub for real-time TTS chunks.
Mount under FastAPI: app.include_router(router, prefix="/v1")
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import AsyncGenerator

router = APIRouter()

async def fake_chunker(text: str, voice_id: str) -> AsyncGenerator[bytes, None]:
    """
    Placeholder: yields deterministic PCM-like bytes.
    Replace with real engine streaming and backpressure control.
    """
    # Simulate three chunks
    for i in range(3):
        yield f"CHUNK-{i}:{voice_id}".encode("utf-8")

@router.websocket("/stream/{voice_id}")
async def stream_tts(websocket: WebSocket, voice_id: str):
    await websocket.accept()
    try:
        # First message from client should be JSON with {"text": "..."} or plain text
        init = await websocket.receive_text()
        async for chunk in fake_chunker(init, voice_id):
            await websocket.send_bytes(chunk)
        await websocket.close(code=1000)
    except WebSocketDisconnect:
        # Client disconnected
        return
