"""
Marketplace Panel (skeleton)
PySide6 UI stub that lists downloadable voices with preview and rating.
This file avoids import errors if PySide6 is not installed by guarding imports.
"""

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
except Exception:  # pragma: no cover - guard for environments without PySide6
    QWidget = object
    def QVBoxLayout(): return None
    def QLabel(*a, **k): return None
    def QPushButton(*a, **k): return None
    def QListWidget(): return None
    def QListWidgetItem(*a, **k): return None

class MarketplacePanel(QWidget):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
        except Exception:
            # When QWidget is object (no PySide6), skip UI setup
            return
        self.setObjectName("MarketplacePanel")
        self.setMinimumSize(640, 480)
        layout = QVBoxLayout()
        title = QLabel("Community Voices Marketplace (Preview)")
        self.listing = QListWidget()
        refresh = QPushButton("Refresh")
        layout.addWidget(title)
        layout.addWidget(self.listing)
        layout.addWidget(refresh)
        self.setLayout(layout)

    # Placeholder API; your app can wire real data here
    def populate_items(self, voices):
        if not self.listing:
            return
        self.listing.clear()
        for v in voices:
            item = QListWidgetItem(f"{v.get('name','(unnamed)')} — ⭐ {v.get('rating', 'N/A')}")
            self.listing.addItem(item)
