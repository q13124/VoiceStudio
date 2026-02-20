"""
REAL functional test - traces every workflow with the Allan Watts asset.
Not checking if elements exist. Testing if things ACTUALLY WORK.
"""

from __future__ import annotations

import json
import os
import struct
import tempfile

import requests

BASE = "http://127.0.0.1:8001"
ASSET_ID = "305cdf87-73a1-4271-8ae1-3d9407ad51c1"
ALLAN_WATTS_FILE = r"C:\Users\Tyler\Downloads\Allan Watts.m4a"

results = {}


def test(name, fn):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    try:
        result = fn()
        results[name] = result
        return result
    except Exception as e:
        print(f"  EXCEPTION: {type(e).__name__}: {e}")
        results[name] = {"status": "EXCEPTION", "error": str(e)}
        return None


def t01_backend_health():
    r = requests.get(f"{BASE}/api/health", timeout=5)
    status = r.json().get("status", "unknown")
    print(f"  Status: {r.status_code} -> {status}")
    works = r.status_code == 200 and status == "ok"
    return {"status_code": r.status_code, "works": works, "healthy": status == "ok"}


def t02_library_list():
    r = requests.get(f"{BASE}/api/library/assets", timeout=10)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        assets = data.get("assets", data.get("items", data if isinstance(data, list) else []))
        print(f"  Assets returned: {len(assets)}")
        if assets and isinstance(assets[0], dict):
            print(f"  First: id={assets[0].get('id', '?')[:12]}... name={assets[0].get('name', '?')}")
        return {"status_code": r.status_code, "count": len(assets), "works": len(assets) > 0}
    else:
        print(f"  ERROR: {r.text[:300]}")
        return {"status_code": r.status_code, "works": False, "error": r.text[:300]}


def t03_library_search():
    r = requests.get(f"{BASE}/api/library/assets", params={"search": "Allan Watts"}, timeout=10)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        assets = data.get("assets", data.get("items", data if isinstance(data, list) else []))
        print(f"  Search results: {len(assets)}")
        return {"status_code": r.status_code, "count": len(assets), "works": True}
    print(f"  ERROR: {r.text[:300]}")
    return {"status_code": r.status_code, "works": False}


def t04_get_specific_asset():
    r = requests.get(f"{BASE}/api/library/assets/{ASSET_ID}", timeout=10)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Asset data: {json.dumps(data, indent=2)[:500]}")
        return {"status_code": r.status_code, "works": True, "data": data}
    print(f"  ERROR: {r.text[:300]}")
    return {"status_code": r.status_code, "works": False, "error": r.text[:300]}


def t05_upload_real_file():
    """Try uploading the actual Allan Watts file."""
    if not os.path.exists(ALLAN_WATTS_FILE):
        print(f"  SKIP: File not found: {ALLAN_WATTS_FILE}")
        return {"works": False, "error": "file not found"}

    print(f"  Uploading: {ALLAN_WATTS_FILE}")
    with open(ALLAN_WATTS_FILE, "rb") as f:
        # Correct endpoint is /api/library/assets/upload with file upload
        r = requests.post(
            f"{BASE}/api/library/assets/upload",
            files={"file": ("Allan Watts.m4a", f, "audio/x-m4a")},
            data={"tags": "allan watts,audio,test"},
            timeout=60,
        )
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.text[:500]}")
    return {"status_code": r.status_code, "works": r.status_code in (200, 201), "response": r.text[:500]}


def t06_list_engines():
    r = requests.get(f"{BASE}/api/v3/engines", timeout=10)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            print(f"  Engines: {len(data)}")
            for e in data[:5]:
                name = e.get("name", e.get("id", "?")) if isinstance(e, dict) else str(e)
                print(f"    - {name}")
        elif isinstance(data, dict):
            engines = data.get("engines", data.get("items", []))
            print(f"  Engines: {len(engines)}")
            for e in engines[:5]:
                name = e.get("name", e.get("id", "?")) if isinstance(e, dict) else str(e)
                print(f"    - {name}")
        return {"status_code": r.status_code, "works": True}
    print(f"  ERROR: {r.text[:300]}")
    return {"status_code": r.status_code, "works": False}


def t07_voice_profiles():
    # Correct endpoint is /api/profiles (not /api/voice/profiles)
    r = requests.get(f"{BASE}/api/profiles", timeout=10)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        profiles = data if isinstance(data, list) else data.get("profiles", data.get("items", []))
        print(f"  Profiles: {len(profiles)}")
        for p in profiles[:5]:
            if isinstance(p, dict):
                print(f"    - {p.get('name', p.get('id', '?'))}")
        return {"status_code": r.status_code, "count": len(profiles), "works": True, "profiles": profiles}
    print(f"  ERROR: {r.text[:300]}")
    return {"status_code": r.status_code, "works": False}


def t08_transcription_submit():
    # Correct endpoint is /api/transcribe/ (not /api/transcribe/submit)
    # Correct field is audio_id (not asset_id)
    # Use "whisper" engine (faster_whisper) instead of "whisper_cpp" which requires whisper-cpp-python
    r = requests.post(
        f"{BASE}/api/transcribe/",
        json={"audio_id": ASSET_ID, "engine": "whisper", "language": "en"},
        timeout=300,  # Transcription can take time for longer audio files
    )
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.text[:500]}")
    return {"status_code": r.status_code, "works": r.status_code in (200, 201, 202), "response": r.text[:500]}


