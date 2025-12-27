#!/usr/bin/env python3
"""
Export OpenAPI Schema Script
Exports the FastAPI OpenAPI schema to docs/api/openapi.json
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

try:
    from backend.api.main import app

    # Generate OpenAPI schema
    openapi_schema = app.openapi()

    # Ensure docs/api directory exists
    output_dir = project_root / "docs" / "api"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write schema to file
    output_file = output_dir / "openapi.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

    print(f"[OK] OpenAPI schema exported to {output_file}")
    print(
        f"   Schema version: {openapi_schema.get('info', {}).get('version', 'unknown')}"
    )
    print(f"   Total paths: {len(openapi_schema.get('paths', {}))}")

    sys.exit(0)
except Exception as e:
    print(f"[ERROR] Error exporting OpenAPI schema: {e}", file=sys.stderr)
    import traceback

    traceback.print_exc()
    sys.exit(1)
