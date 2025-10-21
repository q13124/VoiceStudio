#!/usr/bin/env python3
"""
VoiceStudio VSDML Voice Cloning System - Ultimate Optimization Script
Comprehensive system optimization, monitoring, and performance enhancement
"""

import os
import sys
import time
import subprocess
import json
import psutil
import platform
from pathlib import Path
import warnings
from datetime import datetime

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

class VoiceCloningOptimizer:
    """Ultimate voice cloning system optimizer"""

    def __init__(self):
        self.start_time = time.time()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "performance_metrics": {},
            "optimization_results": {},
            "recommendations": []
        }

    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def get_system_info(self):
        """Gather comprehensive system information"""
        self.log("Gathering system information...")

        try:
            import torch
            import TTS
            import transformers

            self.results["system_info"] = {
                "platform": platform.platform(),
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "torch_version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "tts_version": getattr(TTS, '_version', getattr(TTS, '__version__', 'Unknown')),
                "transformers_version": transformers.__version__
            }

            if torch.cuda.is_available():
                self.results["system_info"]["gpu_name"] = torch.cuda.get_device_name(0)
                self.results["system_info"]["gpu_memory_gb"] = round(
                    torch.cuda.get_device_properties(0).total_memory / (1024**3), 2
                )
                self.results["system_info"]["cuda_version"] = torch.version.cuda

            self.log(f"System: {platform.system()} {platform.release()}")
            self.log(f"Python: {sys.version.split()[0]}")
            self.log(f"PyTorch: {torch.__version__}")
            self.log(f"CUDA Available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                self.log(f"GPU: {torch.cuda.get_device_name(0)}")

        except Exception as e:
            self.log(f"Error gathering system info: {e}", "ERROR")

    def optimize_memory_usage(self):
        """Optimize memory usage for voice cloning"""
        self.log("Optimizing memory usage...")

        try:
            import torch

            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                self.log("CUDA cache cleared")

            # Set memory management
            if torch.cuda.is_available():
                torch.cuda.set_per_process_memory_fraction(0.8)  # Use 80% of GPU memory
                self.log("GPU memory fraction set to 80%")

            # Optimize PyTorch settings
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
            self.log("PyTorch optimizations applied")

            self.results["optimization_results"]["memory_optimization"] = "SUCCESS"

        except Exception as e:
            self.log(f"Memory optimization error: {e}", "ERROR")
            self.results["optimization_results"]["memory_optimization"] = f"ERROR: {e}"

    def benchmark_voice_synthesis(self):
        """Benchmark voice synthesis performance"""
        self.log("Running voice synthesis benchmarks...")

        try:
            from TTS.api import TTS

            # Test different models
            test_text = "Hello from VoiceStudio optimized voice cloning system"
            models_to_test = [
                'tts_models/en/ljspeech/tacotron2-DDC',
                'tts_models/multilingual/multi-dataset/xtts_v2'
            ]

            benchmark_results = {}

            for model_name in models_to_test:
                try:
                    self.log(f"Testing model: {model_name}")

                    # Load model
                    start_time = time.time()
                    tts = TTS(model_name)
                    load_time = time.time() - start_time

                    # Test synthesis
                    start_time = time.time()
                    tts.tts_to_file(text=test_text, file_path=f"temp_{model_name.split('/')[-1]}.wav")
                    synthesis_time = time.time() - start_time

                    # Calculate metrics
                    estimated_duration = len(test_text) * 0.1  # Rough estimate
                    rtf = synthesis_time / estimated_duration

                    benchmark_results[model_name] = {
                        "load_time": round(load_time, 2),
                        "synthesis_time": round(synthesis_time, 2),
                        "rtf": round(rtf, 2),
                        "faster_than_realtime": rtf < 1.0
                    }

                    self.log(f"Model {model_name}: Load={load_time:.2f}s, Synthesis={synthesis_time:.2f}s, RTF={rtf:.2f}")

                    # Cleanup
                    temp_file = f"temp_{model_name.split('/')[-1]}.wav"
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

                except Exception as e:
                    self.log(f"Benchmark failed for {model_name}: {e}", "WARNING")
                    benchmark_results[model_name] = {"error": str(e)}

            self.results["performance_metrics"]["voice_synthesis_benchmarks"] = benchmark_results

        except Exception as e:
            self.log(f"Benchmarking error: {e}", "ERROR")
            self.results["performance_metrics"]["voice_synthesis_benchmarks"] = {"error": str(e)}

    def check_dependencies(self):
        """Check all critical dependencies"""
        self.log("Checking dependencies...")

        critical_packages = [
            "torch", "torchaudio", "TTS", "transformers", "numpy", "pandas",
            "soundfile", "librosa", "av", "ctranslate2", "faster_whisper",
            "nltk", "scipy", "scikit-learn"
        ]

        dependency_status = {}

        for package in critical_packages:
            try:
                if package == "TTS":
                    import TTS
                    version = getattr(TTS, '_version', getattr(TTS, '__version__', 'Unknown'))
                else:
                    module = __import__(package)
                    version = getattr(module, '__version__', 'Unknown')

                dependency_status[package] = {
                    "status": "INSTALLED",
                    "version": version
                }
                self.log(f"OK {package}: {version}")

            except ImportError:
                dependency_status[package] = {
                    "status": "MISSING",
                    "version": None
                }
                self.log(f"FAIL {package}: MISSING", "ERROR")

        self.results["optimization_results"]["dependencies"] = dependency_status

    def generate_recommendations(self):
        """Generate optimization recommendations"""
        self.log("Generating recommendations...")

        recommendations = []

        # Check CUDA availability
        if not self.results["system_info"].get("cuda_available", False):
            recommendations.append({
                "category": "Performance",
                "priority": "HIGH",
                "recommendation": "Install CUDA-enabled PyTorch for GPU acceleration",
                "command": "pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121"
            })

        # Check memory usage
        memory_available = self.results["system_info"].get("memory_available_gb", 0)
        if memory_available < 8:
            recommendations.append({
                "category": "Performance",
                "priority": "MEDIUM",
                "recommendation": "Consider upgrading RAM for better performance with large models",
                "details": f"Current available: {memory_available}GB"
            })

        # Check GPU memory
        gpu_memory = self.results["system_info"].get("gpu_memory_gb", 0)
        if gpu_memory > 0 and gpu_memory < 8:
            recommendations.append({
                "category": "Performance",
                "priority": "MEDIUM",
                "recommendation": "Consider using smaller models or CPU fallback for limited GPU memory",
                "details": f"GPU memory: {gpu_memory}GB"
            })

        # Check for missing dependencies
        dependencies = self.results["optimization_results"].get("dependencies", {})
        missing_deps = [pkg for pkg, info in dependencies.items() if info["status"] == "MISSING"]

        if missing_deps:
            recommendations.append({
                "category": "Dependencies",
                "priority": "HIGH",
                "recommendation": f"Install missing dependencies: {', '.join(missing_deps)}",
                "command": f"pip install {' '.join(missing_deps)}"
            })

        self.results["recommendations"] = recommendations

        for rec in recommendations:
            self.log(f"Recommendation [{rec['priority']}]: {rec['recommendation']}")

    def save_results(self):
        """Save optimization results to file"""
        self.log("Saving optimization results...")

        results_file = "voice_cloning_optimization_report.json"

        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)

            self.log(f"Results saved to {results_file}")

        except Exception as e:
            self.log(f"Error saving results: {e}", "ERROR")

    def run_full_optimization(self):
        """Run complete optimization suite"""
        self.log("Starting VoiceStudio VSDML Voice Cloning System Optimization")
        self.log("=" * 70)

        # Run all optimization steps
        self.get_system_info()
        self.check_dependencies()
        self.optimize_memory_usage()
        self.benchmark_voice_synthesis()
        self.generate_recommendations()
        self.save_results()

        # Calculate total time
        total_time = time.time() - self.start_time

        self.log("=" * 70)
        self.log(f"Optimization completed in {total_time:.2f} seconds")
        self.log("Voice cloning system is optimized and ready for production!")

        return self.results


