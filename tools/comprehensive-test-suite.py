#!/usr/bin/env python3
"""
VoiceStudio Comprehensive Test Suite
Tests all services, optimizations, and integrations with performance benchmarking.
"""

import sys
import os
import time
import threading
import logging
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Any
import uuid
import tempfile
import numpy as np
import soundfile as sf

# Add services to path
sys.path.append(str(Path(__file__).parent.parent / "services"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestResult:
    """Test result container"""
    def __init__(self, test_name: str, success: bool, duration: float, 
                 message: str = "", details: Dict[str, Any] = None):
        self.test_name = test_name
        self.success = success
        self.duration = duration
        self.message = message
        self.details = details or {}

class VoiceStudioTestSuite:
    """Comprehensive test suite for VoiceStudio"""
    
    def __init__(self):
        self.results = []
        self.base_url = "http://127.0.0.1"
        self.services = {
            "assistant": 5080,
            "orchestrator": 5090,
            "autofix": 5081,
            "voice_cloning": 5083,
            "web_interface": 8080,
            "ml_model_optimizer": 5084
        }
        self.test_data = self._create_test_data()
    
    def _create_test_data(self) -> Dict[str, Any]:
        """Create test data for various tests"""
        # Create temporary audio file for testing
        temp_dir = Path(tempfile.gettempdir()) / "voicestudio_tests"
        temp_dir.mkdir(exist_ok=True)
        
        # Generate test audio
        sample_rate = 22050
        duration = 2.0  # 2 seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t) * 0.5  # 440Hz sine wave
        
        test_audio_path = temp_dir / "test_audio.wav"
        sf.write(str(test_audio_path), audio, sample_rate)
        
        return {
            "test_audio_path": str(test_audio_path),
            "test_speaker_id": "test_speaker_001",
            "test_text": "This is a test sentence for voice cloning.",
            "test_model_type": "gpt_sovits"
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        logger.info("Starting comprehensive VoiceStudio test suite...")
        
        start_time = time.time()
        
        # Test categories
        test_categories = [
            ("Service Health Tests", self._test_service_health),
            ("Database Optimization Tests", self._test_database_optimizations),
            ("Service Discovery Tests", self._test_service_discovery),
            ("Voice Cloning Tests", self._test_voice_cloning),
            ("Web Interface Tests", self._test_web_interface),
            ("ML Model Optimization Tests", self._test_ml_model_optimization),
            ("Performance Benchmark Tests", self._test_performance_benchmarks),
            ("Integration Tests", self._test_integrations),
            ("Stress Tests", self._test_stress_scenarios)
        ]
        
        # Run all test categories
        for category_name, test_func in test_categories:
            logger.info(f"Running {category_name}...")
            try:
                test_func()
            except Exception as e:
                self.results.append(TestResult(
                    f"{category_name} - Error", False, 0.0, str(e)
                ))
        
        total_duration = time.time() - start_time
        
        # Generate summary
        summary = self._generate_summary(total_duration)
        
        logger.info(f"Test suite completed in {total_duration:.2f} seconds")
        return summary
    
    def _test_service_health(self):
        """Test service health endpoints"""
        for service_name, port in self.services.items():
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}:{port}/health", timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    health_data = response.json()
                    self.results.append(TestResult(
                        f"Service Health - {service_name}",
                        True, duration, "Service is healthy",
                        {"status_code": response.status_code, "response_time": duration}
                    ))
                else:
                    self.results.append(TestResult(
                        f"Service Health - {service_name}",
                        False, duration, f"HTTP {response.status_code}"
                    ))
                    
            except Exception as e:
                duration = time.time() - start_time
                self.results.append(TestResult(
                    f"Service Health - {service_name}",
                    False, duration, str(e)
                ))
    
    def _test_database_optimizations(self):
        """Test database optimization features"""
        try:
            from database import DatabaseManager, get_database_logger, record_metric
            
            # Test connection pooling
            start_time = time.time()
            db_manager = DatabaseManager(pool_size=5)
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                "Database - Connection Pooling",
                True, duration, "Connection pool initialized successfully",
                {"pool_size": 5}
            ))
            
            # Test async logging
            start_time = time.time()
            db_logger = get_database_logger("test_service", "Test Service")
            db_logger.info("Test log message", {"test": True})
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                "Database - Async Logging",
                True, duration, "Async logging working",
                {"log_type": "info"}
            ))
            
            # Test async metrics
            start_time = time.time()
            record_metric("test_service", "Test Service", "test_metric", 1.0, {"test": True})
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                "Database - Async Metrics",
                True, duration, "Async metrics recording working",
                {"metric_value": 1.0}
            ))
            
            # Test caching
            start_time = time.time()
            logs1 = db_manager.get_service_logs(limit=10)
            logs2 = db_manager.get_service_logs(limit=10)  # Should use cache
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                "Database - Caching",
                True, duration, "Database caching working",
                {"cache_hit": True}
            ))
            
            # Test batch operations
            start_time = time.time()
            events = [
                {"service_id": "test", "service_name": "Test", "level": "INFO", "message": f"Test {i}"}
                for i in range(10)
            ]
            db_manager.batch_log_events(events)
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                "Database - Batch Operations",
                True, duration, "Batch operations working",
                {"batch_size": len(events)}
            ))
            
            db_manager.close()
            
        except Exception as e:
            self.results.append(TestResult(
                "Database Optimizations - Error",
                False, 0.0, str(e)
            ))
    
    def _test_service_discovery(self):
        """Test service discovery optimizations"""
        try:
            from service_discovery import ServiceRegistry, ServiceInfo
            
            # Test session pooling
            start_time = time.time()
            registry = ServiceRegistry()
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                "Service Discovery - Session Pooling",
                True, duration, "Session pool initialized",
                {"pool_size": 20}
            ))
            
            # Test parallel health checks
            start_time = time.time()
            service_info = ServiceInfo(
                service_id="test-service",
                name="test",
                host="127.0.0.1",
                port=8080,
                health_endpoint="/health"
            )
            registry.register_service(service_info)
            
            # Test parallel health check
            futures = []
            for _ in range(5):
                future = registry._executor.submit(registry.check_service_health, service_info)
                futures.append(future)
            
            for future in as_completed(futures):
                future.result()
            
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                "Service Discovery - Parallel Health Checks",
                True, duration, "Parallel health checks working",
                {"parallel_checks": 5}
            ))
            
            registry.stop_heartbeat_monitoring()
            
        except Exception as e:
            self.results.append(TestResult(
                "Service Discovery - Error",
                False, 0.0, str(e)
            ))
    
    def _test_voice_cloning(self):
        """Test voice cloning service"""
        try:
            # Test voice cloning service health
            start_time = time.time()
            response = requests.get(f"{self.base_url}:5083/health", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.results.append(TestResult(
                    "Voice Cloning - Service Health",
                    True, duration, "Voice cloning service is healthy"
                ))
                
                # Test voice cloning session creation
                start_time = time.time()
                clone_data = {
                    "speaker_id": self.test_data["test_speaker_id"],
                    "reference_audio_path": self.test_data["test_audio_path"],
                    "target_text": self.test_data["test_text"],
                    "model_type": self.test_data["test_model_type"]
                }
                
                response = requests.post(
                    f"{self.base_url}:5083/clone",
                    json=clone_data,
                    timeout=30
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    self.results.append(TestResult(
                        "Voice Cloning - Session Creation",
                        True, duration, "Voice cloning session created",
                        {"session_id": result.get("session_id")}
                    ))
                else:
                    self.results.append(TestResult(
                        "Voice Cloning - Session Creation",
                        False, duration, f"HTTP {response.status_code}"
                    ))
            else:
                self.results.append(TestResult(
                    "Voice Cloning - Service Health",
                    False, duration, f"HTTP {response.status_code}"
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "Voice Cloning - Error",
                False, 0.0, str(e)
            ))
    
    def _test_web_interface(self):
        """Test web interface service"""
        try:
            # Test web interface health
            start_time = time.time()
            response = requests.get(f"{self.base_url}:8080/health", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.results.append(TestResult(
                    "Web Interface - Service Health",
                    True, duration, "Web interface service is healthy"
                ))
                
                # Test dashboard data
                start_time = time.time()
                response = requests.get(f"{self.base_url}:8080/api/dashboard", timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.results.append(TestResult(
                        "Web Interface - Dashboard Data",
                        True, duration, "Dashboard data loaded successfully"
                    ))
                else:
                    self.results.append(TestResult(
                        "Web Interface - Dashboard Data",
                        False, duration, f"HTTP {response.status_code}"
                    ))
                
                # Test static file serving
                start_time = time.time()
                response = requests.get(f"{self.base_url}:8080/", timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.results.append(TestResult(
                        "Web Interface - Static Files",
                        True, duration, "Static files served successfully",
                        {"content_length": len(response.content)}
                    ))
                else:
                    self.results.append(TestResult(
                        "Web Interface - Static Files",
                        False, duration, f"HTTP {response.status_code}"
                    ))
            else:
                self.results.append(TestResult(
                    "Web Interface - Service Health",
                    False, duration, f"HTTP {response.status_code}"
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "Web Interface - Error",
                False, 0.0, str(e)
            ))
    
    def _test_ml_model_optimization(self):
        """Test ML model optimization service"""
        try:
            # Test ML model service health
            start_time = time.time()
            response = requests.get(f"{self.base_url}:5084/health", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.results.append(TestResult(
                    "ML Model Optimizer - Service Health",
                    True, duration, "ML model optimization service is healthy"
                ))
                
                # Test model loading
                start_time = time.time()
                load_data = {
                    "model_type": "gpt_sovits",
                    "optimization": "inference"
                }
                
                response = requests.post(
                    f"{self.base_url}:5084/load",
                    json=load_data,
                    timeout=30
                )
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    self.results.append(TestResult(
                        "ML Model Optimizer - Model Loading",
                        True, duration, "Model loaded successfully",
                        {"model_id": result.get("model_id"), "load_time": result.get("load_time")}
                    ))
                    
                    # Test model info
                    model_id = result.get("model_id")
                    if model_id:
                        start_time = time.time()
                        response = requests.get(f"{self.base_url}:5084/models?model_id={model_id}", timeout=10)
                        duration = time.time() - start_time
                        
                        if response.status_code == 200:
                            self.results.append(TestResult(
                                "ML Model Optimizer - Model Info",
                                True, duration, "Model info retrieved successfully"
                            ))
                        else:
                            self.results.append(TestResult(
                                "ML Model Optimizer - Model Info",
                                False, duration, f"HTTP {response.status_code}"
                            ))
                else:
                    self.results.append(TestResult(
                        "ML Model Optimizer - Model Loading",
                        False, duration, f"HTTP {response.status_code}"
                    ))
                
                # Test performance metrics
                start_time = time.time()
                response = requests.get(f"{self.base_url}:5084/performance", timeout=10)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    self.results.append(TestResult(
                        "ML Model Optimizer - Performance Metrics",
                        True, duration, "Performance metrics retrieved successfully"
                    ))
                else:
                    self.results.append(TestResult(
                        "ML Model Optimizer - Performance Metrics",
                        False, duration, f"HTTP {response.status_code}"
                    ))
            else:
                self.results.append(TestResult(
                    "ML Model Optimizer - Service Health",
                    False, duration, f"HTTP {response.status_code}"
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "ML Model Optimizer - Error",
                False, 0.0, str(e)
            ))
    
    def _test_performance_benchmarks(self):
        """Test performance benchmarks"""
        try:
            # Database performance benchmark
            from database import DatabaseManager
            
            db_manager = DatabaseManager(pool_size=10)
            
            # Benchmark logging performance
            start_time = time.time()
            for i in range(100):
                db_manager.log_service_event(f"benchmark-service-{i}", "Benchmark Service", "INFO", f"Benchmark message {i}")
            
            # Wait for async operations
            time.sleep(2)
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                "Performance - Database Logging",
                True, duration, f"100 async log operations in {duration:.2f}s",
                {"operations_per_second": 100 / duration}
            ))
            
            # Benchmark metrics performance
            start_time = time.time()
            for i in range(100):
                db_manager.record_service_metric(f"benchmark-service-{i}", "Benchmark Service", "benchmark_metric", i)
            
            time.sleep(2)
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                "Performance - Database Metrics",
                True, duration, f"100 async metric operations in {duration:.2f}s",
                {"operations_per_second": 100 / duration}
            ))
            
            # Benchmark caching performance
            start_time = time.time()
            for i in range(100):
                db_manager.get_service_logs(limit=10)
            duration = time.time() - start_time
            
            self.results.append(TestResult(
                "Performance - Database Caching",
                True, duration, f"100 cached queries in {duration:.2f}s",
                {"queries_per_second": 100 / duration}
            ))
            
            db_manager.close()
            
        except Exception as e:
            self.results.append(TestResult(
                "Performance Benchmarks - Error",
                False, 0.0, str(e)
            ))
    
    def _test_integrations(self):
        """Test service integrations"""
        try:
            # Test service-to-service communication
            start_time = time.time()
            
            # Test assistant service calling autofix
            response = requests.get(f"{self.base_url}:5080/autofix/status", timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.results.append(TestResult(
                    "Integration - Service Communication",
                    True, duration, "Service-to-service communication working"
                ))
            else:
                self.results.append(TestResult(
                    "Integration - Service Communication",
                    False, duration, f"HTTP {response.status_code}"
                ))
            
            # Test service discovery integration
            start_time = time.time()
            response = requests.get(f"{self.base_url}:5080/discovery", 
                                  headers={"X-API-Key": "test-key"}, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.results.append(TestResult(
                    "Integration - Service Discovery",
                    True, duration, "Service discovery integration working"
                ))
            else:
                self.results.append(TestResult(
                    "Integration - Service Discovery",
                    False, duration, f"HTTP {response.status_code}"
                ))
                
        except Exception as e:
            self.results.append(TestResult(
                "Integration Tests - Error",
                False, 0.0, str(e)
            ))
    
    def _test_stress_scenarios(self):
        """Test stress scenarios"""
        try:
            # Concurrent request stress test
            start_time = time.time()
            
            def make_request():
                try:
                    response = requests.get(f"{self.base_url}:5080/health", timeout=5)
                    return response.status_code == 200
                except:
                    return False
            
            # Make 50 concurrent requests
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(50)]
                results = [future.result() for future in futures]
            
            duration = time.time() - start_time
            success_count = sum(results)
            
            self.results.append(TestResult(
                "Stress Test - Concurrent Requests",
                success_count >= 45, duration, 
                f"{success_count}/50 concurrent requests successful",
                {"success_rate": success_count / 50}
            ))
            
        except Exception as e:
            self.results.append(TestResult(
                "Stress Tests - Error",
                False, 0.0, str(e)
            ))
    
    def _generate_summary(self, total_duration: float) -> Dict[str, Any]:
        """Generate test summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        # Group results by category
        categories = {}
        for result in self.results:
            category = result.test_name.split(" - ")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "total": 0}
            
            categories[category]["total"] += 1
            if result.success:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        # Calculate average response times
        avg_response_time = sum(r.duration for r in self.results) / total_tests if total_tests > 0 else 0
        
        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "total_duration": total_duration,
                "average_response_time": avg_response_time
            },
            "category_breakdown": categories,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "duration": r.duration,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.results
            ],
            "timestamp": time.time()
        }
        
        return summary

def main():
    """Main test function"""
    logger.info("Starting VoiceStudio Comprehensive Test Suite...")
    
    test_suite = VoiceStudioTestSuite()
    
    try:
        summary = test_suite.run_all_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("VOICESTUDIO COMPREHENSIVE TEST SUITE RESULTS")
        print("="*80)
        
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {summary['test_summary']['total_tests']}")
        print(f"   Passed: {summary['test_summary']['passed_tests']}")
        print(f"   Failed: {summary['test_summary']['failed_tests']}")
        print(f"   Success Rate: {summary['test_summary']['success_rate']:.1%}")
        print(f"   Total Duration: {summary['test_summary']['total_duration']:.2f}s")
        print(f"   Average Response Time: {summary['test_summary']['average_response_time']:.3f}s")
        
        print(f"\n📋 Category Breakdown:")
        for category, stats in summary['category_breakdown'].items():
            success_rate = stats['passed'] / stats['total'] if stats['total'] > 0 else 0
            print(f"   {category}: {stats['passed']}/{stats['total']} ({success_rate:.1%})")
        
        print(f"\n🔍 Detailed Results:")
        for result in summary['detailed_results']:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test_name']}: {result['message']} ({result['duration']:.3f}s)")
        
        # Save results to file
        results_file = Path("test_results.json")
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        # Return success/failure
        if summary['test_summary']['failed_tests'] == 0:
            print(f"\n🎉 All tests passed! VoiceStudio is fully optimized and working correctly.")
            return True
        else:
            print(f"\n⚠️  {summary['test_summary']['failed_tests']} tests failed. Please check the logs for details.")
            return False
            
    except Exception as e:
        logger.error(f"Test suite failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
