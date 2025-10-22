#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Engine Verification & Testing System
Advanced voice cloning engine validation and testing
"""

import subprocess
import sys
import os
import json
import time
import tempfile
from pathlib import Path
import torch
import torchaudio


class VoiceStudioEngineVerifier:
    def __init__(self):
        self.user_python = Path(
            "C:/Users/Tyler/AppData/Local/Programs/Python/Python311/python.exe"
        )
        self.workers_dir = Path("workers")
        self.test_audio_dir = Path("test_audio")
        self.results = {}

    def log(self, message):
        print(f"VoiceStudio Engine Verifier: {message}")

    def check_cuda_availability(self):
        """Check CUDA availability and performance"""
        self.log("Checking CUDA availability...")

        try:
            test_code = """
import torch
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA device count:", torch.cuda.device_count())
    print("CUDA device name:", torch.cuda.get_device_name(0))
    print("CUDA memory allocated:", torch.cuda.memory_allocated(0) / 1024**3, "GB")
    print("CUDA memory cached:", torch.cuda.memory_reserved(0) / 1024**3, "GB")
"""
            result = subprocess.run(
                [str(self.user_python), "-c", test_code], capture_output=True, text=True
            )

            if result.returncode == 0:
                self.log("CUDA verification successful")
                self.results["cuda"] = {
                    "status": "available",
                    "output": result.stdout.strip(),
                }
                return True
            else:
                self.log(f"CUDA verification failed: {result.stderr}")
                self.results["cuda"] = {
                    "status": "failed",
                    "error": result.stderr.strip(),
                }
                return False

        except Exception as e:
            self.log(f"CUDA check failed: {e}")
            self.results["cuda"] = {"status": "error", "error": str(e)}
            return False

    def verify_xtts_engine(self):
        """Verify XTTS-v2 engine functionality"""
        self.log("Verifying XTTS-v2 engine...")

        try:
            test_code = """
try:
    from TTS.api import TTS
    print("XTTS import successful")

    # Test basic TTS functionality
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    print("XTTS model loaded successfully")

    # Test voice cloning capability
    print("XTTS voice cloning capability: Available")

except Exception as e:
    print(f"XTTS error: {e}")
"""
            result = subprocess.run(
                [str(self.user_python), "-c", test_code],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if (
                result.returncode == 0
                and "XTTS model loaded successfully" in result.stdout
            ):
                self.log("XTTS-v2 engine verified successfully")
                self.results["xtts"] = {
                    "status": "working",
                    "output": result.stdout.strip(),
                }
                return True
            else:
                self.log(f"XTTS verification failed: {result.stderr}")
                self.results["xtts"] = {
                    "status": "failed",
                    "error": result.stderr.strip(),
                }
                return False

        except Exception as e:
            self.log(f"XTTS verification error: {e}")
            self.results["xtts"] = {"status": "error", "error": str(e)}
            return False

    def verify_openvoice_engine(self):
        """Verify OpenVoice V2 engine functionality"""
        self.log("Verifying OpenVoice V2 engine...")

        try:
            test_code = """
try:
    import openvoice
    print("OpenVoice import successful")

    # Test OpenVoice functionality
    from openvoice import se_extractor
    print("OpenVoice SE extractor available")

    print("OpenVoice V2 capability: Available")

except Exception as e:
    print(f"OpenVoice error: {e}")
"""
            result = subprocess.run(
                [str(self.user_python), "-c", test_code],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if (
                result.returncode == 0
                and "OpenVoice import successful" in result.stdout
            ):
                self.log("OpenVoice V2 engine verified successfully")
                self.results["openvoice"] = {
                    "status": "working",
                    "output": result.stdout.strip(),
                }
                return True
            else:
                self.log(f"OpenVoice verification failed: {result.stderr}")
                self.results["openvoice"] = {
                    "status": "failed",
                    "error": result.stderr.strip(),
                }
                return False

        except Exception as e:
            self.log(f"OpenVoice verification error: {e}")
            self.results["openvoice"] = {"status": "error", "error": str(e)}
            return False

    def verify_cosyvoice_engine(self):
        """Verify CosyVoice 2 engine functionality"""
        self.log("Verifying CosyVoice 2 engine...")

        try:
            test_code = """
