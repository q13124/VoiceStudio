#!/usr/bin/env python3
"""
VoiceStudio Service Starter (Windows)
Windows batch script to start VoiceStudio services.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start VoiceStudio services"""
    script_dir = Path(__file__).parent
    start_script = script_dir / "start-services.py"
    
    print("Starting VoiceStudio Services...")
    print("=" * 50)
    
    try:
        # Start the service manager
        subprocess.run([sys.executable, str(start_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting services: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServices stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
