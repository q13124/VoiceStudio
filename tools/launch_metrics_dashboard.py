#!/usr/bin/env python3
"""
VoiceStudio Ultimate - Metrics Dashboard Launcher
Launch the quality metrics dashboard
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_metrics_dashboard import VoiceCloningMetricsDashboard

def main():
    parser = argparse.ArgumentParser(description="VoiceStudio Metrics Dashboard Launcher")
    parser.add_argument("--host", default="127.0.0.1", help="Dashboard host")
    parser.add_argument("--port", type=int, default=8050, help="Dashboard port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--generate-samples", type=int, help="Generate sample metrics")
    parser.add_argument("--config", help="Configuration file path")

    args = parser.parse_args()

    try:
        # Create dashboard
        dashboard = VoiceCloningMetricsDashboard(args.config)

        # Generate sample data if requested
        if args.generate_samples:
            dashboard.generate_sample_metrics(args.generate_samples)
            print(f"Generated {args.generate_samples} sample metrics")

        # Run dashboard
        print(f"Starting VoiceStudio Metrics Dashboard on {args.host}:{args.port}")
        print("Press Ctrl+C to stop")

        dashboard.run_dashboard(host=args.host, port=args.port, debug=args.debug)

    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except Exception as e:
        print(f"Error running dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
