#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Test Runner
Comprehensive test execution and reporting system
"""

import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import sys

class VoiceStudioTestRunner:
    def __init__(self, test_data_path, results_path):
        self.test_data_path = Path(test_data_path)
        self.results_path = Path(results_path)
        self.config_path = Path("C:/Users/Tyler/VoiceStudio/tests/test_config.json")
        
    def load_test_config(self):
        """Load test configuration"""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def generate_test_data(self):
        """Generate test data if not exists"""
        print("Generating test data...")
        try:
            subprocess.run([
                sys.executable, 
                str(self.test_data_path.parent / "generate_test_data.py")
            ], check=True)
            print("Test data generation complete")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Test data generation failed: {e}")
            return False
    
    def run_accuracy_tests(self):
        """Run accuracy tests"""
        print("Running accuracy tests...")
        try:
            subprocess.run([
                sys.executable, 
                str(self.test_data_path.parent / "test_accuracy.py")
            ], check=True)
            print("Accuracy tests complete")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Accuracy tests failed: {e}")
            return False
    
    def run_performance_tests(self):
        """Run performance tests"""
        print("Running performance tests...")
        try:
            subprocess.run([
                sys.executable, 
                str(self.test_data_path.parent / "test_performance.py")
            ], check=True)
            print("Performance tests complete")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Performance tests failed: {e}")
            return False
    
    def run_pytest_tests(self):
        """Run pytest unit tests"""
        print("Running pytest unit tests...")
        try:
            subprocess.run([
                sys.executable, "-m", "pytest", 
                str(self.test_data_path.parent),
                "-v", "--tb=short"
            ], check=True)
            print("Pytest tests complete")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Pytest tests failed: {e}")
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("Generating test report...")
        
        report = {
            "test_suite": "VoiceStudio Ultimate Test Suite",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {},
            "accuracy_results": {},
            "performance_results": {},
            "recommendations": []
        }
        
        # Load accuracy results
        accuracy_path = self.results_path / "accuracy" / "accuracy_test_results.json"
        if accuracy_path.exists():
            with open(accuracy_path, 'r') as f:
                report["accuracy_results"] = json.load(f)
        
        # Load performance results
        performance_path = self.results_path / "performance" / "performance_test_results.json"
        if performance_path.exists():
            with open(performance_path, 'r') as f:
                report["performance_results"] = json.load(f)
        
        # Generate summary
        report["summary"] = self.generate_summary(report)
        
        # Generate recommendations
        report["recommendations"] = self.generate_recommendations(report)
        
        # Save report
        report_path = self.results_path / "test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Test report saved: {report_path}")
        return report
    
    def generate_summary(self, report):
        """Generate test summary"""
        summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "success_rate": 0.0,
            "engines_tested": [],
            "overall_quality": "Unknown"
        }
        
        # Analyze accuracy results
        if report["accuracy_results"]:
            for engine, results in report["accuracy_results"].items():
                summary["engines_tested"].append(engine)
                for test_name, test_results in results.items():
                    summary["total_tests"] += 1
                    if all(result.get("threshold_met", False) for result in test_results.values()):
                        summary["passed_tests"] += 1
                    else:
                        summary["failed_tests"] += 1
        
        # Calculate success rate
        if summary["total_tests"] > 0:
            summary["success_rate"] = summary["passed_tests"] / summary["total_tests"]
        
        # Determine overall quality
        if summary["success_rate"] >= 0.95:
            summary["overall_quality"] = "Excellent"
        elif summary["success_rate"] >= 0.85:
            summary["overall_quality"] = "Good"
        elif summary["success_rate"] >= 0.70:
            summary["overall_quality"] = "Fair"
        else:
            summary["overall_quality"] = "Needs Improvement"
        
        return summary
    
    def generate_recommendations(self, report):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze accuracy results
        if report["accuracy_results"]:
            for engine, results in report["accuracy_results"].items():
                for test_name, test_results in results.items():
                    for test_type, result in test_results.items():
                        if not result.get("threshold_met", False):
                            recommendations.append({
                                "type": "accuracy",
                                "engine": engine,
                                "test": test_type,
                                "issue": f"{test_type} below threshold",
                                "recommendation": f"Improve {test_type} for {engine} engine"
                            })
        
        # Analyze performance results
        if report["performance_results"]:
            for engine, results in report["performance_results"].items():
                if "latency" in results and not results["latency"].get("threshold_met", False):
                    recommendations.append({
                        "type": "performance",
                        "engine": engine,
                        "issue": "High processing latency",
                        "recommendation": f"Optimize {engine} engine for better performance"
                    })
                
                if "memory" in results and not results["memory"].get("threshold_met", False):
                    recommendations.append({
                        "type": "performance",
                        "engine": engine,
                        "issue": "High memory usage",
                        "recommendation": f"Optimize memory usage for {engine} engine"
                    })
        
        return recommendations
    
    def run_all_tests(self):
        """Run all tests"""
        print("VoiceStudio Ultimate - Test Runner")
        print("=" * 50)
        
        # Generate test data
        if not self.generate_test_data():
            return False
        
        # Run accuracy tests
        if not self.run_accuracy_tests():
            return False
        
        # Run performance tests
        if not self.run_performance_tests():
            return False
        
        # Run pytest tests
        if not self.run_pytest_tests():
            return False
        
        # Generate report
        report = self.generate_test_report()
        
        print("=" * 50)
        print("All tests complete!")
        print(f"Overall Quality: {report['summary']['overall_quality']}")
        print(f"Success Rate: {report['summary']['success_rate']:.2%}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="VoiceStudio Ultimate Test Runner")
    parser.add_argument("--test-data", default="C:/Users/Tyler/VoiceStudio/tests/data",
                       help="Path to test data directory")
    parser.add_argument("--results", default="C:/Users/Tyler/VoiceStudio/tests/results",
                       help="Path to test results directory")
    parser.add_argument("--accuracy-only", action="store_true",
                       help="Run only accuracy tests")
    parser.add_argument("--performance-only", action="store_true",
                       help="Run only performance tests")
    
    args = parser.parse_args()
    
    test_runner = VoiceStudioTestRunner(args.test_data, args.results)
    
    if args.accuracy_only:
        test_runner.generate_test_data()
        test_runner.run_accuracy_tests()
    elif args.performance_only:
        test_runner.generate_test_data()
        test_runner.run_performance_tests()
    else:
        test_runner.run_all_tests()

if __name__ == "__main__":
    main()
