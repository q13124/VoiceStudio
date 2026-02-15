from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from tools.context.core.manager import ContextManager
from tools.context.core.models import AllocationContext, ContextLevel

# Force UTF-8 output on Windows to handle Unicode characters
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="context-allocate",
        description="Allocate a context bundle for a role/task",
    )
    parser.add_argument("--role", help="Role short name (e.g., core-platform)")
    parser.add_argument("--task", help="Task id (e.g., TASK-0001)")
    parser.add_argument("--phase", help="Phase name")
    parser.add_argument("--budget", type=int, default=None, help="Total budget chars override")
    parser.add_argument("--include-git", action="store_true", help="Include git context")
    parser.add_argument("--preamble", action="store_true", help="Output markdown preamble instead of JSON")
    parser.add_argument("--part", action="store_true", help="Output P.A.R.T. structured format")
    parser.add_argument("--level", choices=["high", "mid", "low"], default="mid",
                        help="Context level (high=minimal, mid=normal, low=all)")
    parser.add_argument("--config", help="Config path (default tools/context/config/context-sources.json)")
    args = parser.parse_args(argv)

    config_path = Path(args.config) if args.config else Path("tools/context/config/context-sources.json")
    manager = ContextManager.from_config(config_path)
    budget = args.budget if args.budget is not None else manager.config.get("budgets", {}).get("total_chars", 12000)

    # Parse max_level
    level_map = {"high": ContextLevel.HIGH, "mid": ContextLevel.MID, "low": ContextLevel.LOW}
    max_level = level_map[args.level]

    bundle = manager.allocate(
        AllocationContext(
            task_id=args.task,
            phase=args.phase,
            role=args.role,
            include_git=bool(args.include_git),
            budget_chars=int(budget),
            max_level=max_level,
        )
    )

    if args.part:
        print(bundle.to_part_markdown())
    elif args.preamble:
        print(bundle.to_preamble_markdown())
    else:
        print(bundle.to_json())
    return 0


if __name__ == "__main__":
    sys.exit(main())
