import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.core.utils.native_tools import find_ffmpeg


def test_find_ffmpeg_prefers_env_path(tmp_path: Path, monkeypatch):
    """Test that VOICESTUDIO_FFMPEG_PATH env var is used when path_config fails."""
    fake = tmp_path / "ffmpeg.exe"
    fake.write_text("not a real exe", encoding="utf-8")
    monkeypatch.setenv("VOICESTUDIO_FFMPEG_PATH", str(fake))

    # Mock backend.config.path_config to raise ImportError so it falls through to env var
    mock_module = MagicMock()
    mock_module.get_ffmpeg_path.side_effect = RuntimeError("Mocked runtime error")
    with patch.dict(sys.modules, {"backend.config.path_config": mock_module}):
        result = find_ffmpeg()
        # When path_config fails, should fall back to env var
        assert result == str(fake)


def test_find_ffmpeg_uses_path_config_first(tmp_path: Path, monkeypatch):
    """Test that path_config is tried first."""
    fake_env = tmp_path / "env_ffmpeg.exe"
    fake_env.write_text("env ffmpeg", encoding="utf-8")
    monkeypatch.setenv("VOICESTUDIO_FFMPEG_PATH", str(fake_env))

    fake_config = tmp_path / "config_ffmpeg.exe"
    fake_config.write_text("config ffmpeg", encoding="utf-8")

    # Mock path_config module to return a specific path
    mock_module = MagicMock()
    mock_module.get_ffmpeg_path.return_value = fake_config
    with patch.dict(sys.modules, {"backend.config.path_config": mock_module}):
        result = find_ffmpeg()
        # path_config takes precedence over env var
        assert result == str(fake_config)