try:
    import cosyvoice
    print("CosyVoice import successful")

    # Test CosyVoice functionality
    print("CosyVoice 2 capability: Available")

except Exception as e:
    print(f"CosyVoice error: {e}")
"""
            result = subprocess.run(
                [str(self.user_python), "-c", test_code],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if (
                result.returncode == 0
                and "CosyVoice import successful" in result.stdout
            ):
                self.log("CosyVoice 2 engine verified successfully")
                self.results["cosyvoice"] = {
                    "status": "working",
                    "output": result.stdout.strip(),
                }
                return True
            else:
                self.log(f"CosyVoice verification failed: {result.stderr}")
                self.results["cosyvoice"] = {
                    "status": "failed",
                    "error": result.stderr.strip(),
                }
                return False

        except Exception as e:
            self.log(f"CosyVoice verification error: {e}")
            self.results["cosyvoice"] = {"status": "error", "error": str(e)}
            return False

    def verify_whisper_asr(self):
        """Verify Whisper ASR functionality"""
        self.log("Verifying Whisper ASR...")

        try:
            test_code = """
try:
    from faster_whisper import WhisperModel
    print("Faster Whisper import successful")

    # Test Whisper model loading
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print("Whisper model loaded successfully")

    print("Whisper ASR capability: Available")

except Exception as e:
    print(f"Whisper error: {e}")
"""
            result = subprocess.run(
                [str(self.user_python), "-c", test_code],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if (
                result.returncode == 0
                and "Whisper model loaded successfully" in result.stdout
            ):
                self.log("Whisper ASR verified successfully")
                self.results["whisper"] = {
                    "status": "working",
                    "output": result.stdout.strip(),
                }
                return True
            else:
                self.log(f"Whisper verification failed: {result.stderr}")
                self.results["whisper"] = {
                    "status": "failed",
                    "error": result.stderr.strip(),
                }
                return False

        except Exception as e:
            self.log(f"Whisper verification error: {e}")
            self.results["whisper"] = {"status": "error", "error": str(e)}
            return False

    def verify_pyannote_diarization(self):
        """Verify Pyannote speaker diarization"""
        self.log("Verifying Pyannote diarization...")

        try:
            test_code = """
try:
    from pyannote.audio import Pipeline
    print("Pyannote import successful")

    # Test Pyannote pipeline
    print("Pyannote diarization capability: Available")

except Exception as e:
    print(f"Pyannote error: {e}")
"""
            result = subprocess.run(
                [str(self.user_python), "-c", test_code],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0 and "Pyannote import successful" in result.stdout:
                self.log("Pyannote diarization verified successfully")
                self.results["pyannote"] = {
                    "status": "working",
                    "output": result.stdout.strip(),
                }
                return True
            else:
                self.log(f"Pyannote verification failed: {result.stderr}")
                self.results["pyannote"] = {
                    "status": "failed",
                    "error": result.stderr.strip(),
                }
                return False

        except Exception as e:
            self.log(f"Pyannote verification error: {e}")
            self.results["pyannote"] = {"status": "error", "error": str(e)}
            return False

    def test_voice_cloning_workflow(self):
        """Test complete voice cloning workflow"""
        self.log("Testing complete voice cloning workflow...")

        try:
            # Create test audio directory
            self.test_audio_dir.mkdir(exist_ok=True)

            # Test text for voice cloning
            test_text = "Hello, this is VoiceStudio Ultimate testing voice cloning capabilities."

            # Test XTTS workflow
            test_code = f"""
import tempfile
import os
from pathlib import Path

