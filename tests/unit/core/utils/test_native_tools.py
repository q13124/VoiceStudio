from pathlib import Path

from app.core.utils.native_tools import find_ffmpeg


def test_find_ffmpeg_prefers_env_path(tmp_path: Path, monkeypatch):
    fake = tmp_path / "ffmpeg.exe"
    fake.write_text("not a real exe", encoding="utf-8")
    monkeypatch.setenv("VOICESTUDIO_FFMPEG_PATH", str(fake))

    assert find_ffmpeg() == str(fake)

