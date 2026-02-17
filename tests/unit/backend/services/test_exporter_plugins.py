"""Unit tests for FLAC and Opus exporter plugins."""

from pathlib import Path

import pytest

from backend.core.audio.formats import AudioFormat
from plugins.export_flac import plugin as flac_plugin
from plugins.export_opus import plugin as opus_plugin


# Plugin directories containing manifests
FLAC_PLUGIN_DIR = Path(__file__).parents[4] / "plugins" / "export_flac"
OPUS_PLUGIN_DIR = Path(__file__).parents[4] / "plugins" / "export_opus"


class _FakeResult:
    def __init__(self, success: bool):
        self.success = success


class _FakeConverter:
    """Captures convert_to_format kwargs for assertions."""

    def __init__(self):
        self.last_call_kwargs = {}

    async def convert_to_format(self, **kwargs):
        self.last_call_kwargs = kwargs
        return _FakeResult(True)


@pytest.mark.asyncio
async def test_flac_exporter_uses_conversion_service(tmp_path: Path):
    plugin = flac_plugin.FlacExporterPlugin(FLAC_PLUGIN_DIR)
    converter = _FakeConverter()
    plugin._converter = converter
    ok = await plugin.export(b"RIFF....WAVE", tmp_path / "out.flac", {"sample_rate": 44100})
    assert ok is True
    assert converter.last_call_kwargs.get("target_format") == AudioFormat.FLAC


@pytest.mark.asyncio
async def test_opus_exporter_uses_conversion_service(tmp_path: Path):
    plugin = opus_plugin.OpusExporterPlugin(OPUS_PLUGIN_DIR)
    converter = _FakeConverter()
    plugin._converter = converter
    ok = await plugin.export(b"RIFF....WAVE", tmp_path / "out.opus", {"bitrate_kbps": 96})
    assert ok is True
    assert converter.last_call_kwargs.get("target_format") == AudioFormat.OPUS