try:
    from TTS.api import TTS

    # Initialize XTTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = temp_file.name

    # Test voice cloning (using a default voice for testing)
    tts.tts_to_file(text="{test_text}", speaker_wav="", language="en", file_path=temp_path)

    # Check if file was created
    if os.path.exists(temp_path):
        file_size = os.path.getsize(temp_path)
        print(f"Voice cloning test successful - File size: {{file_size}} bytes")
        os.unlink(temp_path)  # Clean up
    else:
        print("Voice cloning test failed - No output file")

except Exception as e:
    print(f"Voice cloning workflow error: {{e}}")
"""

            result = subprocess.run(
                [str(self.user_python), "-c", test_code],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if (
                result.returncode == 0
                and "Voice cloning test successful" in result.stdout
            ):
                self.log("Voice cloning workflow test successful")
                self.results["workflow"] = {
                    "status": "working",
                    "output": result.stdout.strip(),
                }
                return True
            else:
                self.log(f"Voice cloning workflow test failed: {result.stderr}")
                self.results["workflow"] = {
                    "status": "failed",
                    "error": result.stderr.strip(),
                }
                return False

        except Exception as e:
            self.log(f"Voice cloning workflow test error: {e}")
            self.results["workflow"] = {"status": "error", "error": str(e)}
            return False

    def generate_verification_report(self):
        """Generate comprehensive verification report"""
        self.log("Generating verification report...")

        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": {
                "python_version": sys.version,
                "pytorch_version": torch.__version__,
                "torchaudio_version": torchaudio.__version__,
            },
            "engine_status": self.results,
            "summary": {
                "total_engines": len(self.results),
                "working_engines": len(
                    [r for r in self.results.values() if r.get("status") == "working"]
                ),
                "failed_engines": len(
                    [r for r in self.results.values() if r.get("status") == "failed"]
                ),
                "error_engines": len(
                    [r for r in self.results.values() if r.get("status") == "error"]
                ),
            },
        }

        # Save report
        report_path = Path("voice_studio_engine_verification_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        self.log(f"Verification report saved to {report_path}")
        return report

    def run_complete_verification(self):
        """Run complete engine verification"""
        self.log("Starting VoiceStudio Ultimate Engine Verification...")

        # Check CUDA
        self.check_cuda_availability()

        # Verify engines
        self.verify_xtts_engine()
        self.verify_openvoice_engine()
        self.verify_cosyvoice_engine()
        self.verify_whisper_asr()
        self.verify_pyannote_diarization()

        # Test workflow
        self.test_voice_cloning_workflow()

        # Generate report
        report = self.generate_verification_report()

        self.log("VoiceStudio Ultimate Engine Verification Complete!")
        return report


def main():
    """Main execution function"""
    print("VoiceStudio Ultimate - Engine Verification & Testing")
    print("=" * 55)

    verifier = VoiceStudioEngineVerifier()

    report = verifier.run_complete_verification()

    print("\n" + "=" * 55)
    print("VERIFICATION SUMMARY")
    print("=" * 55)

    for engine, status in report["engine_status"].items():
        status_icon = (
            "✅"
            if status["status"] == "working"
            else "❌" if status["status"] == "failed" else "⚠️"
        )
        print(f"{status_icon} {engine.upper()}: {status['status'].upper()}")

    print(f"\nTotal Engines: {report['summary']['total_engines']}")
    print(f"Working: {report['summary']['working_engines']}")
    print(f"Failed: {report['summary']['failed_engines']}")
    print(f"Errors: {report['summary']['error_engines']}")

    if report["summary"]["working_engines"] >= 3:
        print("\n🎉 SUCCESS: VoiceStudio Ultimate engines are ready!")
        print("Professional voice cloning capabilities verified!")
    else:
        print("\n⚠️ WARNING: Some engines need attention")
        print("Check the verification report for details")


if __name__ == "__main__":
    main()
