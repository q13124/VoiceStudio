#!/usr/bin/env python3
"""
Export OpenAPI Specification

This script exports the OpenAPI specification from a running VoiceStudio backend server.
"""

import json
import sys
from pathlib import Path

import requests

# Default server URL
DEFAULT_SERVER_URL = "http://localhost:8000"
DEFAULT_OUTPUT_FILE = "openapi.json"


def export_openapi_spec(server_url: str = DEFAULT_SERVER_URL, output_file: str = None):
    """
    Export OpenAPI specification from running server.

    Args:
        server_url: Base URL of the backend server
        output_file: Output file path (default: openapi.json in current directory)
    """
    openapi_url = f"{server_url}/openapi.json"

    print(f"Fetching OpenAPI spec from {openapi_url}...")

    try:
        response = requests.get(openapi_url, timeout=10)
        response.raise_for_status()

        spec = response.json()

        # Determine output file
        if output_file is None:
            output_file = DEFAULT_OUTPUT_FILE

        output_path = Path(output_file)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)

        print(f"✅ OpenAPI spec exported to: {output_path.absolute()}")
        print(f"   Total endpoints: {len(spec.get('paths', {}))}")
        print(f"   OpenAPI version: {spec.get('openapi', 'unknown')}")

        # Print summary
        if "tags" in spec:
            print(f"\n📋 Endpoint Categories ({len(spec['tags'])}):")
            for tag in spec["tags"]:
                name = tag.get("name", "unknown")
                description = tag.get("description", "")
                print(f"   • {name}: {description}")

        return output_path

    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {server_url}")
        print("   Make sure the backend server is running.")
        print("   Start it with: cd backend && python -m api.main")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"❌ Error: Request to {server_url} timed out")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error: HTTP {e.response.status_code}")
        print(f"   {e.response.text}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON response: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def validate_openapi_spec(spec_file: str):
    """
    Validate OpenAPI specification file.

    Args:
        spec_file: Path to OpenAPI spec file
    """
    try:
        import jsonschema

        # Load OpenAPI spec
        with open(spec_file, "r", encoding="utf-8") as f:
            spec = json.load(f)

        # Basic validation
        required_fields = ["openapi", "info", "paths"]
        missing_fields = [field for field in required_fields if field not in spec]

        if missing_fields:
            print(f"❌ Invalid OpenAPI spec: Missing fields: {missing_fields}")
            return False

        # Check OpenAPI version
        openapi_version = spec.get("openapi", "")
        if not openapi_version.startswith("3."):
            print(f"⚠️  Warning: OpenAPI version is {openapi_version}, expected 3.x")

        print(f"✅ OpenAPI spec is valid")
        print(f"   Version: {openapi_version}")
        print(f"   Title: {spec.get('info', {}).get('title', 'Unknown')}")
        print(f"   Endpoints: {len(spec.get('paths', {}))}")

        return True

    except ImportError:
        print("⚠️  Warning: jsonschema not installed, skipping validation")
        print("   Install with: pip install jsonschema")
        return None
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Export OpenAPI specification from VoiceStudio backend"
    )
    parser.add_argument(
        "--server-url",
        default=DEFAULT_SERVER_URL,
        help=f"Backend server URL (default: {DEFAULT_SERVER_URL})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"Output file path (default: {DEFAULT_OUTPUT_FILE})",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate the exported OpenAPI spec"
    )

    args = parser.parse_args()

    # Export spec
    output_path = export_openapi_spec(args.server_url, args.output)

    # Validate if requested
    if args.validate:
        print("\n🔍 Validating OpenAPI spec...")
        validate_openapi_spec(str(output_path))


if __name__ == "__main__":
    main()
