#!/usr/bin/env python3
"""
Quality Trends Dashboard

CLI-based quality trends visualization with historical tracking.
Stores scorecard data in SQLite for trend analysis.

Usage:
    python -m tools.quality.dashboard
    python -m tools.quality.dashboard --period 30d
    python -m tools.quality.dashboard --export html
    python -m tools.quality.dashboard ingest  # Import latest scorecard

Features:
- Store historical scorecard data in SQLite
- Display trend charts (ASCII/Unicode) in terminal
- Show week-over-week quality changes
- Identify degradation alerts
"""

import argparse
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Directories
VOICESTUDIO_DIR = PROJECT_ROOT / ".voicestudio"
QUALITY_DIR = PROJECT_ROOT / ".buildlogs" / "quality"

# Database location
DB_PATH = VOICESTUDIO_DIR / "quality_trends.db"


@dataclass
class QualitySnapshot:
    """A point-in-time quality measurement."""
    id: Optional[int]
    timestamp: datetime
    overall_score: float
    gate_score: float
    coverage_score: float
    build_score: float
    debt_score: float
    doc_score: float
    security_score: float
    
    def to_tuple(self) -> Tuple:
        return (
            self.timestamp.isoformat(),
            self.overall_score,
            self.gate_score,
            self.coverage_score,
            self.build_score,
            self.debt_score,
            self.doc_score,
            self.security_score,
        )


