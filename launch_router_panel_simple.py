#!/usr/bin/env python3
"""
VoiceStudio PySide6 Router Panel (Simple) Launcher
Launches the lightweight desktop GUI for VoiceStudio Router
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication
    from app.ui.panels.router_panel_simple import RouterPanel
except ImportError as e:
    print(f"Error importing PySide6: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)


def main():
    """Launch the VoiceStudio Router Panel (Simple)"""
    app = QApplication(sys.argv)
    app.setApplicationName("VoiceStudio Router Panel (Simple)")
    app.setApplicationVersion("1.0.0")

    # Create and show the router panel
    panel = RouterPanel(base_url="http://127.0.0.1:5090")
    panel.show()

    print("VoiceStudio Router Panel (Simple) launched!")
    print("Make sure the VoiceStudio router is running on http://127.0.0.1:5090")
    print("Features: Sync/Async TTS, Engine monitoring, Audio playback (polling only)")

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
