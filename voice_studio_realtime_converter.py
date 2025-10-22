#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Real-Time Voice Conversion System
Low-latency voice conversion with streaming audio processing
"""

import os
import json
import time
import threading
import queue
import numpy as np
import librosa
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
import asyncio
import websockets
from concurrent.futures import ThreadPoolExecutor
import logging

class RealtimeVoiceConverter:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/voicestudio.config.json"
        self.config = self.load_config()
        
        # Audio settings
        self.sample_rate = self.config.get("audio", {}).get("sample_rate", 22050)
        self.chunk_size = self.config.get("audio", {}).get("chunk_size", 512)
        self.channels = self.config.get("audio", {}).get("channels", 1)
        
        # Performance settings
        self.max_latency_ms = self.config.get("performance", {}).get("max_latency_ms", 50)
        self.buffer_size = self.config.get("performance", {}).get("buffer_size", 1024)
        
        # Voice conversion settings
        self.reference_audio = None
        self.reference_features = None
        self.target_voice = None
        
        # Audio buffers
        self.input_buffer = queue.Queue(maxsize=10)
        self.output_buffer = queue.Queue(maxsize=10)
        self.processing_buffer = np.zeros(self.buffer_size, dtype=np.float32)
        
        # Threading
        self.is_running = False
        self.audio_thread = None
        self.processing_thread = None
        self.output_thread = None
        
        # Performance monitoring
        self.latency_stats = []
        self.processing_stats = []
        
        # Engine settings
        self.engine = self.config.get("voice_conversion", {}).get("engine", "xtts")
        self.quality = self.config.get("voice_conversion", {}).get("quality", "high")
        
        # Setup logging
        self.setup_logging()
        
    def load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "audio": {
                "sample_rate": 22050,
                "chunk_size": 512,
                "channels": 1,
                "format": "float32"
            },
            "performance": {
                "max_latency_ms": 50,
                "buffer_size": 1024,
                "max_workers": 4
            },
            "voice_conversion": {
                "engine": "xtts",
                "quality": "high",
                "latency_mode": "ultra"
            }
        }
    
    def setup_logging(self):
        """Setup logging for real-time conversion"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_reference_voice(self, reference_path: str) -> bool:
        """Load reference voice for conversion"""
        try:
            # Load reference audio
            self.reference_audio, sr = librosa.load(reference_path, sr=self.sample_rate)
            
            # Extract voice features
            self.reference_features = self.extract_voice_features(self.reference_audio, sr)
            
            self.logger.info(f"Reference voice loaded: {reference_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load reference voice: {e}")
            return False
    
    def extract_voice_features(self, audio: np.ndarray, sr: int) -> Dict:
        """Extract voice characteristics for conversion"""
        features = {}
        
        # Spectral features
        features['mfcc'] = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        features['spectral_centroid'] = librosa.feature.spectral_centroid(y=audio, sr=sr)
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(y=audio, sr=sr)
        features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(audio)
        
        # Prosodic features
        features['rms'] = librosa.feature.rms(y=audio)
        features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(y=audio, sr=sr)
        
        # Pitch features
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        features['pitch'] = pitches
        features['pitch_magnitude'] = magnitudes
        
        return features
    
    def convert_voice_chunk(self, audio_chunk: np.ndarray) -> np.ndarray:
        """Convert voice chunk using real-time processing"""
        try:
            # Apply voice conversion algorithm
            # This is a simplified implementation
            # In practice, you would use the actual voice cloning engine
            
            # Extract features from input chunk
            input_features = self.extract_voice_features(audio_chunk, self.sample_rate)
            
            # Apply voice conversion
            converted_chunk = self.apply_voice_conversion(audio_chunk, input_features)
            
            return converted_chunk
            
        except Exception as e:
            self.logger.error(f"Voice conversion failed: {e}")
            return audio_chunk  # Return original if conversion fails
    
    def apply_voice_conversion(self, audio_chunk: np.ndarray, input_features: Dict) -> np.ndarray:
        """Apply voice conversion to audio chunk"""
        # Simplified voice conversion implementation
        # In practice, this would use the actual voice cloning engine
        
        # Apply spectral transformation
        converted_chunk = audio_chunk.copy()
        
        # Apply pitch shifting based on reference
        if self.reference_features and 'pitch' in self.reference_features:
            # Calculate pitch shift ratio
            ref_pitch = np.mean(self.reference_features['pitch'][self.reference_features['pitch'] > 0])
            input_pitch = np.mean(input_features['pitch'][input_features['pitch'] > 0])
            
            if ref_pitch > 0 and input_pitch > 0:
                pitch_ratio = ref_pitch / input_pitch
                # Apply pitch shifting (simplified)
                converted_chunk = librosa.effects.pitch_shift(converted_chunk, sr=self.sample_rate, n_steps=np.log2(pitch_ratio) * 12)
        
        # Apply spectral envelope transformation
        if self.reference_features and 'mfcc' in self.reference_features:
            # Transform MFCC features
            ref_mfcc = np.mean(self.reference_features['mfcc'], axis=1)
            input_mfcc = np.mean(input_features['mfcc'], axis=1)
            
            # Apply MFCC transformation
            mfcc_transform = ref_mfcc - input_mfcc
            # Apply transformation to audio (simplified)
            converted_chunk = converted_chunk * (1 + np.mean(mfcc_transform) * 0.1)
        
        return converted_chunk
    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Audio callback for real-time processing"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        # Put input data in buffer
        if not self.input_buffer.full():
            self.input_buffer.put(indata.copy())
        
        # Get output data from buffer
        if not self.output_buffer.empty():
            outdata[:] = self.output_buffer.get()
        else:
            outdata[:] = indata  # Pass through if no processed data
    
    def processing_worker(self):
        """Worker thread for audio processing"""
        while self.is_running:
            try:
                # Get input chunk
                if not self.input_buffer.empty():
                    input_chunk = self.input_buffer.get(timeout=0.1)
                    
                    # Process chunk
                    start_time = time.time()
                    processed_chunk = self.convert_voice_chunk(input_chunk.flatten())
                    processing_time = (time.time() - start_time) * 1000
                    
                    # Record processing time
                    self.processing_stats.append(processing_time)
                    
                    # Put processed chunk in output buffer
                    if not self.output_buffer.full():
                        self.output_buffer.put(processed_chunk.reshape(-1, 1))
                    
                    # Check latency
                    if processing_time > self.max_latency_ms:
                        self.logger.warning(f"High processing latency: {processing_time:.2f}ms")
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Processing worker error: {e}")
    
    def start_conversion(self, input_device: int = None, output_device: int = None):
        """Start real-time voice conversion"""
        try:
            self.is_running = True
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self.processing_worker)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            # Start audio stream
            self.audio_stream = sd.Stream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                blocksize=self.chunk_size,
                callback=self.audio_callback,
                input_device=input_device,
                output_device=output_device
            )
            
            self.audio_stream.start()
            self.logger.info("Real-time voice conversion started")
            
        except Exception as e:
            self.logger.error(f"Failed to start conversion: {e}")
            self.stop_conversion()
    
    def stop_conversion(self):
        """Stop real-time voice conversion"""
        try:
            self.is_running = False
            
            # Stop audio stream
            if hasattr(self, 'audio_stream'):
                self.audio_stream.stop()
                self.audio_stream.close()
            
            # Wait for processing thread
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=1.0)
            
            self.logger.info("Real-time voice conversion stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping conversion: {e}")
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        stats = {
            "is_running": self.is_running,
            "input_buffer_size": self.input_buffer.qsize(),
            "output_buffer_size": self.output_buffer.qsize(),
            "avg_processing_time_ms": np.mean(self.processing_stats) if self.processing_stats else 0,
            "max_processing_time_ms": np.max(self.processing_stats) if self.processing_stats else 0,
            "min_processing_time_ms": np.min(self.processing_stats) if self.processing_stats else 0,
            "total_chunks_processed": len(self.processing_stats)
        }
        
        return stats
    
    def optimize_for_latency(self):
        """Optimize settings for ultra-low latency"""
        # Reduce buffer sizes
        self.chunk_size = min(self.chunk_size, 256)
        self.buffer_size = min(self.buffer_size, 512)
        
        # Update audio settings
        self.config["audio"]["chunk_size"] = self.chunk_size
        self.config["audio"]["buffer_size"] = self.buffer_size
        
        self.logger.info("Optimized for ultra-low latency")

class RealtimeVoiceConversionServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.converter = RealtimeVoiceConverter()
        self.clients = set()
        
    async def register_client(self, websocket, path):
        """Register new client"""
        self.clients.add(websocket)
        self.converter.logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            self.converter.logger.info(f"Client disconnected: {websocket.remote_address}")
    
    async def handle_message(self, websocket, message):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "start_conversion":
                # Start voice conversion
                reference_path = data.get("reference_path")
                if reference_path and self.converter.load_reference_voice(reference_path):
                    self.converter.start_conversion()
                    await websocket.send(json.dumps({"status": "started"}))
                else:
                    await websocket.send(json.dumps({"status": "error", "message": "Failed to load reference voice"}))
            
            elif message_type == "stop_conversion":
                # Stop voice conversion
                self.converter.stop_conversion()
                await websocket.send(json.dumps({"status": "stopped"}))
            
            elif message_type == "get_stats":
                # Get performance stats
                stats = self.converter.get_performance_stats()
                await websocket.send(json.dumps({"type": "stats", "data": stats}))
            
            elif message_type == "audio_chunk":
                # Process audio chunk
                audio_data = np.array(data.get("audio_data"))
                processed_chunk = self.converter.convert_voice_chunk(audio_data)
                
                # Send processed chunk back
                await websocket.send(json.dumps({
                    "type": "processed_chunk",
                    "audio_data": processed_chunk.tolist()
                }))
            
        except Exception as e:
            await websocket.send(json.dumps({"status": "error", "message": str(e)}))
    
    async def start_server(self):
        """Start WebSocket server"""
        self.converter.logger.info(f"Starting real-time voice conversion server on {self.host}:{self.port}")
        
        async with websockets.serve(self.register_client, self.host, self.port):
            await asyncio.Future()  # Run forever

