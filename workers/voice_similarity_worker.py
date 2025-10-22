# workers/voice_similarity_worker.py
# Voice similarity scoring worker for VoiceStudio

import os
import sys
import json
import time
import numpy as np
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_similarity_analyzer import VoiceSimilarityAnalyzer

class VoiceSimilarityWorker:
    def __init__(self, config_path=None):
        self.config_path = config_path or "config/similarity_scoring.json"
        self.analyzer = VoiceSimilarityAnalyzer(self.config_path)
        
    def compare_voices(self, reference_path, comparison_path):
        """Compare two voice files"""
        try:
            results = self.analyzer.compare_voices(reference_path, comparison_path)
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def batch_compare(self, reference_path, comparison_paths):
        """Batch compare multiple voices"""
        try:
            results = self.analyzer.batch_compare_voices(reference_path, comparison_paths)
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_features(self, audio_path):
        """Analyze voice features"""
        try:
            features = self.analyzer.extract_voice_features(audio_path)
            
            # Convert numpy arrays to lists for JSON serialization
            feature_dict = {
                "mfcc_mean": float(np.mean(features.mfcc)),
                "mfcc_std": float(np.std(features.mfcc)),
                "spectral_centroid_mean": float(np.mean(features.spectral_centroid)),
                "spectral_rolloff_mean": float(np.mean(features.spectral_rolloff)),
                "spectral_bandwidth_mean": float(np.mean(features.spectral_bandwidth)),
                "prosody_features": features.prosody_features,
                "timbre_features": features.timbre_features
            }
            
            return {"success": True, "features": feature_dict}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_quality_level(self, similarity_score):
        """Get quality level from similarity score"""
        if similarity_score >= 0.9:
            return "excellent"
        elif similarity_score >= 0.8:
            return "good"
        elif similarity_score >= 0.7:
            return "fair"
        elif similarity_score >= 0.6:
            return "poor"
        else:
            return "very_poor"

def main():
    """Main function for worker"""
    import argparse
    
    parser = argparse.ArgumentParser(description="VoiceStudio Voice Similarity Worker")
    parser.add_argument("--action", choices=["compare", "batch", "analyze"], required=True,
                       help="Action to perform")
    parser.add_argument("--reference", help="Reference audio file path")
    parser.add_argument("--comparison", help="Comparison audio file path")
    parser.add_argument("--comparisons", help="Comma-separated comparison file paths")
    parser.add_argument("--audio", help="Audio file path for feature analysis")
    
    args = parser.parse_args()
    
    worker = VoiceSimilarityWorker()
    
    if args.action == "compare":
        if not args.reference or not args.comparison:
            print("Error: --reference and --comparison required for compare action")
            sys.exit(1)
        
        result = worker.compare_voices(args.reference, args.comparison)
        print(json.dumps(result))
        
    elif args.action == "batch":
        if not args.reference or not args.comparisons:
            print("Error: --reference and --comparisons required for batch action")
            sys.exit(1)
        
        comparison_paths = [path.strip() for path in args.comparisons.split(",")]
        result = worker.batch_compare(args.reference, comparison_paths)
        print(json.dumps(result))
        
    elif args.action == "analyze":
        if not args.audio:
            print("Error: --audio required for analyze action")
            sys.exit(1)
        
        result = worker.analyze_features(args.audio)
        print(json.dumps(result))

if __name__ == "__main__":
    main()
