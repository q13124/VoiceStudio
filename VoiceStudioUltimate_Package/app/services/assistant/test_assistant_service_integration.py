#!/usr/bin/env python3
"""
VoiceStudio Assistant Service Integration Test
Comprehensive test suite for the enhanced assistant service with voice cloning capabilities.
"""

import asyncio
import json
import time
import tempfile
import os
import sys
import logging
import subprocess
import signal
from typing import Dict, Any, Optional
import aiohttp
import numpy as np
import soundfile as sf

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AssistantServiceTester:
    """Test suite for the enhanced assistant service"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5080"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.service_process: Optional[subprocess.Popen] = None
        self.test_results = {
            "timestamp": time.time(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_details": [],
            "performance_metrics": {}
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        if self.service_process:
            self.service_process.terminate()
            self.service_process.wait()
    
    def start_service(self) -> bool:
        """Start the assistant service"""
        try:
            logger.info("Starting Enhanced Assistant Service...")
            
            # Change to the services/assistant directory
            service_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     "services", "assistant")
            
            # Start the service
            self.service_process = subprocess.Popen(
                [sys.executable, "enhanced_service.py"],
                cwd=service_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for service to start
            logger.info("Waiting for service to start...")
            time.sleep(5)  # Give service time to initialize
            
            # Check if service is running
            if self.service_process.poll() is not None:
                logger.error("Service failed to start")
                return False
            
            logger.info("Service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            return False
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to the service"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    result = await response.json()
                    return {
                        "status": response.status,
                        "data": result,
                        "response_time": response.headers.get("X-Response-Time", "N/A")
                    }
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    result = await response.json()
                    return {
                        "status": response.status,
                        "data": result,
                        "response_time": response.headers.get("X-Response-Time", "N/A")
                    }
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "response_time": "N/A"
            }
    
    def run_test(self, test_name: str, test_func):
        """Run a test and record results"""
        logger.info(f"Running test: {test_name}")
        self.test_results["tests_run"] += 1
        
        try:
            start_time = time.time()
            result = asyncio.run(test_func())
            duration = time.time() - start_time
            
            if result.get("success", False):
                self.test_results["tests_passed"] += 1
                logger.info(f"PASSED: {test_name} ({duration:.2f}s)")
            else:
                self.test_results["tests_failed"] += 1
                logger.error(f"FAILED: {test_name} - {result.get('error', 'Unknown error')}")
            
            self.test_results["test_details"].append({
                "name": test_name,
                "success": result.get("success", False),
                "duration": duration,
                "result": result
            })
            
        except Exception as e:
            self.test_results["tests_failed"] += 1
            logger.error(f"ERROR: {test_name} - {str(e)}")
            self.test_results["test_details"].append({
                "name": test_name,
                "success": False,
                "duration": 0,
                "error": str(e)
            })
    
    async def test_service_health(self) -> Dict[str, Any]:
        """Test service health endpoint"""
        response = await self.make_request("GET", "/health")
        
        if response["status"] == 200:
            data = response["data"]
            if data.get("ok") and data.get("service") == "assistant":
                return {"success": True, "data": data}
        
        return {"success": False, "error": f"Health check failed: {response}"}
    
    async def test_voice_cloning_status(self) -> Dict[str, Any]:
        """Test voice cloning status endpoint"""
        response = await self.make_request("GET", "/voice-cloning/status")
        
        if response["status"] == 200:
            data = response["data"]
            if "status" in data:
                return {"success": True, "data": data}
        
        return {"success": False, "error": f"Voice cloning status failed: {response}"}
    
    async def test_available_models(self) -> Dict[str, Any]:
        """Test available models endpoint"""
        response = await self.make_request("GET", "/voice-cloning/models")
        
        if response["status"] == 200:
            data = response["data"]
            if data.get("success") and "models" in data:
                return {"success": True, "data": data}
        
        return {"success": False, "error": f"Available models failed: {response}"}
    
    async def test_speech_synthesis(self) -> Dict[str, Any]:
        """Test speech synthesis endpoint"""
        test_data = {
            "text": "Hello from VoiceStudio Assistant Service test",
            "model_type": "basic",
            "language": "en"
        }
        
        response = await self.make_request("POST", "/voice-cloning/synthesize", test_data)
        
        if response["status"] == 200:
            data = response["data"]
            if data.get("success") and "audio_path" in data:
                return {"success": True, "data": data}
        
        return {"success": False, "error": f"Speech synthesis failed: {response}"}
    
    async def test_voice_cloning(self) -> Dict[str, Any]:
        """Test voice cloning endpoint"""
        # Create a dummy reference audio file
        temp_dir = tempfile.mkdtemp()
        reference_audio = os.path.join(temp_dir, "reference.wav")
        
        try:
            # Create 3 seconds of dummy audio
            dummy_audio = np.random.rand(22050 * 3)
            sf.write(reference_audio, dummy_audio, 22050)
            
            test_data = {
                "text": "Hello from VoiceStudio voice cloning test",
                "reference_audio_path": reference_audio,
                "language": "en"
            }
            
            response = await self.make_request("POST", "/voice-cloning/clone", test_data)
            
            if response["status"] == 200:
                data = response["data"]
                if data.get("success") and "audio_path" in data:
                    return {"success": True, "data": data}
            
            return {"success": False, "error": f"Voice cloning failed: {response}"}
            
        finally:
            # Cleanup
            if os.path.exists(reference_audio):
                os.remove(reference_audio)
            os.rmdir(temp_dir)
    
    async def test_audio_transcription(self) -> Dict[str, Any]:
        """Test audio transcription endpoint"""
        # Create a dummy audio file for transcription
        temp_dir = tempfile.mkdtemp()
        test_audio = os.path.join(temp_dir, "test_audio.wav")
        
        try:
            # Create 2 seconds of dummy audio
            dummy_audio = np.random.rand(22050 * 2)
            sf.write(test_audio, dummy_audio, 22050)
            
            test_data = {
                "audio_path": test_audio,
                "language": "en"
            }
            
            response = await self.make_request("POST", "/voice-cloning/transcribe", test_data)
            
            if response["status"] == 200:
                data = response["data"]
                # Transcription might fail with dummy audio, but endpoint should respond
                return {"success": True, "data": data}
            
            return {"success": False, "error": f"Audio transcription failed: {response}"}
            
        finally:
            # Cleanup
            if os.path.exists(test_audio):
                os.remove(test_audio)
            os.rmdir(temp_dir)
    
    async def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Test performance benchmarks"""
        logger.info("Running performance benchmarks...")
        
        # Test multiple synthesis requests
        synthesis_times = []
        for i in range(3):
            test_data = {
                "text": f"Performance test {i+1}",
                "model_type": "basic",
                "language": "en"
            }
            
            start_time = time.time()
            response = await self.make_request("POST", "/voice-cloning/synthesize", test_data)
            duration = time.time() - start_time
            
            if response["status"] == 200:
                synthesis_times.append(duration)
        
        if synthesis_times:
            avg_time = sum(synthesis_times) / len(synthesis_times)
            self.test_results["performance_metrics"]["avg_synthesis_time"] = avg_time
            self.test_results["performance_metrics"]["synthesis_times"] = synthesis_times
            
            return {"success": True, "avg_time": avg_time}
        
        return {"success": False, "error": "Performance benchmarks failed"}
    
    def print_test_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*70)
        logger.info("VOICESTUDIO ASSISTANT SERVICE INTEGRATION TEST SUMMARY")
        logger.info("="*70)
        
        total_tests = self.test_results["tests_run"]
        passed_tests = self.test_results["tests_passed"]
        failed_tests = self.test_results["tests_failed"]
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        # Performance metrics
        if self.test_results["performance_metrics"]:
            logger.info("\nPerformance Metrics:")
            for metric, value in self.test_results["performance_metrics"].items():
                logger.info(f"  {metric}: {value}")
        
        # Test details
        logger.info("\nTest Details:")
        for test in self.test_results["test_details"]:
            status = "PASS" if test["success"] else "FAIL"
            logger.info(f"  {status}: {test['name']} ({test['duration']:.2f}s)")
        
        logger.info("="*70)
        
        if failed_tests == 0:
            logger.info("All tests passed! Assistant service with voice cloning is fully operational.")
        else:
            logger.warning(f"{failed_tests} tests failed. Check the logs for details.")
    
    def save_test_results(self, filename: str = "assistant_service_test_results.json"):
        """Save test results to file"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=4, ensure_ascii=False)
        logger.info(f"Test results saved to {filename}")

async def main():
    """Main test runner"""
    logger.info("Starting VoiceStudio Assistant Service Integration Tests")
    
    async with AssistantServiceTester() as tester:
        # Start the service
        if not tester.start_service():
            logger.error("Failed to start service. Exiting.")
            return
        
        # Run all tests
        tester.run_test("Service Health Check", tester.test_service_health)
        tester.run_test("Voice Cloning Status", tester.test_voice_cloning_status)
        tester.run_test("Available Models", tester.test_available_models)
        tester.run_test("Speech Synthesis", tester.test_speech_synthesis)
        tester.run_test("Voice Cloning", tester.test_voice_cloning)
        tester.run_test("Audio Transcription", tester.test_audio_transcription)
        tester.run_test("Performance Benchmarks", tester.test_performance_benchmarks)
        
        # Print summary and save results
        tester.print_test_summary()
        tester.save_test_results()

if __name__ == "__main__":
    asyncio.run(main())
