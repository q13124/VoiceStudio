"""
Overseer Issue System configuration.

Central configurable parameters for storage, pattern matching,
risk assessment, and recommendation confidence.
"""

import os
from pathlib import Path

# Storage
_default_log_dir = (
    Path(os.environ.get("APPDATA", os.path.expanduser("~")))
    / "VoiceStudio"
    / "logs"
    / "overseer_issues"
)
ISSUES_LOG_DIR = Path(
    os.environ.get("VOICESTUDIO_ISSUES_LOG_DIR", str(_default_log_dir))
)
MAX_FILE_SIZE_MB = 100
RETENTION_DAYS = 90
DAILY_ROTATION = True
# Compress rotated log files to .jsonl.gz after this many days (0 = disable)
COMPRESS_AFTER_DAYS = 1

# Pattern matching
PATTERN_SIMILARITY_THRESHOLD = 0.7
MAX_LEARNED_PATTERNS = 1000

# Risk assessment weights (must sum to 1.0 for normalized score)
FREQUENCY_WEIGHT = 0.4
BLAST_RADIUS_WEIGHT = 0.3
SEVERITY_WEIGHT = 0.3

# Recommendation confidence thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.8
MEDIUM_CONFIDENCE_THRESHOLD = 0.6

# Recommendation feedback (outcome tracking for calibration)
RECOMMENDATION_FEEDBACK_FILENAME = "recommendation_feedback.jsonl"
