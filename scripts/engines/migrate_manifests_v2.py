#!/usr/bin/env python3
"""
Engine Manifest v1 to v2 Migration Script

Migrates engine manifest files to schema v2.0 format with:
- schema_version field
- Standardized capabilities enum
- health_check configuration
- circuit_breaker configuration
- quality_features for TTS engines
- venv_family assignment

TASK-EE-001 (TD-016)
"""

from __future__ import annotations

import json
import glob
from pathlib import Path
from typing import Any, Optional, List, Dict

# Capability mappings for normalization
CAPABILITY_MAPPINGS = {
    # Old/custom -> Standard enum
    "fast_tts": "real_time",
    "low_latency": "real_time",
    "offline": None,  # Remove, implied by local-first
    "multi_voice": None,  # Remove, implied
    "speech_to_text": "transcription",
    "multi_language_stt": "transcription",
    "language_detection": None,  # Remove, implied for STT
    "word_timestamps": None,  # Remove, implied for STT
}

# Standard capabilities from schema
VALID_CAPABILITIES = {
    "voice_cloning",
    "zero_shot_cloning",
    "multi_language_tts",
    "emotion_control",
    "expressive_speech",
    "high_quality_synthesis",
    "real_time",
    "streaming",
    "batch_processing",
    "voice_conversion",
    "style_transfer",
    "prosody_control",
    "transcription",
    "translation",
}

# Venv family assignments based on engine characteristics
VENV_FAMILY_OVERRIDES = {
    "chatterbox": "bleeding_edge",
    "piper": "cpu_only",
    "silero": "cpu_only",
    "espeak_ng": "cpu_only",
    "festival": "cpu_only",
    "rhvoice": "cpu_only",
    "marytts": "cpu_only",
}

# Quality feature defaults by engine type
QUALITY_DEFAULTS = {
    "tts": {
        "mos_estimate": "3.5-4.0",
        "similarity_score": "medium",
        "naturalness": "medium",
        "zero_shot_capability": False,
    },
    "stt": None,  # STT engines don't have quality features
    "voice_conversion": {
        "mos_estimate": "3.0-4.0",
        "similarity_score": "high",
        "naturalness": "medium",
        "zero_shot_capability": False,
    },
}

# Engine-specific quality overrides
QUALITY_OVERRIDES = {
    "xtts_v2": {
        "mos_estimate": "4.0-4.5",
        "similarity_score": "very_high",
        "naturalness": "high",
        "zero_shot_capability": True,
    },
    "chatterbox": {
        "mos_estimate": "4.5-5.0",
        "similarity_score": "very_high",
        "naturalness": "very_high",
        "zero_shot_capability": True,
    },
    "tortoise": {
        "mos_estimate": "4.0-4.5",
        "similarity_score": "high",
        "naturalness": "very_high",
        "zero_shot_capability": True,
    },
    "openvoice": {
        "mos_estimate": "4.0-4.5",
        "similarity_score": "very_high",
        "naturalness": "high",
        "zero_shot_capability": True,
    },
    "rvc": {
        "mos_estimate": "3.5-4.5",
        "similarity_score": "very_high",
        "naturalness": "high",
        "zero_shot_capability": False,
    },
    "sovits": {
        "mos_estimate": "4.0-4.5",
        "similarity_score": "very_high",
        "naturalness": "high",
        "zero_shot_capability": False,
    },
    "gpt_sovits": {
        "mos_estimate": "4.0-4.5",
        "similarity_score": "very_high",
        "naturalness": "very_high",
        "zero_shot_capability": True,
    },
}


def normalize_capabilities(caps: List[str] | None) -> List[str]:
    """Normalize capabilities to schema v2 enum values."""
    if not caps:
        return []
    
    normalized = set()
    for cap in caps:
        if cap in VALID_CAPABILITIES:
            normalized.add(cap)
        elif cap in CAPABILITY_MAPPINGS:
            mapped = CAPABILITY_MAPPINGS[cap]
            if mapped:
                normalized.add(mapped)
        # Keep unknown capabilities as-is (schema may need update)
        else:
            normalized.add(cap)
    
    return sorted(list(normalized))


def get_venv_family(engine_id: str, manifest: Dict) -> str:
    """Determine venv family for an engine."""
    # Check if already set
    if "venv_family" in manifest:
        return manifest["venv_family"]
    
    # Check overrides
    if engine_id in VENV_FAMILY_OVERRIDES:
        return VENV_FAMILY_OVERRIDES[engine_id]
    
    # Determine from device requirements
    device_req = manifest.get("device_requirements", {})
    gpu_req = device_req.get("gpu", "optional")
    
    if gpu_req == "not_supported":
        return "cpu_only"
    
    # Check torch version requirement
    deps = manifest.get("dependencies", {})
    torch_ver = deps.get("torch", "")
    
    if ">=2.6" in torch_ver or ">2.5" in torch_ver:
        return "bleeding_edge"
    
    return "core"


def get_quality_features(engine_id: str, manifest: Dict) -> Optional[Dict]:
    """Get quality features for an engine."""
    # Already has quality features
    if "quality_features" in manifest:
        return manifest["quality_features"]
    
    # Check overrides
    if engine_id in QUALITY_OVERRIDES:
        return QUALITY_OVERRIDES[engine_id]
    
    # Get defaults based on subtype
    subtype = manifest.get("subtype", "")
    return QUALITY_DEFAULTS.get(subtype)


def get_health_check(engine_id: str, manifest: Dict) -> Dict:
    """Get health check configuration."""
    if "health_check" in manifest:
        return manifest["health_check"]
    
    return {
        "endpoint": f"/api/engines/{engine_id}/health",
        "timeout_seconds": 30,
        "retries": 3,
    }