def main():
    """Main function for testing real-time voice conversion"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VoiceStudio Real-Time Voice Conversion")
    parser.add_argument("--mode", choices=["local", "server"], default="local",
                       help="Run mode: local or server")
    parser.add_argument("--reference", required=True,
                       help="Path to reference voice file")
    parser.add_argument("--host", default="localhost",
                       help="Server host (server mode)")
    parser.add_argument("--port", type=int, default=8765,
                       help="Server port (server mode)")
    
    args = parser.parse_args()
    
    if args.mode == "local":
        # Local mode - direct audio processing
        converter = RealtimeVoiceConverter()
        
        if converter.load_reference_voice(args.reference):
            print("Reference voice loaded. Starting real-time conversion...")
            print("Press Ctrl+C to stop")
            
            try:
                converter.start_conversion()
                
                # Monitor performance
                while True:
                    time.sleep(5)
                    stats = converter.get_performance_stats()
                    print(f"Stats: {stats}")
                    
            except KeyboardInterrupt:
                print("Stopping conversion...")
                converter.stop_conversion()
        else:
            print("Failed to load reference voice")
    
    elif args.mode == "server":
        # Server mode - WebSocket server
        server = RealtimeVoiceConversionServer(args.host, args.port)
        
        print(f"Starting server on {args.host}:{args.port}")
        print("Press Ctrl+C to stop")
        
        try:
            asyncio.run(server.start_server())
        except KeyboardInterrupt:
            print("Stopping server...")

if __name__ == "__main__":
    main()
