#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Performance Test Suite
Comprehensive testing for voice cloning performance and efficiency
"""

import os
import json
import time
import psutil
import numpy as np
import librosa
import pytest
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class VoiceCloningPerformanceTests:
    def __init__(self, test_data_path, results_path):
        self.test_data_path = Path(test_data_path)
        self.results_path = Path(results_path)
        self.reference_path = self.test_data_path / "reference_audio"
        self.text_path = self.test_data_path / "test_texts"
        
    def test_processing_latency(self, engine, reference_audio, test_text, output_path):
        """Test processing latency for voice cloning"""
        try:
            # Monitor system resources
            start_time = time.time()
            start_memory = psutil.virtual_memory().used
            start_cpu = psutil.cpu_percent()
            
            # Perform voice cloning
            result = self.clone_voice(engine, test_text, reference_audio, output_path)
            
            end_time = time.time()
            end_memory = psutil.virtual_memory().used
            end_cpu = psutil.cpu_percent()
            
            if not result['success']:
                return {'success': False, 'error': result['error']}
            
            # Calculate metrics
            processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
            memory_usage = (end_memory - start_memory) / (1024 * 1024)  # Convert to MB
            cpu_usage = end_cpu - start_cpu
            
            return {
                'success': True,
                'processing_time_ms': processing_time,
                'memory_usage_mb': memory_usage,
                'cpu_usage_percent': cpu_usage,
                'threshold_met': processing_time <= 10000  # 10 second threshold
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_memory_efficiency(self, engine, reference_audio, test_text, output_path):
        """Test memory efficiency during voice cloning"""
        try:
            # Get initial memory state
            initial_memory = psutil.virtual_memory()
            
            # Perform voice cloning
            result = self.clone_voice(engine, test_text, reference_audio, output_path)
            
            # Get final memory state
            final_memory = psutil.virtual_memory()
            
            if not result['success']:
                return {'success': False, 'error': result['error']}
            
            # Calculate memory metrics
            memory_used = (final_memory.used - initial_memory.used) / (1024 * 1024)  # MB
            peak_memory = final_memory.used / (1024 * 1024)  # MB
            memory_percent = final_memory.percent
            
            return {
                'success': True,
                'memory_used_mb': memory_used,
                'peak_memory_mb': peak_memory,
                'memory_percent': memory_percent,
                'threshold_met': peak_memory <= 4096  # 4GB threshold
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_cpu_efficiency(self, engine, reference_audio, test_text, output_path):
        """Test CPU efficiency during voice cloning"""
        try:
            # Monitor CPU usage
            cpu_samples = []
            
            def monitor_cpu():
                while True:
                    cpu_samples.append(psutil.cpu_percent())
                    time.sleep(0.1)
            
            # Start CPU monitoring
            monitor_thread = threading.Thread(target=monitor_cpu)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Perform voice cloning
            result = self.clone_voice(engine, test_text, reference_audio, output_path)
            
            # Stop monitoring
            time.sleep(0.5)  # Let monitoring finish
            
            if not result['success']:
                return {'success': False, 'error': result['error']}
            
            # Calculate CPU metrics
            avg_cpu = np.mean(cpu_samples) if cpu_samples else 0
            max_cpu = np.max(cpu_samples) if cpu_samples else 0
            min_cpu = np.min(cpu_samples) if cpu_samples else 0
            
            return {
                'success': True,
                'avg_cpu_percent': avg_cpu,
                'max_cpu_percent': max_cpu,
                'min_cpu_percent': min_cpu,
                'cpu_samples': len(cpu_samples),
                'threshold_met': avg_cpu <= 80  # 80% threshold
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_concurrent_processing(self, engine, test_cases):
        """Test concurrent processing capabilities"""
        try:
            results = []
            
            def process_single_case(case):
                reference_audio, test_text, output_path = case
                return self.clone_voice(engine, test_text, reference_audio, output_path)
            
            # Process cases concurrently
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(process_single_case, case) for case in test_cases]
                results = [future.result() for future in as_completed(futures)]
            
            end_time = time.time()
            total_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Calculate metrics
            successful_results = [r for r in results if r['success']]
            success_rate = len(successful_results) / len(results) if results else 0
            avg_time_per_case = total_time / len(test_cases) if test_cases else 0
            
            return {
                'success': True,
                'total_time_ms': total_time,
                'avg_time_per_case_ms': avg_time_per_case,
                'success_rate': success_rate,
                'total_cases': len(test_cases),
                'successful_cases': len(successful_results),
                'threshold_met': success_rate >= 0.95  # 95% success rate threshold
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_scalability(self, engine, reference_audio, test_text, max_concurrent=10):
        """Test scalability with increasing concurrent requests"""
        try:
            scalability_results = []
            
            for concurrent_count in range(1, max_concurrent + 1):
                # Create test cases
                test_cases = []
                for i in range(concurrent_count):
                    output_path = self.results_path / "performance" / f"scalability_{concurrent_count}_{i}.wav"
                    test_cases.append((reference_audio, test_text, output_path))
                
                # Test concurrent processing
                result = self.test_concurrent_processing(engine, test_cases)
                
                if result['success']:
                    scalability_results.append({
                        'concurrent_count': concurrent_count,
                        'total_time_ms': result['total_time_ms'],
                        'avg_time_per_case_ms': result['avg_time_per_case_ms'],
                        'success_rate': result['success_rate']
                    })
            
            return {
                'success': True,
                'scalability_results': scalability_results,
                'max_concurrent': max_concurrent
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def clone_voice(self, engine, text, reference_audio, output_path):
        """Perform voice cloning using specified engine"""
        try:
            # This is a placeholder for actual voice cloning
            # In practice, you would call the actual voice cloning engine
            
            # Simulate voice cloning process with variable time
            processing_time = np.random.uniform(1, 5)  # 1-5 seconds
            time.sleep(processing_time)
            
            # For testing, we'll copy the reference audio
            # In practice, this would be the actual cloned voice
            import shutil
            shutil.copy(reference_audio, output_path)
            
            return {'success': True, 'output_path': output_path}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_comprehensive_performance_tests(self):
        """Run comprehensive performance tests for all engines"""
        test_results = {}
        
        # Load test configuration
        config_path = Path("C:/Users/Tyler/VoiceStudio/tests/test_config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        engines = config['engines']
        test_texts = self.load_test_texts()
        reference_audios = list(self.reference_path.glob("*.wav"))
        
        for engine_name, engine_config in engines.items():
            if not engine_config['enabled']:
                continue
                
            print(f"Testing engine performance: {engine_name}")
            engine_results = {}
            
            # Test with first reference audio and text
            ref_audio = reference_audios[0]
            test_text = test_texts[0]
            
            # Processing latency test
            output_path = self.results_path / "performance" / f"{engine_name}_latency.wav"
            latency_result = self.test_processing_latency(engine_name, ref_audio, test_text, output_path)
            engine_results['latency'] = latency_result
            
            # Memory efficiency test
            output_path = self.results_path / "performance" / f"{engine_name}_memory.wav"
            memory_result = self.test_memory_efficiency(engine_name, ref_audio, test_text, output_path)
            engine_results['memory'] = memory_result
            
            # CPU efficiency test
            output_path = self.results_path / "performance" / f"{engine_name}_cpu.wav"
            cpu_result = self.test_cpu_efficiency(engine_name, ref_audio, test_text, output_path)
            engine_results['cpu'] = cpu_result
            
            # Scalability test
            scalability_result = self.test_scalability(engine_name, ref_audio, test_text, max_concurrent=5)
            engine_results['scalability'] = scalability_result
            
            test_results[engine_name] = engine_results
        
        # Save results
        results_path = self.results_path / "performance" / "performance_test_results.json"
        with open(results_path, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"Performance test results saved: {results_path}")
        return test_results
    
    def load_test_texts(self):
        """Load test texts from files"""
        text_files = list(self.text_path.glob("*.txt"))
        return text_files

def main():
    test_data_path = "C:/Users/Tyler/VoiceStudio/tests/data"
    results_path = "C:/Users/Tyler/VoiceStudio/tests/results"
    
    performance_tests = VoiceCloningPerformanceTests(test_data_path, results_path)
    
    print("VoiceStudio Ultimate - Performance Test Suite")
    print("=" * 50)
    
    results = performance_tests.run_comprehensive_performance_tests()
    
    print("=" * 50)
    print("Performance testing complete!")

if __name__ == "__main__":
    main()
