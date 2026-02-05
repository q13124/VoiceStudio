#!/usr/bin/env python3
"""
Export OpenAPI Schema Script
Exports the FastAPI OpenAPI schema to docs/api/openapi.json

Usage:
    python scripts/export_openapi_schema.py
    python scripts/export_openapi_schema.py --output path/to/openapi.json
"""

import argparse
import json
import sys
from pathlib import Path

from _env_setup import PROJECT_ROOT
# Backend path already in sys.path via _env_setup


def main():
    parser = argparse.ArgumentParser(description="Export OpenAPI schema from FastAPI app")
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path (default: docs/api/openapi.json)"
    )
    args = parser.parse_args()

    try:
        from backend.api.main import app

        # Generate OpenAPI schema
        openapi_schema = app.openapi()

        # Determine output path
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = PROJECT_ROOT / "docs" / "api" / "openapi.json"

        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Write schema to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

        print(f"[OK] OpenAPI schema exported to {output_file}")
        print(
            f"   Schema version: {openapi_schema.get('info', {}).get('version', 'unknown')}"
        )
        print(f"   Total paths: {len(openapi_schema.get('paths', {}))}")

        return 0

    except Exception as e:
        print(f"[ERROR] Error exporting OpenAPI schema: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
