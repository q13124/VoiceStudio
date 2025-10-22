# workers/metrics_dashboard_worker.py
# Metrics dashboard worker for VoiceStudio

import os
import sys
import json
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_metrics_dashboard import VoiceCloningMetricsDashboard, MetricType, QualityLevel, QualityMetric

class MetricsDashboardWorker:
    def __init__(self, config_path=None):
        self.config_path = config_path or "config/metrics_dashboard.json"
        self.dashboard = VoiceCloningMetricsDashboard(self.config_path)

    def add_metric(self, metric_data):
        """Add a quality metric"""
        try:
            # Create metric object
            metric = QualityMetric(
                metric_id=metric_data.get("metric_id", f"metric_{time.time()}"),
                metric_type=MetricType(metric_data["metric_type"]),
                value=float(metric_data["value"]),
                quality_level=self.determine_quality_level(float(metric_data["value"])),
                timestamp=metric_data.get("timestamp", time.time()),
                engine=metric_data["engine"],
                language=metric_data["language"],
                user_id=metric_data.get("user_id"),
                session_id=metric_data.get("session_id"),
                metadata=metric_data.get("metadata")
            )

            # Add metric
            self.dashboard.add_metric(metric)

            return {"success": True, "metric_id": metric.metric_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_metrics_summary(self, hours=24):
        """Get metrics summary"""
        try:
            recent_metrics = self.dashboard.get_recent_metrics(hours=hours)

            if not recent_metrics:
                return {"success": True, "summary": {"total_metrics": 0}}

            # Calculate summary
            summary = {
                "total_metrics": len(recent_metrics),
                "engines": list(set([m.engine for m in recent_metrics])),
                "languages": list(set([m.language for m in recent_metrics])),
                "metric_types": list(set([m.metric_type.value for m in recent_metrics]))
            }

            # Calculate averages
            averages = {}
            for metric_type in MetricType:
                type_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
                if type_metrics:
                    averages[metric_type.value] = {
                        "count": len(type_metrics),
                        "average": sum(m.value for m in type_metrics) / len(type_metrics)
                    }

            summary["averages"] = averages

            return {"success": True, "summary": summary}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_alerts(self, limit=50):
        """Get alerts"""
        try:
            recent_alerts = self.dashboard.alerts[-limit:] if self.dashboard.alerts else []
            return {"success": True, "alerts": recent_alerts}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def determine_quality_level(self, value):
        """Determine quality level from value"""
        if value >= 0.9:
            return QualityLevel.EXCELLENT
        elif value >= 0.8:
            return QualityLevel.GOOD
        elif value >= 0.7:
            return QualityLevel.FAIR
        elif value >= 0.6:
            return QualityLevel.POOR
        else:
            return QualityLevel.VERY_POOR

def main():
    """Main function for worker"""
    import argparse

    parser = argparse.ArgumentParser(description="VoiceStudio Metrics Dashboard Worker")
    parser.add_argument("--action", choices=["add", "summary", "alerts"], required=True,
                       help="Action to perform")
    parser.add_argument("--metric-data", help="JSON file with metric data")
    parser.add_argument("--hours", type=int, default=24, help="Hours for summary")
    parser.add_argument("--limit", type=int, default=50, help="Limit for alerts")

    args = parser.parse_args()

    worker = MetricsDashboardWorker()

    if args.action == "add":
        if not args.metric_data:
            print("Error: --metric-data required for add action")
            sys.exit(1)

        # Load metric data
        with open(args.metric_data, 'r', encoding='utf-8') as f:
            metric_data = json.load(f)

        result = worker.add_metric(metric_data)
        print(json.dumps(result))

    elif args.action == "summary":
        result = worker.get_metrics_summary(args.hours)
        print(json.dumps(result))

    elif args.action == "alerts":
        result = worker.get_alerts(args.limit)
        print(json.dumps(result))

if __name__ == "__main__":
    main()
