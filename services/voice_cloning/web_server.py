#!/usr/bin/env python3
"""
VoiceStudio Voice Cloning Web Interface Server
Serves the web interface for voice cloning operations.
"""

import asyncio
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VoiceStudio Web Interface", version="1.0.0")

# Serve the web interface
@app.get("/", response_class=HTMLResponse)
async def serve_interface():
    """Serve the voice cloning web interface"""
    interface_path = Path(__file__).parent / "web_interface.html"
    
    if not interface_path.exists():
        return HTMLResponse("""
        <html>
            <head><title>VoiceStudio - Interface Not Found</title></head>
            <body>
                <h1>VoiceStudio Web Interface</h1>
                <p>The web interface file was not found. Please ensure web_interface.html exists.</p>
            </body>
        </html>
        """, status_code=404)
    
    with open(interface_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return HTMLResponse(content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "web_interface"}

async def start_web_interface_server(port: int = 8080):
    """Start the web interface server"""
    logger.info(f"Starting VoiceStudio web interface server on port {port}")
    
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_web_interface_server())
