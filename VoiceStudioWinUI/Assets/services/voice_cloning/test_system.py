#!/usr/bin/env python3
"""
VoiceStudio Voice Cloning System Tests
Comprehensive testing and validation for the voice cloning system.
"""

import asyncio
import logging
import pytest
import requests
import json
import time
import os
import tempfile
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, Any, List
import websockets
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceCloningSystemTester:
    """Comprehensive tester for the voice cloning system"""
    
    def __init__(self, base_url: str = "http://localhost:5083", web_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.web_url = web_url
        self.test_results = {}
        self.test_audio_files = []
        
    def create_test_audio(self, duration: float = 2.0, sample_rate: int = 22050) -> str:
        """Create a test audio file"""
        # Generate a simple sine wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440  # A4 note
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Add some variation to make it more realistic
        audio += 0.1 * np.sin(2 * np.pi * frequency * 2 * t)  # Harmonic
        audio += 0.05 * np.random.normal(0, 1, len(audio))  # Noise
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(temp_file.name, audio, sample_rate)
        self.test_audio_files.append(temp_file.name)
        
        return temp_file.name
    
    def cleanup_test_files(self):
        """Clean up test audio files"""
        for file_path in self.test_audio_files:
            try:
                os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    async def test_service_health(self) -> bool:
        """Test if voice cloning service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Service health check passed: {data}")
                return True
            else:
                logger.error(f"Service health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Service health check error: {e}")
            return False
    
    async def test_voice_profile_extraction(self) -> bool:
        """Test voice profile extraction"""
        try:
            logger.info("Testing voice profile extraction...")
            
            # Create test audio
            audio_file = self.create_test_audio()
            
            # Test profile extraction
            with open(audio_file, 'rb') as f:
                files = {'audio_file': f}
                response = requests.post(f"{self.base_url}/extract-voice-profile", files=files, timeout=30)
            
            if response.status_code == 200:
                profile = response.json()
                logger.info(f"Voice profile extraction successful: {profile}")
                
                # Validate profile structure
                required_fields = ['speaker_embedding', 'pitch_contour', 'formant_frequencies', 
                                 'speaking_rate', 'breathing_patterns', 'emotion_patterns']
                
                for field in required_fields:
                    if field not in profile:
                        logger.error(f"Missing required field in profile: {field}")
                        return False
                
                logger.info("Voice profile extraction test passed")
                return True
            else:
                logger.error(f"Voice profile extraction failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Voice profile extraction test error: {e}")
            return False
    
    async def test_voice_cloning(self) -> bool:
        """Test voice cloning functionality"""
        try:
            logger.info("Testing voice cloning...")
            
            # Create test audio
            audio_file = self.create_test_audio()
            target_text = "Hello, this is a test of the voice cloning system."
            
            # Test voice cloning
            with open(audio_file, 'rb') as f:
                files = {'reference_audio': f}
                data = {
                    'target_text': target_text,
                    'speaker_id': 'test_speaker_001',
                    'model_type': 'gpt_sovits'
                }
                response = requests.post(f"{self.base_url}/clone-voice", files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Voice cloning successful: {result}")
                
                # Validate result structure
                required_fields = ['cloned_audio', 'voice_profile', 'processing_time', 'model_type']
                
                for field in required_fields:
                    if field not in result:
                        logger.error(f"Missing required field in result: {field}")
                        return False
                
                # Check if cloned audio file exists
                cloned_audio_path = result.get('cloned_audio')
                if cloned_audio_path and os.path.exists(cloned_audio_path):
                    logger.info(f"Cloned audio file exists: {cloned_audio_path}")
                else:
                    logger.warning("Cloned audio file not found or path not provided")
                
                logger.info("Voice cloning test passed")
                return True
            else:
                logger.error(f"Voice cloning failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Voice cloning test error: {e}")
            return False
    
    async def test_batch_cloning(self) -> bool:
        """Test batch voice cloning"""
        try:
            logger.info("Testing batch voice cloning...")
            
            # Create multiple test audio files
            audio_files = []
            target_texts = []
            
            for i in range(3):
                audio_file = self.create_test_audio()
                audio_files.append(('reference_audios', open(audio_file, 'rb')))
                target_texts.append(f"Batch test message {i+1}")
            
            # Test batch cloning
            data = {
                'target_texts': target_texts,
                'speaker_ids': ['test_speaker_001', 'test_speaker_002', 'test_speaker_003'],
                'model_type': 'gpt_sovits'
            }
            
            response = requests.post(f"{self.base_url}/clone-voice-batch", files=audio_files, data=data, timeout=120)
            
            # Close file handles
            for _, file_handle in audio_files:
                file_handle.close()
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Batch voice cloning successful: {result}")
                
                # Validate batch result structure
                if 'batch_results' not in result:
                    logger.error("Missing batch_results in response")
                    return False
                
                batch_results = result['batch_results']
                if len(batch_results) != 3:
                    logger.error(f"Expected 3 batch results, got {len(batch_results)}")
                    return False
                
                logger.info("Batch voice cloning test passed")
                return True
            else:
                logger.error(f"Batch voice cloning failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Batch voice cloning test error: {e}")
            return False
    
    async def test_unlimited_audio_processing(self) -> bool:
        """Test unlimited audio length processing"""
        try:
            logger.info("Testing unlimited audio processing...")
            
            # Create longer test audio
            audio_file = self.create_test_audio(duration=5.0)
            target_text = "This is a longer test message for unlimited audio processing."
            
            # Test unlimited processing
            with open(audio_file, 'rb') as f:
                files = {'reference_audio': f}
                data = {
                    'target_text': target_text,
                    'speaker_id': 'test_speaker_unlimited',
                    'processing_mode': 'chunked'
                }
                response = requests.post(f"{self.base_url}/clone-voice-unlimited", files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Unlimited audio processing initiated: {result}")
                
                # Check if session was created
                if 'session_id' not in result:
                    logger.error("Missing session_id in response")
                    return False
                
                session_id = result['session_id']
                
                # Wait for processing to complete (with timeout)
                max_wait_time = 120  # 2 minutes
                wait_time = 0
                
                while wait_time < max_wait_time:
                    await asyncio.sleep(5)
                    wait_time += 5
                    
                    # Check session status
                    status_response = requests.get(f"{self.base_url}/sessions/{session_id}", timeout=5)
                    if status_response.status_code == 200:
                        status = status_response.json()
                        logger.info(f"Session status: {status['status']}")
                        
                        if status['status'] == 'completed':
                            logger.info("Unlimited audio processing test passed")
                            return True
                        elif status['status'] == 'failed':
                            logger.error(f"Unlimited audio processing failed: {status.get('error', 'Unknown error')}")
                            return False
                
                logger.warning("Unlimited audio processing timed out")
                return False
            else:
                logger.error(f"Unlimited audio processing failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Unlimited audio processing test error: {e}")
            return False
    
    async def test_websocket_connection(self) -> bool:
        """Test WebSocket connection"""
        try:
            logger.info("Testing WebSocket connection...")
            
            uri = f"ws://localhost:5083/ws"
            
            async with websockets.connect(uri) as websocket:
                # Wait for initial message
                message = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(message)
                
                logger.info(f"WebSocket message received: {data}")
                
                # Validate message structure
                if 'active_sessions' not in data or 'timestamp' not in data:
                    logger.error("Invalid WebSocket message structure")
                    return False
                
                logger.info("WebSocket connection test passed")
                return True
                
        except Exception as e:
            logger.error(f"WebSocket connection test error: {e}")
            return False
    
    async def test_web_interface(self) -> bool:
        """Test web interface availability"""
        try:
            logger.info("Testing web interface...")
            
            response = requests.get(f"{self.web_url}/", timeout=5)
            if response.status_code == 200:
                content = response.text
                if "VoiceStudio" in content and "Voice Cloning" in content:
                    logger.info("Web interface test passed")
                    return True
                else:
                    logger.error("Web interface content validation failed")
                    return False
            else:
                logger.error(f"Web interface test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Web interface test error: {e}")
            return False
    
    async def test_performance_metrics(self) -> bool:
        """Test performance metrics endpoint"""
        try:
            logger.info("Testing performance metrics...")
            
            response = requests.get(f"{self.base_url}/metrics", timeout=5)
            if response.status_code == 200:
                metrics = response.json()
                logger.info(f"Performance metrics retrieved: {metrics}")
                
                # Validate metrics structure
                required_sections = ['files_processed', 'cache_hits', 'cache_misses', 'voice_cloning']
                
                for section in required_sections:
                    if section not in metrics:
                        logger.error(f"Missing required metrics section: {section}")
                        return False
                
                logger.info("Performance metrics test passed")
                return True
            else:
                logger.error(f"Performance metrics test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Performance metrics test error: {e}")
            return False
    
    async def test_model_availability(self) -> bool:
        """Test model availability endpoint"""
        try:
            logger.info("Testing model availability...")
            
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                logger.info(f"Model availability: {models}")
                
                # Validate models structure
                if 'available_models' not in models:
                    logger.error("Missing available_models in response")
                    return False
                
                expected_models = ['gpt_sovits', 'openvoice', 'coqui_xtts', 'tortoise_tts', 'rvc']
                available_models = models['available_models']
                
                for model in expected_models:
                    if model not in available_models:
                        logger.warning(f"Expected model {model} not available")
                
                logger.info("Model availability test passed")
                return True
            else:
                logger.error(f"Model availability test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Model availability test error: {e}")
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        logger.info("Starting comprehensive voice cloning system tests...")
        
        tests = [
            ("Service Health", self.test_service_health),
            ("Voice Profile Extraction", self.test_voice_profile_extraction),
            ("Voice Cloning", self.test_voice_cloning),
            ("Batch Cloning", self.test_batch_cloning),
            ("Unlimited Audio Processing", self.test_unlimited_audio_processing),
            ("WebSocket Connection", self.test_websocket_connection),
            ("Web Interface", self.test_web_interface),
            ("Performance Metrics", self.test_performance_metrics),
            ("Model Availability", self.test_model_availability)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                logger.info(f"Running test: {test_name}")
                result = await test_func()
                results[test_name] = result
                
                if result:
                    logger.info(f"✅ {test_name} PASSED")
                else:
                    logger.error(f"❌ {test_name} FAILED")
                    
            except Exception as e:
                logger.error(f"❌ {test_name} ERROR: {e}")
                results[test_name] = False
        
        # Cleanup test files
        self.cleanup_test_files()
        
        # Print summary
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"TEST SUMMARY: {passed}/{total} tests passed")
        logger.info(f"{'='*50}")
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
        
        return results

async def main():
    """Main test function"""
    tester = VoiceCloningSystemTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Exit with error code if any tests failed
        if not all(results.values()):
            logger.error("Some tests failed!")
            exit(1)
        else:
            logger.info("All tests passed! 🎉")
            exit(0)
            
    except Exception as e:
        logger.error(f"Test suite error: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