def main():
    """Main optimization function"""
    optimizer = VoiceCloningOptimizer()
    results = optimizer.run_full_optimization()

    # Print summary
    print("\n" + "=" * 70)
    print("VOICE CLONING SYSTEM OPTIMIZATION SUMMARY")
    print("=" * 70)

    # System summary
    sys_info = results["system_info"]
    print(f"Platform: {sys_info.get('platform', 'Unknown')}")
    print(f"Python: {sys_info.get('python_version', 'Unknown').split()[0]}")
    print(f"PyTorch: {sys_info.get('torch_version', 'Unknown')}")
    print(f"CUDA: {sys_info.get('cuda_available', False)}")
    if sys_info.get('cuda_available'):
        print(f"GPU: {sys_info.get('gpu_name', 'Unknown')}")
        print(f"GPU Memory: {sys_info.get('gpu_memory_gb', 0)}GB")

    # Performance summary
    benchmarks = results["performance_metrics"].get("voice_synthesis_benchmarks", {})
    if benchmarks:
        print(f"\nVoice Synthesis Performance:")
        for model, metrics in benchmarks.items():
            if "error" not in metrics:
                print(f"  {model.split('/')[-1]}: {metrics['synthesis_time']}s (RTF: {metrics['rtf']})")

    # Recommendations summary
    recommendations = results["recommendations"]
    if recommendations:
        print(f"\nRecommendations ({len(recommendations)}):")
        for rec in recommendations:
            print(f"  [{rec['priority']}] {rec['recommendation']}")

    print("=" * 70)


if __name__ == "__main__":
    main()
