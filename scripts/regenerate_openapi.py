#!/usr/bin/env python3
"""
Regenerate OpenAPI Specification from FastAPI App

This script exports the full OpenAPI specification from the FastAPI application,
including all registered routers and their endpoints.

Usage:
    python scripts/regenerate_openapi.py
    python scripts/regenerate_openapi.py --output docs/api/openapi.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def regenerate_openapi(output_path: str = "docs/api/openapi.json") -> None:
    """
    Regenerate the OpenAPI specification from the FastAPI app.
    
    Args:
        output_path: Path to write the OpenAPI JSON file
    """
    try:
        from backend.api.main import app
        
        # Get the OpenAPI schema
        openapi_schema = app.openapi()
        
        # Ensure output directory exists
        output_file = project_root / output_path
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the schema
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
        
        # Count endpoints
        paths = openapi_schema.get("paths", {})
        endpoint_count = sum(
            len([m for m in methods.keys() if m != "parameters"])
            for methods in paths.values()
        )
        
        print(f"OpenAPI specification regenerated successfully!")
        print(f"  Output: {output_file}")
        print(f"  Paths: {len(paths)}")
        print(f"  Endpoints: {endpoint_count}")
        print(f"  Version: {openapi_schema.get('info', {}).get('version', 'unknown')}")
        
        # List some key endpoint groups
        prefixes = {}
        for path in paths.keys():
            parts = path.split("/")
            if len(parts) > 2:
                prefix = f"/{parts[1]}/{parts[2]}" if parts[1] == "api" else f"/{parts[1]}"
                prefixes[prefix] = prefixes.get(prefix, 0) + 1
        
        print(f"\nEndpoint groups:")
        for prefix, count in sorted(prefixes.items(), key=lambda x: -x[1])[:20]:
            print(f"  {prefix}: {count} endpoints")
        
    except ImportError as e:
        print(f"Error importing FastAPI app: {e}")
        print("Make sure you're running from the project root with all dependencies installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error regenerating OpenAPI spec: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate OpenAPI specification from FastAPI app"
    )
    parser.add_argument(
        "--output", "-o",
        default="docs/api/openapi.json",
        help="Output path for the OpenAPI JSON file (default: docs/api/openapi.json)"
    )
    
    args = parser.parse_args()
    regenerate_openapi(args.output)


if __name__ == "__main__":
    main()