def get_circuit_breaker(manifest: Dict) -> Dict:
    """Get circuit breaker configuration."""
    if "circuit_breaker" in manifest:
        return manifest["circuit_breaker"]
    
    return {
        "failure_threshold": 3,
        "recovery_timeout_seconds": 60,
        "enabled": True,
    }


def migrate_manifest(manifest: Dict) -> Dict:
    """Migrate a v1 manifest to v2 format."""
    engine_id = manifest.get("engine_id", "unknown")
    
    # Already v2
    if manifest.get("schema_version") == "2.0":
        return manifest
    
    # Create new manifest with v2 fields
    migrated = {
        "engine_id": manifest.get("engine_id"),
        "name": manifest.get("name"),
        "type": manifest.get("type", "audio"),
        "subtype": manifest.get("subtype"),
        "version": manifest.get("version", "1.0"),
        "schema_version": "2.0",
        "description": manifest.get("description"),
        "author": manifest.get("author"),
        "license": manifest.get("license"),
    }
    
    # Optional fields
    if "homepage" in manifest:
        migrated["homepage"] = manifest["homepage"]
    
    if "python_version" in manifest:
        migrated["python_version"] = manifest["python_version"]
    
    # Venv family (TD-001, ADR-022)
    migrated["venv_family"] = get_venv_family(engine_id, manifest)
    
    # Dependencies
    if "dependencies" in manifest:
        migrated["dependencies"] = manifest["dependencies"]
    
    if "system_dependencies" in manifest:
        migrated["system_dependencies"] = manifest["system_dependencies"]
    
    # Model paths
    if "model_paths" in manifest:
        migrated["model_paths"] = manifest["model_paths"]
    
    # Languages
    if "supported_languages" in manifest:
        migrated["supported_languages"] = manifest["supported_languages"]
    
    # Capabilities (normalized)
    if "capabilities" in manifest:
        migrated["capabilities"] = normalize_capabilities(manifest["capabilities"])
    
    # Device requirements
    if "device_requirements" in manifest:
        migrated["device_requirements"] = manifest["device_requirements"]
    
    # Entry point
    if "entry_point" in manifest:
        migrated["entry_point"] = manifest["entry_point"]
    
    # Config schema
    if "config_schema" in manifest:
        migrated["config_schema"] = manifest["config_schema"]
    
    # Quality features (v2)
    quality = get_quality_features(engine_id, manifest)
    if quality:
        migrated["quality_features"] = quality
    
    # Health check (v2)
    migrated["health_check"] = get_health_check(engine_id, manifest)
    
    # Circuit breaker (TD-014, v2)
    migrated["circuit_breaker"] = get_circuit_breaker(manifest)
    
    # Tags
    if "tags" in manifest:
        migrated["tags"] = manifest["tags"]
    else:
        # Auto-generate tags
        tags = [manifest.get("type", "audio")]
        if manifest.get("subtype"):
            tags.append(manifest["subtype"])
        migrated["tags"] = tags
    
    # Preserve other fields (resources, lifecycle, security, etc.)
    for key in ["tasks", "resources", "lifecycle", "preHooks", "postHooks", "log", "security"]:
        if key in manifest:
            migrated[key] = manifest[key]
    
    # Remove None values
    return {k: v for k, v in migrated.items() if v is not None}


def migrate_all_manifests(dry_run: bool = False) -> Dict:
    """Migrate all engine manifests to v2."""
    results = {
        "migrated": [],
        "already_v2": [],
        "errors": [],
    }
    
    manifest_files = glob.glob("engines/**/engine.manifest.json", recursive=True)
    
    for filepath in manifest_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            engine_id = manifest.get("engine_id", Path(filepath).parent.name)
            
            if manifest.get("schema_version") == "2.0":
                results["already_v2"].append(engine_id)
                continue
            
            migrated = migrate_manifest(manifest)
            
            if dry_run:
                print(f"Would migrate: {engine_id}")
                print(f"  venv_family: {migrated.get('venv_family')}")
                print(f"  capabilities: {migrated.get('capabilities')}")
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(migrated, f, indent=2, ensure_ascii=False)
                    f.write("\n")
            
            results["migrated"].append(engine_id)
            
        except Exception as e:
            results["errors"].append({"file": filepath, "error": str(e)})
    
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate engine manifests to v2")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--validate", action="store_true", help="Validate manifests after migration")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Engine Manifest v2 Migration")
    print("TASK-EE-001 (TD-016)")
    print("=" * 60)
    print()
    
    results = migrate_all_manifests(dry_run=args.dry_run)
    
    print()
    print(f"Already v2: {len(results['already_v2'])}")
    print(f"Migrated: {len(results['migrated'])}")
    print(f"Errors: {len(results['errors'])}")
    
    if results["errors"]:
        print("\nErrors:")
        for err in results["errors"]:
            print(f"  {err['file']}: {err['error']}")
    
    if args.validate and not args.dry_run:
        print("\nValidating migrated manifests...")
        # Validate all manifests have required fields
        valid = 0
        invalid = 0
        for filepath in glob.glob("engines/**/engine.manifest.json", recursive=True):
            with open(filepath, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            required = ["engine_id", "name", "type", "version", "schema_version"]
            if all(k in manifest for k in required):
                valid += 1
            else:
                missing = [k for k in required if k not in manifest]
                print(f"  Invalid: {filepath} - missing: {missing}")
                invalid += 1
        
        print(f"\nValidation: {valid} valid, {invalid} invalid")
    
    return 0 if not results["errors"] else 1


if __name__ == "__main__":
    exit(main())
