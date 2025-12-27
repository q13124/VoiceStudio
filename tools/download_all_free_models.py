#!/usr/bin/env python3
"""
VoiceStudio Model Download Script

Downloads all free/open-source models for VoiceStudio engines.
Verifies checksums and stores models in %PROGRAMDATA%\VoiceStudio\models\

Usage:
    python tools/download_all_free_models.py                    # Download all
    python tools/download_all_free_models.py --engine piper      # Specific engine
    python tools/download_all_free_models.py --verify-only        # Verify existing
    python tools/download_all_free_models.py --update-index      # Update index
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Permissive licenses allowed for download
PERMISSIVE_LICENSES = {
    "MIT",
    "Apache-2.0",
    "BSD",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "CC-BY",
    "CC-BY-4.0",
    "CC0",
    "Public Domain",
    "LGPL-2.1",
    "LGPL-3.0",
}

# ProgramData path for Windows
PROGRAMDATA = os.getenv("PROGRAMDATA", os.path.expanduser("~"))
MODELS_BASE_DIR = Path(PROGRAMDATA) / "VoiceStudio" / "models"
ENGINES_DIR = Path(__file__).parent.parent / "engines"
INDEX_FILE = ENGINES_DIR / "models.index.json"
LOCAL_INDEX_FILE = MODELS_BASE_DIR / "models.index.json"


def calculate_sha256(file_path: Path) -> str:
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def verify_checksum(file_path: Path, expected_sha256: str) -> bool:
    """Verify file checksum matches expected value."""
    if not expected_sha256:
        logger.warning(
            f"No checksum provided for {file_path.name}, skipping verification"
        )
        return True

    actual_sha256 = calculate_sha256(file_path)
    return actual_sha256.lower() == expected_sha256.lower()


def download_file(
    url: str, destination: Path, expected_sha256: Optional[str] = None
) -> bool:
    """Download a file from URL with checksum verification."""
    logger.info(f"Downloading {url} to {destination}")

    try:
        # Create parent directory if needed
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Download with progress
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rProgress: {percent:.1f}%", end="", flush=True)

        print()  # New line after progress

        # Verify checksum if provided
        if expected_sha256:
            logger.info(f"Verifying checksum for {destination.name}")
            if verify_checksum(destination, expected_sha256):
                logger.info(f"✓ Checksum verified for {destination.name}")
                return True
            else:
                logger.error(f"✗ Checksum mismatch for {destination.name}")
                destination.unlink()  # Delete corrupted file
                return False

        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        if destination.exists():
            destination.unlink()
        return False
    except Exception as e:
        logger.error(f"Unexpected error downloading {url}: {e}")
        if destination.exists():
            destination.unlink()
        return False


def extract_archive(archive_path: Path, extract_to: Path) -> bool:
    """Extract ZIP archive to destination directory."""
    logger.info(f"Extracting {archive_path.name} to {extract_to}")

    try:
        extract_to.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)

        logger.info(f"✓ Extracted {archive_path.name}")
        return True

    except zipfile.BadZipFile:
        logger.error(f"✗ Invalid ZIP file: {archive_path}")
        return False
    except Exception as e:
        logger.error(f"✗ Failed to extract {archive_path}: {e}")
        return False


def load_index() -> Dict:
    """Load models index file."""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "version": "1.0",
        "updated": datetime.utcnow().isoformat() + "Z",
        "models": [],
    }


def save_local_index(index_data: Dict):
    """Save local index file."""
    MODELS_BASE_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOCAL_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)


def get_engine_models(engine_id: Optional[str] = None) -> List[Dict]:
    """Get list of models to download, filtered by engine if specified."""
    index_data = load_index()
    models = index_data.get("models", [])

    # Filter by permissive licenses
    free_models = [
        m
        for m in models
        if m.get("license", "").split("-")[0] in PERMISSIVE_LICENSES
        or m.get("license", "").startswith("CC-")
    ]

    # Filter by engine if specified
    if engine_id:
        free_models = [m for m in free_models if m.get("engine") == engine_id]

    return free_models


def is_model_downloaded(model: Dict) -> Tuple[bool, Optional[Path]]:
    """Check if model is already downloaded and verified."""
    engine_id = model.get("engine")
    model_name = model.get("name")

    if not engine_id or not model_name:
        return False, None

    # Check in engine-specific directory
    model_dir = MODELS_BASE_DIR / engine_id
    model_file = model_dir / f"{model_name}.zip"

    # Also check for extracted files
    if not model_file.exists():
        # Check if already extracted
        extracted_dir = model_dir / model_name
        if extracted_dir.exists() and any(extracted_dir.iterdir()):
            # Verify checksum if we have one
            if model.get("sha256"):
                # Try to find the main model file
                for file_path in extracted_dir.rglob("*"):
                    if file_path.is_file():
                        if verify_checksum(file_path, model.get("sha256")):
                            return True, extracted_dir
            else:
                return True, extracted_dir

    if model_file.exists():
        # Verify checksum
        if model.get("sha256"):
            if verify_checksum(model_file, model.get("sha256")):
                return True, model_file
        else:
            return True, model_file

    return False, None


def download_model(model: Dict) -> bool:
    """Download and install a single model."""
    engine_id = model.get("engine")
    model_name = model.get("name")
    download_url = model.get("download_url")
    sha256 = model.get("sha256")

    if not all([engine_id, model_name, download_url]):
        logger.error(f"Incomplete model definition: {model}")
        return False

    # Check if already downloaded
    is_downloaded, existing_path = is_model_downloaded(model)
    if is_downloaded:
        logger.info(f"✓ Model {model_name} already downloaded at {existing_path}")
        return True

    # Determine download destination
    model_dir = MODELS_BASE_DIR / engine_id
    model_dir.mkdir(parents=True, exist_ok=True)

    # Download to temporary file
    url_path = Path(urlparse(download_url).path)
    temp_file = model_dir / f"{model_name}_temp{url_path.suffix}"

    # Download file
    if not download_file(download_url, temp_file, sha256):
        return False

    # Extract if ZIP
    if temp_file.suffix.lower() == ".zip":
        extract_to = model_dir / model_name
        if not extract_archive(temp_file, extract_to):
            temp_file.unlink()
            return False
        # Remove archive after extraction
        temp_file.unlink()
        logger.info(f"✓ Model {model_name} installed to {extract_to}")
    else:
        # Rename to final name
        final_file = model_dir / f"{model_name}{temp_file.suffix}"
        temp_file.rename(final_file)
        logger.info(f"✓ Model {model_name} installed to {final_file}")

    return True


def verify_existing_models() -> Tuple[int, int]:
    """Verify checksums of all existing models."""
    index_data = load_index()
    models = index_data.get("models", [])

    verified = 0
    failed = 0

    for model in models:
        is_downloaded, model_path = is_model_downloaded(model)
        if is_downloaded and model_path:
            sha256 = model.get("sha256")
            if sha256:
                if verify_checksum(model_path, sha256):
                    logger.info(f"✓ Verified {model.get('name')}")
                    verified += 1
                else:
                    logger.error(f"✗ Checksum mismatch: {model.get('name')}")
                    failed += 1
            else:
                logger.warning(
                    f"No checksum for {model.get('name')}, skipping verification"
                )

    return verified, failed


def main():
    parser = argparse.ArgumentParser(description="Download VoiceStudio engine models")
    parser.add_argument("--engine", help="Download models for specific engine only")
    parser.add_argument(
        "--verify-only", action="store_true", help="Verify existing models only"
    )
    parser.add_argument(
        "--update-index", action="store_true", help="Update index from remote"
    )
    parser.add_argument("--list", action="store_true", help="List available models")

    args = parser.parse_args()

    # Ensure models directory exists
    MODELS_BASE_DIR.mkdir(parents=True, exist_ok=True)

    if args.verify_only:
        logger.info("Verifying existing models...")
        verified, failed = verify_existing_models()
        logger.info(f"Verification complete: {verified} verified, {failed} failed")
        return

    if args.list:
        models = get_engine_models(args.engine)
        print(f"\nAvailable models ({len(models)}):")
        for model in models:
            print(
                f"  - {model.get('name')} ({model.get('engine')}) - {model.get('license')}"
            )
        return

    if args.update_index:
        logger.info("Index update not yet implemented")
        logger.info("Manually update engines/models.index.json with new models")
        return

    # Download models
    models = get_engine_models(args.engine)

    if not models:
        logger.warning("No models found to download")
        if args.engine:
            logger.warning(f"  (filtered by engine: {args.engine})")
        return

    logger.info(f"Found {len(models)} models to download")

    success_count = 0
    fail_count = 0

    for model in models:
        logger.info(f"\nProcessing: {model.get('name')} ({model.get('engine')})")
        if download_model(model):
            success_count += 1
        else:
            fail_count += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"Download complete: {success_count} succeeded, {fail_count} failed")
    logger.info(f"Models stored in: {MODELS_BASE_DIR}")


if __name__ == "__main__":
    main()
