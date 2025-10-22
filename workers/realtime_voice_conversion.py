# workers/realtime_voice_conversion.py
# Real-time voice conversion worker for VoiceStudio

import os
import sys
import json
import time
import numpy as np
import librosa
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_realtime_converter import RealtimeVoiceConverter

class RealtimeVoiceConversionWorker:
    def __init__(self, config_path=None):
        self.config_path = config_path or "config/realtime_conversion.json"
        self.converter = RealtimeVoiceConverter(self.config_path)
        self.is_running = False
        
    def start_conversion(self, reference_path, input_device=None, output_device=None):
        """Start real-time voice conversion"""
        try:
            # Load reference voice
            if not self.converter.load_reference_voice(reference_path):
                return {"success": False, "error": "Failed to load reference voice"}
            
            # Start conversion
            self.converter.start_conversion(input_device, output_device)
            self.is_running = True
            
            return {"success": True, "status": "conversion_started"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop_conversion(self):
        """Stop real-time voice conversion"""
        try:
            self.converter.stop_conversion()
            self.is_running = False
            
            return {"success": True, "status": "conversion_stopped"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_stats(self):
        """Get performance statistics"""
        try:
            stats = self.converter.get_performance_stats()
            return {"success": True, "stats": stats}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def optimize_for_latency(self):
        """Optimize for ultra-low latency"""
        try:
            self.converter.optimize_for_latency()
            return {"success": True, "status": "optimized"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Main function for worker"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VoiceStudio Real-Time Voice Conversion Worker")
    parser.add_argument("--action", choices=["start", "stop", "stats", "optimize"], required=True,
                       help="Action to perform")
    parser.add_argument("--reference", help="Path to reference voice file")
    parser.add_argument("--input-device", type=int, help="Input audio device ID")
    parser.add_argument("--output-device", type=int, help="Output audio device ID")
    
    args = parser.parse_args()
    
    worker = RealtimeVoiceConversionWorker()
    
    if args.action == "start":
        if not args.reference:
            print("Error: --reference required for start action")
            sys.exit(1)
        
        result = worker.start_conversion(args.reference, args.input_device, args.output_device)
        print(json.dumps(result))
        
    elif args.action == "stop":
        result = worker.stop_conversion()
        print(json.dumps(result))
        
    elif args.action == "stats":
        result = worker.get_stats()
        print(json.dumps(result))
        
    elif args.action == "optimize":
        result = worker.optimize_for_latency()
        print(json.dumps(result))

if __name__ == "__main__":
    main()