def t09_synthesis_submit():
    # First get a profile_id from the profiles endpoint
    profiles_resp = requests.get(f"{BASE}/api/profiles", timeout=10)
    profile_id = None
    if profiles_resp.status_code == 200:
        data = profiles_resp.json()
        profiles = data if isinstance(data, list) else data.get("profiles", data.get("items", []))
        if profiles and isinstance(profiles[0], dict):
            profile_id = profiles[0].get("id") or profiles[0].get("profile_id")
            print(f"  Using profile: {profile_id}")

    if not profile_id:
        print("  SKIP: No profiles available, cannot test synthesis")
        return {"status_code": 0, "works": False, "error": "no profiles available"}

    # profile_id is REQUIRED for synthesis
    # Don't specify engine - let backend use its fallback chain (XTTS -> Piper -> eSpeak -> gTTS -> pyttsx3)
    r = requests.post(
        f"{BASE}/api/voice/synthesize",
        json={
            "text": "Hello world, this is a test of voice synthesis.",
            "profile_id": profile_id,
            # engine not specified - use backend default with fallback
        },
        timeout=60,  # Increased timeout for fallback attempts
    )
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.text[:500]}")
    return {"status_code": r.status_code, "works": r.status_code in (200, 201, 202), "response": r.text[:500]}


def t10_voice_clone():
    # Clone endpoint requires multipart form-data with file upload, NOT JSON
    # reference_audio: list[UploadFile] = File(...)
    if not os.path.exists(ALLAN_WATTS_FILE):
        print(f"  SKIP: File not found: {ALLAN_WATTS_FILE}")
        return {"works": False, "error": "file not found"}

    print(f"  Cloning voice from: {ALLAN_WATTS_FILE}")
    with open(ALLAN_WATTS_FILE, "rb") as f:
        r = requests.post(
            f"{BASE}/api/voice/clone",
            files={"reference_audio": ("Allan Watts.m4a", f, "audio/x-m4a")},
            data={
                "engine": "xtts",
                "quality_mode": "standard",
                "profile_name": "Allan Watts Clone Test",
            },
            timeout=60,
        )
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.text[:500]}")
    return {"status_code": r.status_code, "works": r.status_code in (200, 201, 202), "response": r.text[:500]}


def t11_audio_formats():
    r = requests.get(f"{BASE}/api/audio/formats", timeout=10)
    print(f"  Status: {r.status_code}")
    print(f"  Response: {r.text[:500]}")
    return {"status_code": r.status_code, "works": r.status_code == 200}


def t12_convert_asset():
    """Try to convert the Allan Watts asset to WAV using audio export endpoint.

    Note: /api/rvc/convert is for RVC *voice* conversion (changing voice characteristics),
    NOT audio format conversion. For format conversion, use /api/audio/export.
    """
    # Use /api/audio/export for audio format conversion
    # Use stream=True to avoid downloading the entire audio file (can be 500MB+)
    r = requests.post(
        f"{BASE}/api/audio/export",
        json={"source": ASSET_ID, "format": "wav"},
        timeout=30,
        stream=True,  # Don't download body, just check headers
    )
    print(f"  Audio export status: {r.status_code}")
    if r.status_code in (200, 201, 202):
        content_type = r.headers.get("Content-Type", "unknown")
        content_length = r.headers.get("Content-Length", "unknown")
        print(f"  Content-Type: {content_type}, Size: {content_length} bytes")
        r.close()  # Close connection without downloading body
        return {"status_code": r.status_code, "works": True, "endpoint": "audio/export"}

    # If export fails, show the error and list available formats
    print(f"  Export error: {r.text[:300]}")
    r2 = requests.get(f"{BASE}/api/audio/formats", timeout=10)
    print(f"  Audio formats status: {r2.status_code}")
    if r2.status_code == 200:
        print(f"  Available formats: {r2.text[:300]}")

    return {
        "status_code": r.status_code,
        "works": False,
        "note": "Audio export failed - check source ID and format",
    }


def t13_all_routes():
    """List all registered API routes to find what actually exists."""
    r = requests.get(f"{BASE}/openapi.json", timeout=10)
    if r.status_code == 200:
        spec = r.json()
        paths = sorted(spec.get("paths", {}).keys())
        print(f"  Total endpoints: {len(paths)}")
        for p in paths:
            methods = [m.upper() for m in spec["paths"][p] if m != "parameters"]
            print(f"    {','.join(methods):12s} {p}")
        return {"status_code": 200, "works": True, "total": len(paths), "paths": paths}
    print(f"  ERROR: {r.status_code}")
    return {"status_code": r.status_code, "works": False}


if __name__ == "__main__":
    print("=" * 60)
    print("REAL FUNCTIONAL TEST - Allan Watts End-to-End")
    print("=" * 60)

    test("01_backend_health", t01_backend_health)
    test("02_library_list", t02_library_list)
    test("03_library_search", t03_library_search)
    test("04_get_specific_asset", t04_get_specific_asset)
    test("05_upload_real_file", t05_upload_real_file)
    test("06_list_engines", t06_list_engines)
    test("07_voice_profiles", t07_voice_profiles)
    test("08_transcription_submit", t08_transcription_submit)
    test("09_synthesis_submit", t09_synthesis_submit)
    test("10_voice_clone", t10_voice_clone)
    test("11_audio_formats", t11_audio_formats)
    test("12_convert_asset", t12_convert_asset)
    test("13_all_routes", t13_all_routes)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, result in results.items():
        if result is None:
            status = "EXCEPTION"
        elif isinstance(result, dict):
            works = result.get("works", False)
            code = result.get("status_code", "?")
            status = f"{'WORKS' if works else 'BROKEN'} (HTTP {code})"
        else:
            status = str(result)
        print(f"  {name:35s} {status}")
