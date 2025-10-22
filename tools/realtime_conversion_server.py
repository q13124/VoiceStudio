# tools/realtime_conversion_server.py
# WebSocket server for real-time voice conversion

import asyncio
import json
import logging
import websockets
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_realtime_converter import RealtimeVoiceConversionServer

class VoiceStudioRealtimeServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.server = RealtimeVoiceConversionServer(host, port)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start the WebSocket server"""
        self.logger.info(f"Starting VoiceStudio Real-Time Conversion Server on {self.host}:{self.port}")
        
        async with websockets.serve(self.server.register_client, self.host, self.port):
            self.logger.info("Server started. Waiting for connections...")
            await asyncio.Future()  # Run forever
    
    def stop(self):
        """Stop the server"""
        self.logger.info("Stopping server...")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VoiceStudio Real-Time Conversion Server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    
    args = parser.parse_args()
    
    server = VoiceStudioRealtimeServer(args.host, args.port)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()

if __name__ == "__main__":
    main()
