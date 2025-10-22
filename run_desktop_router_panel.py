"""
Launcher for the PySide6 Router Panel.
"""

from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from app.ui.panels.router_panel import RouterPanel

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5090"
    app = QApplication(sys.argv)
    w = RouterPanel(base_url=base)
    w.resize(1200, 800)
    w.show()
    sys.exit(app.exec())
