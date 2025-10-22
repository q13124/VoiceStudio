# examples/realtime_conversion_client.py
# Example client for real-time voice conversion

import asyncio
import json
import websockets
import numpy as np
import sounddevice as sd
import soundfile as sf

class RealtimeConversionClient:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.websocket = None
        self.is_connected = False
        
    async def connect(self):
        """Connect to the server"""
        try:
            self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}")
            self.is_connected = True
            print(f"Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the server"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            print("Disconnected")
    
    async def start_conversion(self, reference_path):
        """Start voice conversion"""
        if not self.is_connected:
            print("Not connected to server")
            return False
        
        message = {
            "type": "start_conversion",
            "reference_path": reference_path
        }
        
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        result = json.loads(response)
        
        if result.get("status") == "started":
            print("Voice conversion started")
            return True
        else:
            print(f"Failed to start conversion: {result.get('message')}")
            return False
    
    async def stop_conversion(self):
        """Stop voice conversion"""
        if not self.is_connected:
            return False
        
        message = {"type": "stop_conversion"}
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        result = json.loads(response)
        
        if result.get("status") == "stopped":
            print("Voice conversion stopped")
            return True
        else:
            print(f"Failed to stop conversion: {result.get('message')}")
            return False
    
    async def send_audio_chunk(self, audio_data):
        """Send audio chunk for processing"""
        if not self.is_connected:
            return None
        
        message = {
            "type": "audio_chunk",
            "audio_data": audio_data.tolist()
        }
        
        await self.websocket.send(json.dumps(message))
        
        # Wait for processed chunk
        response = await self.websocket.recv()
        result = json.loads(response)
        
        if result.get("type") == "processed_chunk":
            return np.array(result.get("audio_data"))
        else:
            return None
    
    async def get_stats(self):
        """Get performance statistics"""
        if not self.is_connected:
            return None
        
        message = {"type": "get_stats"}
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        result = json.loads(response)
        
        if result.get("type") == "stats":
            return result.get("data")
        else:
            return None

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VoiceStudio Real-Time Conversion Client")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    parser.add_argument("--reference", required=True, help="Path to reference voice file")
    
    args = parser.parse_args()
    
    client = RealtimeConversionClient(args.host, args.port)
    
    try:
        # Connect to server
        if not await client.connect():
            return
        
        # Start conversion
        if not await client.start_conversion(args.reference):
            return
        
        print("Real-time voice conversion active. Press Ctrl+C to stop.")
        
        # Monitor stats
        while True:
            await asyncio.sleep(5)
            stats = await client.get_stats()
            if stats:
                print(f"Stats: {stats}")
            
    except KeyboardInterrupt:
        print("\nStopping conversion...")
        await client.stop_conversion()
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
