#!/usr/bin/env python3
"""
Overseer Automated Monitoring System
Monitors worker progress and triggers reviews intelligently
Event-driven + periodic monitoring (no spamming)
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Try to import watchdog, but don't fail if not available
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️ watchdog not installed. Install with: pip install watchdog")
    print("   Monitoring will use polling instead of file watching.")


class TaskChecklistMonitor:
    """Monitor MASTER_TASK_CHECKLIST.md for changes"""

    def __init__(self, checklist_path: Path, callback):
        self.checklist_path = checklist_path
        self.callback = callback
        self.last_hash: Optional[str] = None
        self.last_mtime: float = 0.0

    def check_for_changes(self) -> bool:
        """Check if checklist has changed. Returns True if changed."""
        if not self.checklist_path.exists():
            return False

        # Check modification time first (faster)
        current_mtime = self.checklist_path.stat().st_mtime
        if current_mtime == self.last_mtime:
            return False

        # Calculate hash of current file
        try:
            with open(self.checklist_path, "rb") as f:
                current_hash = hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"Error reading checklist: {e}")
            return False

        if current_hash != self.last_hash:
            self.last_hash = current_hash
            self.last_mtime = current_mtime
            self.callback("checklist_updated", str(self.checklist_path))
            return True

        return False


class ProgressFileMonitor:
    """Monitor worker progress files"""

    def __init__(self, progress_dir: Path, callback):
        self.progress_dir = progress_dir
        self.callback = callback
        self.known_files: Dict[str, float] = {}

    def check_for_changes(self):
        """Check for new or updated progress files"""
        if not self.progress_dir.exists():
            return

        # Check all JSON files in progress directory
        for progress_file in self.progress_dir.glob("WORKER_*.json"):
            file_path = str(progress_file)
            current_mtime = progress_file.stat().st_mtime

            if file_path not in self.known_files:
                # New file
                self.known_files[file_path] = current_mtime
                self.callback("progress_file_created", file_path)
            elif self.known_files[file_path] != current_mtime:
                # Updated file
                self.known_files[file_path] = current_mtime
                self.callback("progress_file_updated", file_path)


class OverseerMonitor:
    """Main monitoring system - Event-driven + periodic"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.checklist_path = project_root / "docs/governance/MASTER_TASK_CHECKLIST.md"
        self.progress_dir = project_root / "docs/governance/progress"
        self.reviews_dir = project_root / "docs/governance/reviews"

        # Create directories if needed
        self.progress_dir.mkdir(parents=True, exist_ok=True)
        self.reviews_dir.mkdir(parents=True, exist_ok=True)

        # Initialize monitors
        self.checklist_monitor = TaskChecklistMonitor(
            self.checklist_path, self.handle_event
        )
        self.progress_monitor = ProgressFileMonitor(
            self.progress_dir, self.handle_event
        )

        # Review timing
        self.last_quick_review = datetime.now()
        self.last_comprehensive_review = datetime.now()
        self.quick_review_interval = timedelta(hours=2)  # Every 2-4 hours
        self.comprehensive_review_interval = timedelta(hours=6)  # Every 6-8 hours

        # File watching (if available)
        self.observer: Optional[Observer] = None
        if WATCHDOG_AVAILABLE:
            self.setup_file_watching()

    def setup_file_watching(self):
        """Set up file system watching (if watchdog available)"""
        if not WATCHDOG_AVAILABLE:
            return

        class ChecklistHandler(FileSystemEventHandler):
            def __init__(self, monitor):
                self.monitor = monitor

            def on_modified(self, event):
                if event.src_path.endswith("MASTER_TASK_CHECKLIST.md"):
                    self.monitor.checklist_monitor.check_for_changes()

        class ProgressHandler(FileSystemEventHandler):
            def __init__(self, monitor):
                self.monitor = monitor

            def on_created(self, event):
                if event.src_path.endswith(".json"):
                    self.monitor.progress_monitor.check_for_changes()

            def on_modified(self, event):
                if event.src_path.endswith(".json"):
                    self.monitor.progress_monitor.check_for_changes()

        self.observer = Observer()

        # Watch checklist file
        checklist_dir = self.checklist_path.parent
        self.observer.schedule(
            ChecklistHandler(self), str(checklist_dir), recursive=False
        )

        # Watch progress directory
        self.observer.schedule(
            ProgressHandler(self), str(self.progress_dir), recursive=True
        )

    def handle_event(self, event_type: str, file_path: str):
        """Handle monitoring events"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] 📋 Event: {event_type} - {file_path}")

        if event_type == "checklist_updated":
            self.review_checklist_changes()
        elif event_type in ["progress_file_created", "progress_file_updated"]:
            self.review_worker_progress(file_path)

    def review_checklist_changes(self):
        """Review checklist changes"""
        print("🔍 Reviewing checklist changes...")
        # Analysis pending implementation
        # - Parse checklist
        # - Identify completed tasks
        # - Verify completed tasks
        # - Check for blockers
        # - Generate review report

    def review_worker_progress(self, progress_file: str):
        """Review worker progress"""
        print(f"👷 Reviewing worker progress: {progress_file}")
        try:
            with open(progress_file, "r") as f:
                progress = json.load(f)

            worker = progress.get("worker", "Unknown")
            status = progress.get("status", "unknown")
            current_task = progress.get("current_task", "None")
            blockers = progress.get("blockers", [])

            print(f"   Worker: {worker}")
            print(f"   Status: {status}")
            print(f"   Current Task: {current_task}")

            if blockers:
                print(f"   ⚠️ Blockers: {blockers}")
                # Guidance generation pending

        except Exception as e:
            print(f"   Error reading progress file: {e}")

    def quick_review(self):
        """Quick progress check (every 2-4 hours)"""
        print("🔍 Quick review...")
        # Check checklist
        self.checklist_monitor.check_for_changes()
        # Check progress files
        self.progress_monitor.check_for_changes()
        # TODO: Generate quick review report

    def comprehensive_review(self):
        """Comprehensive review (every 6-8 hours)"""
        print("🔍 Comprehensive review...")
        # Review all workers
        # Review all tasks
        # Check for quality issues
        # Balance workload
        # TODO: Generate comprehensive review report

    def generate_review_report(self, review_type: str):
        """Generate review report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reviews_dir / f"{timestamp}_{review_type}_review.md"

        report = f"""# Overseer Review Report
**Type:** {review_type}
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
[Review summary here]

## Findings
[Findings here]

## Actions Taken
[Actions here]

## Next Steps
[Next steps here]
"""

        with open(report_path, "w") as f:
            f.write(report)

        print(f"📄 Review report saved: {report_path}")

    def start(self):
        """Start monitoring"""
        print("👁️ Overseer monitoring system started")
        print(f"   Checklist: {self.checklist_path}")
        print(f"   Progress: {self.progress_dir}")
        print(f"   Reviews: {self.reviews_dir}")

        if self.observer:
            self.observer.start()
            print("   File watching: ENABLED (watchdog)")
        else:
            print("   File watching: DISABLED (using polling)")

        try:
            while True:
                now = datetime.now()

                # Quick review (every 2-4 hours)
                if now - self.last_quick_review >= self.quick_review_interval:
                    self.quick_review()
                    self.last_quick_review = now

                # Comprehensive review (every 6-8 hours)
                if (
                    now - self.last_comprehensive_review
                    >= self.comprehensive_review_interval
                ):
                    self.comprehensive_review()
                    self.generate_review_report("comprehensive")
                    self.last_comprehensive_review = now

                # Polling check (if watchdog not available)
                if not self.observer:
                    self.checklist_monitor.check_for_changes()
                    self.progress_monitor.check_for_changes()

                # Sleep for 5 minutes (not spamming)
                time.sleep(300)

        except KeyboardInterrupt:
            print("\n🛑 Stopping monitor...")
            if self.observer:
                self.observer.stop()
                self.observer.join()
            print("✅ Monitor stopped")


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent

    if not project_root.exists():
        print(f"❌ Project root not found: {project_root}")
        return 1

    monitor = OverseerMonitor(project_root)
    monitor.start()
    return 0


if __name__ == "__main__":
    exit(main())