class QualityDatabase:
    """SQLite database for quality trend storage."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    gate_score REAL DEFAULT 0,
                    coverage_score REAL DEFAULT 0,
                    build_score REAL DEFAULT 0,
                    debt_score REAL DEFAULT 0,
                    doc_score REAL DEFAULT 0,
                    security_score REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp 
                ON quality_snapshots(timestamp)
            """)
            conn.commit()
    
    def insert_snapshot(self, snapshot: QualitySnapshot):
        """Insert a quality snapshot."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO quality_snapshots 
                (timestamp, overall_score, gate_score, coverage_score, 
                 build_score, debt_score, doc_score, security_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, snapshot.to_tuple())
            conn.commit()
    
    def get_snapshots(self, days: int = 30) -> List[QualitySnapshot]:
        """Get snapshots from the last N days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, timestamp, overall_score, gate_score, coverage_score,
                       build_score, debt_score, doc_score, security_score
                FROM quality_snapshots
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            """, (cutoff,))
            
            snapshots = []
            for row in cursor.fetchall():
                snapshots.append(QualitySnapshot(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    overall_score=row[2],
                    gate_score=row[3],
                    coverage_score=row[4],
                    build_score=row[5],
                    debt_score=row[6],
                    doc_score=row[7],
                    security_score=row[8],
                ))
            
            return snapshots
    
    def get_latest(self) -> Optional[QualitySnapshot]:
        """Get the most recent snapshot."""
        snapshots = self.get_snapshots(days=365)
        return snapshots[-1] if snapshots else None
    
    def get_week_ago(self) -> Optional[QualitySnapshot]:
        """Get snapshot from approximately 7 days ago."""
        target = datetime.now() - timedelta(days=7)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, timestamp, overall_score, gate_score, coverage_score,
                       build_score, debt_score, doc_score, security_score
                FROM quality_snapshots
                WHERE timestamp <= ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (target.isoformat(),))
            
            row = cursor.fetchone()
            if row:
                return QualitySnapshot(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    overall_score=row[2],
                    gate_score=row[3],
                    coverage_score=row[4],
                    build_score=row[5],
                    debt_score=row[6],
                    doc_score=row[7],
                    security_score=row[8],
                )
            return None


def ingest_scorecard(scorecard_path: Optional[Path] = None) -> Optional[QualitySnapshot]:
    """Ingest a scorecard JSON file into the database."""
    if scorecard_path is None:
        # Find the latest scorecard
        if not QUALITY_DIR.exists():
            print(f"Error: Quality directory not found: {QUALITY_DIR}")
            return None
        
        scorecards = sorted(QUALITY_DIR.glob("scorecard_*.json"), reverse=True)
        if not scorecards:
            print("Error: No scorecard files found")
            return None
        
        scorecard_path = scorecards[0]
    
    try:
        data = json.loads(scorecard_path.read_text())
        
        dimensions = data.get("dimensions", {})
        
        snapshot = QualitySnapshot(
            id=None,
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            overall_score=data.get("overall_score", 0),
            gate_score=dimensions.get("gates", {}).get("score", 0),
            coverage_score=dimensions.get("coverage", {}).get("score", 0),
            build_score=dimensions.get("build", {}).get("score", 0),
            debt_score=dimensions.get("debt", {}).get("score", 0),
            doc_score=dimensions.get("docs", {}).get("score", 0),
            security_score=dimensions.get("security", {}).get("score", 0),
        )
        
        db = QualityDatabase()
        db.insert_snapshot(snapshot)
        
        print(f"Ingested scorecard: {scorecard_path.name}")
        print(f"Overall score: {snapshot.overall_score:.1f}")
        
        return snapshot
        
    except Exception as e:
        print(f"Error ingesting scorecard: {e}")
        return None


def draw_ascii_chart(snapshots: List[QualitySnapshot], width: int = 60, height: int = 15) -> str:
    """Draw a simple ASCII chart of quality scores over time."""
    if not snapshots:
        return "No data available"
    
    scores = [s.overall_score for s in snapshots]
    min_score = max(0, min(scores) - 5)
    max_score = min(100, max(scores) + 5)
    score_range = max_score - min_score
    
    if score_range == 0:
        score_range = 10
    
    lines = []
    
    # Header
    lines.append("Quality Score Trend")
    lines.append("-" * width)
    
    # Chart area
    chart_width = width - 8  # Leave room for Y-axis labels
    
    # Resample to fit width if needed
    if len(scores) > chart_width:
        step = len(scores) / chart_width
        sampled_scores = [scores[int(i * step)] for i in range(chart_width)]
    else:
        sampled_scores = scores
    
    for row in range(height - 1, -1, -1):
        threshold = min_score + (row / (height - 1)) * score_range
        
        # Y-axis label
        if row == height - 1:
            label = f"{max_score:5.0f}|"
        elif row == 0:
            label = f"{min_score:5.0f}|"
        elif row == height // 2:
            mid = (min_score + max_score) / 2
            label = f"{mid:5.0f}|"
        else:
            label = "     |"
        
        # Chart points
        chart_line = ""
        for score in sampled_scores:
            if score >= threshold:
                chart_line += "█"
            else:
                chart_line += " "
        
        lines.append(label + chart_line)
    
    # X-axis
    lines.append("     +" + "-" * len(sampled_scores))
    
    # Date labels
    if snapshots:
        start_date = snapshots[0].timestamp.strftime("%m/%d")
        end_date = snapshots[-1].timestamp.strftime("%m/%d")
        padding = len(sampled_scores) - len(start_date) - len(end_date)
        lines.append(f"      {start_date}{' ' * padding}{end_date}")
    
    return "\n".join(lines)


def format_delta(current: float, previous: Optional[float]) -> str:
    """Format a score delta with arrow."""
    if previous is None:
        return "  --  "
    
    delta = current - previous
    if delta > 0.5:
        return f" ↑{delta:+.1f}"
    elif delta < -0.5:
        return f" ↓{delta:+.1f}"
    else:
        return "  →   "


def display_dashboard(days: int = 30):
    """Display the quality dashboard."""
    db = QualityDatabase()
    snapshots = db.get_snapshots(days=days)
    
    print("=" * 70)
    print("              VoiceStudio Quality Dashboard")
    print("=" * 70)
    print()
    
    if not snapshots:
        print("No quality data available.")
        print()
        print("To add data, run:")
        print("  python scripts/quality_scorecard.py")
        print("  python -m tools.quality.dashboard ingest")
        return
    
    # Current status
    latest = snapshots[-1]
    week_ago = db.get_week_ago()
    
    print(f"Latest measurement: {latest.timestamp.strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Grade calculation
    def grade(score: float) -> str:
        if score >= 95: return "A+"
        if score >= 90: return "A"
        if score >= 85: return "B+"
        if score >= 80: return "B"
        if score >= 75: return "C+"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"
    
    print(f"  Overall Score: {latest.overall_score:5.1f}  ({grade(latest.overall_score)})"
          f"{format_delta(latest.overall_score, week_ago.overall_score if week_ago else None)}")
    print()
    
    # Dimension breakdown
    print("-" * 70)
    print("  Dimension      Score   7d Change   Status")
    print("-" * 70)
    
    dimensions = [
        ("Gates", latest.gate_score, week_ago.gate_score if week_ago else None),
        ("Coverage", latest.coverage_score, week_ago.coverage_score if week_ago else None),
        ("Build", latest.build_score, week_ago.build_score if week_ago else None),
        ("Tech Debt", latest.debt_score, week_ago.debt_score if week_ago else None),
        ("Documentation", latest.doc_score, week_ago.doc_score if week_ago else None),
        ("Security", latest.security_score, week_ago.security_score if week_ago else None),
    ]
    
    for name, score, prev_score in dimensions:
        delta_str = format_delta(score, prev_score)
        status = "OK" if score >= 70 else "LOW" if score >= 50 else "CRITICAL"
        print(f"  {name:14} {score:5.1f}   {delta_str:10}   [{status}]")
    
    print("-" * 70)
    print()
    
    # Trend chart
    if len(snapshots) >= 2:
        print(draw_ascii_chart(snapshots))
        print()
    
    # Alerts
    alerts = []
    if latest.overall_score < 70:
        alerts.append("⚠️  Overall quality score is below 70")
    if week_ago and (latest.overall_score - week_ago.overall_score) < -5:
        alerts.append("⚠️  Quality dropped more than 5 points in the last week")
    if latest.gate_score < 100:
        alerts.append("⚠️  Not all gates are passing")
    
    if alerts:
        print("Alerts:")
        for alert in alerts:
            print(f"  {alert}")
        print()


def export_html(days: int = 30) -> str:
    """Export dashboard as HTML."""
    db = QualityDatabase()
    snapshots = db.get_snapshots(days=days)
    
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<title>VoiceStudio Quality Dashboard</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; margin: 20px; }",
        "table { border-collapse: collapse; }",
        "th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }",
        "th { background: #4CAF50; color: white; }",
        ".good { color: green; }",
        ".warn { color: orange; }",
        ".bad { color: red; }",
        "</style>",
        "</head>",
        "<body>",
        "<h1>VoiceStudio Quality Dashboard</h1>",
        f"<p>Generated: {datetime.now().isoformat()}</p>",
    ]
    
    if snapshots:
        latest = snapshots[-1]
        html_parts.extend([
            f"<h2>Overall Score: {latest.overall_score:.1f}</h2>",
            "<table>",
            "<tr><th>Dimension</th><th>Score</th></tr>",
            f"<tr><td>Gates</td><td>{latest.gate_score:.1f}</td></tr>",
            f"<tr><td>Coverage</td><td>{latest.coverage_score:.1f}</td></tr>",
            f"<tr><td>Build</td><td>{latest.build_score:.1f}</td></tr>",
            f"<tr><td>Tech Debt</td><td>{latest.debt_score:.1f}</td></tr>",
            f"<tr><td>Documentation</td><td>{latest.doc_score:.1f}</td></tr>",
            f"<tr><td>Security</td><td>{latest.security_score:.1f}</td></tr>",
            "</table>",
            "<h3>History</h3>",
            "<table>",
            "<tr><th>Date</th><th>Score</th></tr>",
        ])
        
        for s in snapshots[-30:]:  # Last 30 entries
            html_parts.append(
                f"<tr><td>{s.timestamp.strftime('%Y-%m-%d')}</td>"
                f"<td>{s.overall_score:.1f}</td></tr>"
            )
        
        html_parts.append("</table>")
    else:
        html_parts.append("<p>No data available</p>")
    
    html_parts.extend(["</body>", "</html>"])
    
    return "\n".join(html_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Quality Trends Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  (default)  Display the dashboard
  ingest     Import the latest scorecard into the database

Examples:
  python -m tools.quality.dashboard
  python -m tools.quality.dashboard --period 7d
  python -m tools.quality.dashboard ingest
  python -m tools.quality.dashboard --export html > report.html
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        default="display",
        choices=["display", "ingest"],
        help="Command to run (default: display)"
    )
    parser.add_argument(
        "--period",
        type=str,
        default="30d",
        help="Time period for trends (e.g., 7d, 30d, 90d)"
    )
    parser.add_argument(
        "--export",
        choices=["html"],
        help="Export format"
    )
    parser.add_argument(
        "--scorecard",
        type=str,
        help="Specific scorecard file to ingest"
    )
    
    args = parser.parse_args()
    
    # Parse period
    period_match = args.period.lower()
    if period_match.endswith("d"):
        days = int(period_match[:-1])
    else:
        days = int(period_match)
    
    if args.command == "ingest":
        scorecard_path = Path(args.scorecard) if args.scorecard else None
        ingest_scorecard(scorecard_path)
    elif args.export == "html":
        print(export_html(days))
    else:
        display_dashboard(days)


if __name__ == "__main__":
    main()
