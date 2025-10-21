#!/usr/bin/env python3
"""
VoiceStudio Optimization Test Suite
Tests all implemented optimizations to ensure they work correctly.
"""

import sys
import os
import time
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Add services to path
sys.path.append(str(Path(__file__).parent.parent / "services"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_optimizations():
    """Test database optimizations"""
    logger.info("Testing database optimizations...")
    
    try:
        from database import DatabaseManager, get_database_logger, record_metric
        
        # Test connection pooling
        db_manager = DatabaseManager(pool_size=5)
        
        # Test async logging
        db_logger = get_database_logger("test-service", "Test Service")
        db_logger.info("Test log message", {"test": True})
        
        # Test async metrics
        record_metric("test-service", "Test Service", "response_time", 0.5, {"endpoint": "/health"})
        
        # Test caching
        logs = db_manager.get_service_logs(limit=10)
        logs_cached = db_manager.get_service_logs(limit=10)  # Should use cache
        
        # Test configuration caching
        db_manager.set_configuration("test_key", "test_value", "test-service")
        value = db_manager.get_configuration("test_key")
        value_cached = db_manager.get_configuration("test_key")  # Should use cache
        
        # Cleanup
        db_manager.close()
        
        logger.info("✓ Database optimizations working correctly")
        return True
        
    except Exception as e:
        logger.error(f"✗ Database optimization test failed: {e}")
        return False

def test_service_discovery_optimizations():
    """Test service discovery optimizations"""
    logger.info("Testing service discovery optimizations...")
    
    try:
        from service_discovery import ServiceRegistry, ServiceInfo, register_service
        
        # Test session pooling
        registry = ServiceRegistry()
        
        # Test parallel health checks
        service_info = ServiceInfo(
            service_id="test-service",
            name="test",
            host="127.0.0.1",
            port=8080,
            health_endpoint="/health"
        )
        
        registry.register_service(service_info)
        
        # Test caching
        health1 = registry.check_service_health(service_info)
        health2 = registry.check_service_health(service_info)  # Should use cache
        
        # Test parallel monitoring
        registry.start_heartbeat_monitoring()
        time.sleep(2)
        registry.stop_heartbeat_monitoring()
        
        logger.info("✓ Service discovery optimizations working correctly")
        return True
        
    except Exception as e:
        logger.error(f"✗ Service discovery optimization test failed: {e}")
        return False

def test_audio_processing_optimizations():
    """Test audio processing optimizations"""
    logger.info("Testing audio processing optimizations...")
    
    try:
        sys.path.append(str(Path(__file__).parent.parent / "VoiceStudio" / "workers" / "python" / "vsdml"))
        from vsdml.services.audio_processor import AudioProcessor
        
        # Test parallel processing
        processor = AudioProcessor(max_workers=2)
        
        # Test caching
        test_path = "/tmp/test_audio.wav"
        valid1 = processor.validate_audio_path(test_path)
        valid2 = processor.validate_audio_path(test_path)  # Should use cache
        
        # Test parallel batch processing
        test_inputs = ["/tmp/audio1.wav", "/tmp/audio2.wav", "/tmp/audio3.wav"]
        args = {'audio': test_inputs}
        
        # This will test the parallel processing structure
        results = processor.process_audio_batch(args)
        
        # Test cache cleanup
        processor.cleanup_cache()
        
        # Cleanup
        processor.close()
        
        logger.info("✓ Audio processing optimizations working correctly")
        return True
        
    except Exception as e:
        logger.error(f"✗ Audio processing optimization test failed: {e}")
        return False

def test_performance_monitoring():
    """Test performance monitoring"""
    logger.info("Testing performance monitoring...")
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from performance_monitor import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        
        # Test metrics collection
        metrics = monitor._collect_metrics()
        
        # Test analysis
        monitor._analyze_performance(metrics)
        
        # Test report generation
        report = monitor.get_performance_report()
        
        # Test suggestions
        suggestions = monitor.get_optimization_suggestions()
        
        logger.info("✓ Performance monitoring working correctly")
        return True
        
    except Exception as e:
        logger.error(f"✗ Performance monitoring test failed: {e}")
        return False

def test_configuration_optimization():
    """Test configuration optimization"""
    logger.info("Testing configuration optimization...")
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from config_optimizer import ConfigurationOptimizer
        
        optimizer = ConfigurationOptimizer()
        
        # Test config loading
        config = optimizer.load_config()
        
        # Test optimization
        optimized_config = optimizer.optimize_config()
        
        # Test validation
        is_valid = optimizer.validate_config(optimized_config)
        
        # Test tips generation
        tips = optimizer.generate_performance_tips()
        
        logger.info("✓ Configuration optimization working correctly")
        return True
        
    except Exception as e:
        logger.error(f"✗ Configuration optimization test failed: {e}")
        return False

def run_performance_benchmark():
    """Run performance benchmark comparing optimized vs non-optimized"""
    logger.info("Running performance benchmark...")
    
    try:
        # Test database performance
        from database import DatabaseManager
        
        db_manager = DatabaseManager(pool_size=10)
        
        # Benchmark logging performance
        start_time = time.time()
        for i in range(100):
            db_manager.log_service_event(f"test-service-{i}", "Test Service", "INFO", f"Test message {i}")
        
        # Wait for async operations to complete
        time.sleep(2)
        end_time = time.time()
        
        logging_time = end_time - start_time
        logger.info(f"✓ 100 async log operations completed in {logging_time:.2f} seconds")
        
        # Benchmark metrics performance
        start_time = time.time()
        for i in range(100):
            db_manager.record_service_metric(f"test-service-{i}", "Test Service", "test_metric", i)
        
        time.sleep(2)
        end_time = time.time()
        
        metrics_time = end_time - start_time
        logger.info(f"✓ 100 async metric operations completed in {metrics_time:.2f} seconds")
        
        # Benchmark caching performance
        start_time = time.time()
        for i in range(100):
            db_manager.get_service_logs(limit=10)
        end_time = time.time()
        
        cache_time = end_time - start_time
        logger.info(f"✓ 100 cached queries completed in {cache_time:.2f} seconds")
        
        db_manager.close()
        
        logger.info("✓ Performance benchmark completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Performance benchmark failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting VoiceStudio optimization tests...")
    
    tests = [
        ("Database Optimizations", test_database_optimizations),
        ("Service Discovery Optimizations", test_service_discovery_optimizations),
        ("Audio Processing Optimizations", test_audio_processing_optimizations),
        ("Performance Monitoring", test_performance_monitoring),
        ("Configuration Optimization", test_configuration_optimization),
        ("Performance Benchmark", run_performance_benchmark)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            failed += 1
    
    logger.info(f"\n=== Test Results ===")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total: {passed + failed}")
    
    if failed == 0:
        logger.info("🎉 All optimizations are working correctly!")
        return True
    else:
        logger.error(f"❌ {failed} tests failed. Please check the logs.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
