"""Integration tests for plugin loading and registration lifecycle.

These tests use PluginLoader to load real plugins from the plugins/
directory into a fresh FastAPI TestClient and verify routes exist.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.plugins.loader import PluginLoader

PLUGINS_DIR = Path(__file__).resolve().parents[3] / "plugins"

# Phase 3 audio-effect plugins (should always load)
AUDIO_EFFECT_PLUGINS = ["normalize_volume", "compressor", "reverb"]

# Phase 3 exporter plugins (should always load)
EXPORTER_PLUGINS = ["export_flac", "export_opus"]


def _make_app_with_plugins(plugin_names: list[str]) -> tuple[FastAPI, PluginLoader]:
    """Create a FastAPI app and load only the requested plugins."""
    app = FastAPI()
    loader = PluginLoader(str(PLUGINS_DIR))
    for name in plugin_names:
        plugin_dir = PLUGINS_DIR / name
        if plugin_dir.is_dir():
            loader._load_plugin(plugin_dir, app)
    return app, loader


# ------------------------------------------------------------------
# Audio-effect plugin loading
# ------------------------------------------------------------------


@pytest.mark.parametrize("plugin_name", AUDIO_EFFECT_PLUGINS)
def test_audio_effect_plugin_loads_and_registers_health(plugin_name: str):
    """Each audio-effect plugin should load, register a health route, and return 200."""
    app, loader = _make_app_with_plugins([plugin_name])
    assert plugin_name in loader.loaded_plugins, f"{plugin_name} failed to load"

    client = TestClient(app)
    resp = client.get(f"/api/plugin/{plugin_name}/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "healthy" or body.get("plugin") == plugin_name


@pytest.mark.parametrize("plugin_name", AUDIO_EFFECT_PLUGINS)
def test_audio_effect_plugin_has_process_route(plugin_name: str):
    """Each audio-effect plugin should expose a POST /process endpoint."""
    app, loader = _make_app_with_plugins([plugin_name])
    assert plugin_name in loader.loaded_plugins

    routes = [r.path for r in app.routes]
    assert f"/api/plugin/{plugin_name}/process" in routes


# ------------------------------------------------------------------
# Exporter plugin loading
# ------------------------------------------------------------------


@pytest.mark.parametrize("plugin_name", EXPORTER_PLUGINS)
def test_exporter_plugin_loads_and_has_export_route(plugin_name: str):
    """Exporter plugins should load and expose a POST /export endpoint."""
    app, loader = _make_app_with_plugins([plugin_name])
    assert plugin_name in loader.loaded_plugins

    routes = [r.path for r in app.routes]
    assert f"/api/plugin/{plugin_name}/export" in routes


# ------------------------------------------------------------------
# Manifest validity
# ------------------------------------------------------------------


@pytest.mark.parametrize(
    "plugin_name",
    AUDIO_EFFECT_PLUGINS + EXPORTER_PLUGINS,
)
def test_manifest_has_required_fields(plugin_name: str):
    """Every Phase 3 manifest must have name, version, entry_points.backend, and security.isolation_mode."""
    manifest_path = PLUGINS_DIR / plugin_name / "manifest.json"
    assert manifest_path.exists(), f"Missing manifest: {manifest_path}"

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest.get("name") == plugin_name
    assert "version" in manifest
    assert manifest.get("entry_points", {}).get("backend"), "Missing entry_points.backend"
    assert (
        manifest.get("security", {}).get("isolation_mode") == "in_process"
    ), f"{plugin_name} isolation_mode should be 'in_process' (ADR-037 Lane A)"


# ------------------------------------------------------------------
# Loader metadata
# ------------------------------------------------------------------


def test_loader_records_metadata_for_all_loaded_plugins():
    """PluginLoader should store metadata for each successfully loaded plugin."""
    all_names = AUDIO_EFFECT_PLUGINS + EXPORTER_PLUGINS
    app, loader = _make_app_with_plugins(all_names)

    for name in all_names:
        info = loader.get_plugin_info(name)
        assert info is not None, f"Missing metadata for {name}"
        assert info["name"] == name
        assert "version" in info
        assert "directory" in info
