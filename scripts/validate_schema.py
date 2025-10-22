#!/usr/bin/env python3
"""
Local OpenAPI schema validation script
Run this to validate the schema before pushing changes
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def start_server():
    """Start the FastAPI server in background"""
    print("Starting VoiceStudio API server...")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "services.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(5)
    return proc


def fetch_schema():
    """Fetch OpenAPI schema from running server"""
    print("Fetching OpenAPI schema...")
    try:
        result = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:8000/openapi.json"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            raise Exception(f"Failed to fetch schema: {result.stderr}")

        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error fetching schema: {e}")
        return None


def validate_schema(spec):
    """Validate OpenAPI schema"""
    try:
        from openapi_spec_validator import validate_spec

        print("Validating OpenAPI 3.1 schema...")
        validate_spec(spec)
        print("✅ OpenAPI schema is valid")

        # Check version
        assert (
            spec.get("openapi") == "3.1.0"
        ), f'Expected OpenAPI 3.1.0, got {spec.get("openapi")}'
        print("✅ OpenAPI version is 3.1.0")

        # Check for required fields
        assert "info" in spec, "Missing info section"
        assert "paths" in spec, "Missing paths section"
        print("✅ Required sections present")

        # Check TTS endpoint exists
        assert "/v1/generate" in spec.get("paths", {}), "Missing /v1/generate endpoint"
        print("✅ TTS endpoint present")

        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False


def check_breaking_changes(spec):
    """Check for breaking changes in API"""
    print("Checking for breaking changes...")

    # Check that output_chain field exists in TTS request
    tts_path = spec.get("paths", {}).get("/v1/generate", {})
    post_method = tts_path.get("post", {})
    request_body = post_method.get("requestBody", {})
    content = request_body.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})
    properties = schema.get("properties", {})

    if "output_chain" not in properties:
        print("⚠️  output_chain field missing from TTS request")
    else:
        print("✅ output_chain field present")

    # Check that metrics field exists in TTS response
    responses = post_method.get("responses", {})
    success_response = responses.get("200", {})
    response_content = success_response.get("content", {})
    response_json = response_content.get("application/json", {})
    response_schema = response_json.get("schema", {})
    response_properties = response_schema.get("properties", {})
    items_property = response_properties.get("items", {})
    items_schema = items_property.get("items", {})
    item_properties = items_schema.get("properties", {})

    if "metrics" not in item_properties:
        print("⚠️  metrics field missing from TTS response items")
    else:
        print("✅ metrics field present")


def main():
    """Main validation function"""
    print("🔍 VoiceStudio OpenAPI Schema Validation")
    print("=" * 50)

    # Start server
    server_proc = start_server()

    try:
        # Fetch schema
        spec = fetch_schema()
        if not spec:
            print("❌ Failed to fetch schema")
            return 1

        # Validate schema
        if not validate_schema(spec):
            return 1

        # Check for breaking changes
        check_breaking_changes(spec)

        print("\n✅ All validations passed!")
        return 0

    finally:
        # Clean up
        print("\nStopping server...")
        server_proc.terminate()
        server_proc.wait()


if __name__ == "__main__":
    sys.exit(main())
