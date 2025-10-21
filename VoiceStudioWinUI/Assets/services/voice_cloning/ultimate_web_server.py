#!/usr/bin/env python3
"""
VoiceStudio Ultimate Voice Cloning Web Server
Advanced web server for voice cloning services
Version: 3.0.0 "Ultimate Web Server"
"""

import asyncio
import logging
import json
import time
import uuid
from pathlib import Path
import argparse
from typing import Dict, List, Optional, Any
from datetime import datetime
import uvicorn
import socket
from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, File, Form
import traceback
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import websockets
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

# Import our voice cloning services
try:
    from ultimate_real_ai_integration import UltimateRealAIEngine, UltimateRealAIConfig
    from real_ai_model_integration import RealAIModelIntegration, RealModelConfig
    from coqui_tts_service import CoquiTTSService, CoquiConfig, coqui_manager
    from real_time_voice_cloning_system import VoiceStudioRealTimeEngine, RealTimeConfig
    from performance_optimizer_ultimate import (
        VoiceStudioPerformanceOptimizer,
        PerformanceConfig,
    )
    from ultimate_upgrade_system import VoiceStudioUpgradeSystem, UpgradeConfig

    SERVICES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some services not available: {e}")
    SERVICES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceStudioWebServer:
    """Ultimate web server for VoiceStudio voice cloning"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize FastAPI app
        self.app = FastAPI(
            title="VoiceStudio Ultimate Voice Cloning",
            version="3.0.0",
            description="Next-generation voice cloning with cutting-edge AI models",
            docs_url="/docs",
            redoc_url="/redoc",
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Initialize services
        self.ultimate_engine = None
        self.real_ai_integration = None
        self.real_time_engine = None
        self.performance_optimizer = None
        self.upgrade_system = None

        # WebSocket connections
        self.websocket_connections = []

        # Setup routes
        self.setup_routes()

        # Setup static files
        self.setup_static_files()

    def setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/")
        async def root():
            """Root endpoint - serve the main interface"""
            try:
                interface_path = Path(
                    "services/voice_cloning/ultimate_voice_cloning_interface.html"
                )
                if interface_path.exists():
                    return FileResponse(interface_path)
                else:
                    return HTMLResponse(
                        """
                    <html>
                        <head><title>VoiceStudio Ultimate</title></head>
                        <body>
                            <h1>VoiceStudio Ultimate Voice Cloning</h1>
                            <p>Voice cloning interface not found. Please check the installation.</p>
                            <p><a href="/docs">API Documentation</a></p>
                        </body>
                    </html>
                    """
                    )
            except Exception as e:
                self.logger.error(f"Failed to serve root: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/status")
        async def get_status():
            """Get system status"""
            try:
                # Get engine status if available
                engine_status = None
                if self.ultimate_engine:
                    engine_status = self.ultimate_engine.get_engine_status()

                return {
                    "status": "healthy",
                    "service": "VoiceStudio Ultimate Real AI Voice Cloning",
                    "version": "3.0.0",
                    "services_available": SERVICES_AVAILABLE,
                    "real_ai_available": SERVICES_AVAILABLE,
                    "timestamp": datetime.now().isoformat(),
                    "features": [
                        "Real AI Voice Cloning",
                        "GPT-SoVITS Integration",
                        "Coqui XTTS Integration",
                        "RVC Integration",
                        "OpenVoice Integration",
                        "Real-time Processing",
                        "Performance Optimization",
                        "Automatic Upgrades",
                        "Advanced UI/UX",
                    ],
                    "engine_status": engine_status,
                }
            except Exception as e:
                self.logger.error(f"Failed to get status: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/models")
        async def get_models():
            """Get available voice cloning models"""
            try:
                # Get available models from engine if available
                available_models = []
                if self.ultimate_engine:
                    available_models = (
                        self.ultimate_engine.ultimate_service.get_available_models()
                    )

                models = {
                    "gpt_sovits_2": {
                        "name": "GPT-SoVITS 2.0 Real AI",
                        "description": "Real GPT-SoVITS with quantum-level processing",
                        "version": "2.0.0",
                        "features": [
                            "Zero-shot",
                            "Ultra-high quality",
                            "Instant inference",
                            "Multi-language",
                            "Emotion control",
                        ],
                        "quality_score": 0.98,
                        "speed_score": 0.95,
                        "real_time": True,
                        "real_ai": True,
                        "available": "gpt_sovits" in available_models,
                    },
                    "rvc_4": {
                        "name": "RVC 4.0 Real AI",
                        "description": "Real RVC with advanced voice conversion",
                        "version": "4.0.0",
                        "features": [
                            "Real-time",
                            "Ultra-high quality",
                            "Voice conversion",
                            "Ultra-low latency",
                            "GPU acceleration",
                        ],
                        "quality_score": 0.97,
                        "speed_score": 0.98,
                        "real_time": True,
                        "real_ai": True,
                        "available": "rvc" in available_models,
                    },
                    "coqui_xtts_3": {
                        "name": "Coqui XTTS 3.0 Real AI",
                        "description": "Real Coqui XTTS with enhanced multilingual support",
                        "version": "3.0.0",
                        "features": [
                            "Real-time",
                            "Multi-language",
                            "Voice cloning",
                            "Emotion control",
                            "Cross-lingual",
                        ],
                        "quality_score": 0.96,
                        "speed_score": 0.97,
                        "real_time": True,
                        "real_ai": True,
                        "available": "coqui_xtts" in available_models,
                    },
                    "openvoice_2": {
                        "name": "OpenVoice 2.0 Real AI",
                        "description": "Real OpenVoice with enhanced emotion and accent control",
                        "version": "2.0.0",
                        "features": [
                            "Instant cloning",
                            "Emotion control",
                            "Accent control",
                            "Real-time",
                            "Multi-speaker",
                        ],
                        "quality_score": 0.95,
                        "speed_score": 0.99,
                        "real_time": True,
                        "real_ai": True,
                        "available": "openvoice" in available_models,
                    },
                }
                return models
            except Exception as e:
                self.logger.error(f"Failed to get models: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/clone/ultimate")
        async def clone_voice_ultimate(
            reference_audio: UploadFile = File(...),
            target_text: str = Form(...),
            selected_model_id: Optional[str] = Form(None),
            emotion: str = Form("neutral"),
            accent: str = Form("neutral"),
            quality_preset: str = Form("ultimate"),
            real_time: bool = Form(False),
            prosody_control: Optional[str] = Form(None),
        ):
            """Ultimate voice cloning endpoint"""
            try:
                if not SERVICES_AVAILABLE:
                    raise HTTPException(
                        status_code=503, detail="Voice cloning services not available"
                    )

                # Initialize ultimate real AI engine if not already done
                if self.ultimate_engine is None:
                    config = UltimateRealAIConfig()
                    self.ultimate_engine = UltimateRealAIEngine(config)
                    await self.ultimate_engine.start_engine()

                # Save uploaded audio
                audio_path = f"temp_{reference_audio.filename}"
                with open(audio_path, "wb") as f:
                    f.write(await reference_audio.read())

                # Parse prosody control
                prosody = json.loads(prosody_control) if prosody_control else None

                # Normalize model id from UI to engine IDs
                ui_to_engine_model = {
                    "gpt_sovits_2": "gpt_sovits",
                    "coqui_xtts_3": "coqui_xtts",
                    "rvc_4": "rvc",
                    "openvoice_2": "openvoice",
                }
                engine_model_id = None
                if selected_model_id:
                    engine_model_id = ui_to_engine_model.get(
                        selected_model_id, selected_model_id
                    )

                # Clone voice using real AI engine
                result = await self.ultimate_engine.clone_voice(
                    reference_audio=audio_path,
                    target_text=target_text,
                    model_id=engine_model_id,
                    emotion=emotion,
                    accent=accent,
                    prosody_control=prosody,
                    quality_preset=quality_preset,
                    real_time=real_time,
                    output_path=f"output_{uuid.uuid4().hex}.wav",
                )

                # Clean up temp file
                Path(audio_path).unlink()

                return result

            except Exception as e:
                tb = traceback.format_exc()
                self.logger.error(f"Ultimate voice cloning failed: {e}\n{tb}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "error": str(e), "traceback": tb},
                )

        @self.app.post("/api/clone/real-time/start")
        async def start_real_time_cloning():
            """Start real-time voice cloning"""
            try:
                if not SERVICES_AVAILABLE:
                    raise HTTPException(
                        status_code=503, detail="Real-time services not available"
                    )

                # Initialize real-time engine if not already done
                if self.real_time_engine is None:
                    config = RealTimeConfig()
                    self.real_time_engine = VoiceStudioRealTimeEngine(config)

                # Start real-time processing
                await self.real_time_engine.real_time_service.start_service()

                return {
                    "status": "started",
                    "message": "Real-time voice cloning started",
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                self.logger.error(f"Failed to start real-time cloning: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/clone/real-time/stop")
        async def stop_real_time_cloning():
            """Stop real-time voice cloning"""
            try:
                if self.real_time_engine is None:
                    raise HTTPException(
                        status_code=404, detail="Real-time engine not initialized"
                    )

                # Stop real-time processing
                self.real_time_engine.real_time_service.real_time_processor.stop_processing()

                return {
                    "status": "stopped",
                    "message": "Real-time voice cloning stopped",
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                self.logger.error(f"Failed to stop real-time cloning: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/clone/real-time/metrics")
        async def get_real_time_metrics():
            """Get real-time metrics"""
            try:
                if self.real_time_engine is None:
                    raise HTTPException(
                        status_code=404, detail="Real-time engine not initialized"
                    )

                metrics = (
                    self.real_time_engine.real_time_service.real_time_processor.get_metrics()
                )
                return metrics

            except Exception as e:
                self.logger.error(f"Failed to get real-time metrics: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/optimize/start")
        async def start_performance_optimization():
            """Start performance optimization"""
            try:
                if not SERVICES_AVAILABLE:
                    raise HTTPException(
                        status_code=503,
                        detail="Performance optimization services not available",
                    )

                # Initialize performance optimizer if not already done
                if self.performance_optimizer is None:
                    config = PerformanceConfig()
                    self.performance_optimizer = VoiceStudioPerformanceOptimizer(config)

                # Start optimization
                await self.performance_optimizer.start_optimization()

                return {
                    "status": "started",
                    "message": "Performance optimization started",
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                self.logger.error(f"Failed to start performance optimization: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/optimize/report")
        async def get_optimization_report():
            """Get optimization report"""
            try:
                if self.performance_optimizer is None:
                    raise HTTPException(
                        status_code=404, detail="Performance optimizer not initialized"
                    )

                report = self.performance_optimizer.get_optimization_report()
                return report

            except Exception as e:
                self.logger.error(f"Failed to get optimization report: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/upgrade/start")
        async def start_system_upgrade():
            """Start system upgrade"""
            try:
                if not SERVICES_AVAILABLE:
                    raise HTTPException(
                        status_code=503, detail="Upgrade services not available"
                    )

                # Initialize upgrade system if not already done
                if self.upgrade_system is None:
                    config = UpgradeConfig()
                    self.upgrade_system = VoiceStudioUpgradeSystem(config)

                # Start comprehensive upgrade
                await self.upgrade_system.start_comprehensive_upgrade()

                return {
                    "status": "completed",
                    "message": "System upgrade completed",
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                self.logger.error(f"Failed to start system upgrade: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/upgrade/report")
        async def get_upgrade_report():
            """Get upgrade report"""
            try:
                if self.upgrade_system is None:
                    raise HTTPException(
                        status_code=404, detail="Upgrade system not initialized"
                    )

                report = self.upgrade_system.get_upgrade_report()
                return report

            except Exception as e:
                self.logger.error(f"Failed to get upgrade report: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            try:
                await websocket.accept()
                self.websocket_connections.append(websocket)

                # Send welcome message
                await websocket.send_json(
                    {
                        "type": "welcome",
                        "message": "Connected to VoiceStudio Ultimate",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                # Keep connection alive and handle messages
                while True:
                    try:
                        data = await websocket.receive_text()
                        message = json.loads(data)

                        # Handle different message types
                        if message.get("type") == "ping":
                            await websocket.send_json(
                                {
                                    "type": "pong",
                                    "timestamp": datetime.now().isoformat(),
                                }
                            )
                        elif message.get("type") == "get_status":
                            status = {
                                "type": "status",
                                "services_available": SERVICES_AVAILABLE,
                                "ultimate_engine_active": self.ultimate_engine
                                is not None,
                                "real_time_engine_active": self.real_time_engine
                                is not None,
                                "performance_optimizer_active": self.performance_optimizer
                                is not None,
                                "upgrade_system_active": self.upgrade_system
                                is not None,
                                "timestamp": datetime.now().isoformat(),
                            }
                            await websocket.send_json(status)

                    except websockets.exceptions.ConnectionClosed:
                        break
                    except Exception as e:
                        self.logger.error(f"WebSocket error: {e}")
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": str(e),
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

            except Exception as e:
                self.logger.error(f"WebSocket connection failed: {e}")
            finally:
                if websocket in self.websocket_connections:
                    self.websocket_connections.remove(websocket)

    def setup_static_files(self):
        """Setup static file serving"""
        try:
            # Mount static files directory
            static_path = Path("services/voice_cloning")
            if static_path.exists():
                self.app.mount(
                    "/static", StaticFiles(directory=str(static_path)), name="static"
                )

        except Exception as e:
            self.logger.error(f"Failed to setup static files: {e}")

    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all WebSocket connections"""
        try:
            if not self.websocket_connections:
                return

            message_str = json.dumps(message)
            disconnected = []

            for websocket in self.websocket_connections:
                try:
                    await websocket.send_text(message_str)
                except Exception as e:
                    self.logger.error(f"Failed to send message to WebSocket: {e}")
                    disconnected.append(websocket)

            # Remove disconnected connections
            for websocket in disconnected:
                if websocket in self.websocket_connections:
                    self.websocket_connections.remove(websocket)

        except Exception as e:
            self.logger.error(f"Failed to broadcast message: {e}")

    async def start_server(self, host: str = "127.0.0.1", port: int = 8080):
        """Start the web server"""
        try:
            self.logger.info(
                f"Starting VoiceStudio Ultimate Web Server on {host}:{port}"
            )

            # Single-instance/port-in-use guard: fail fast if the port is taken
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                port_in_use = sock.connect_ex((host, port)) == 0
            if port_in_use:
                self.logger.error(
                    f"Port {host}:{port} is already in use. Another instance may be running. Exiting."
                )
                return

            # Start server
            config = uvicorn.Config(
                self.app, host=host, port=port, log_level="info", access_log=True
            )
            server = uvicorn.Server(config)

            self.logger.info("VoiceStudio Ultimate Web Server started successfully")
            await server.serve()

        except Exception as e:
            self.logger.error(f"Failed to start web server: {e}")
            raise


# Example usage
async def main():
    """Example usage of the VoiceStudio web server"""

    # CLI args
    parser = argparse.ArgumentParser(description="VoiceStudio Ultimate Web Server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8083)
    args = parser.parse_args()

    # Initialize web server
    web_server = VoiceStudioWebServer()

    # Start server
    await web_server.start_server(host=args.host, port=args.port)

    print("VoiceStudio Ultimate Web Server test completed!")


if __name__ == "__main__":
    asyncio.run(main())
