# tests/integration/test_render_metrics.py
# Requires: faster-whisper, soundfile, pyloudnorm (or fallback)
import os, json, time, subprocess, tempfile, math, sys
import soundfile as sf

try:
    import pyloudnorm as pyln
except Exception:
    pyln = None

TEXT = "VoiceStudio generates natural speech quickly and reliably."


def render_and_metrics():
    tmpdir = tempfile.mkdtemp(prefix="vs_test_")
    wav = os.path.join(tmpdir, "out.wav")
    pd = os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"), "VoiceStudio")
    py = os.path.join(pd, "pyenv", "Scripts", "python.exe")
    wr = os.path.join(pd, "workers", "worker_router.py")
    # ask dispatcher (fallback chain handled in service, but call worker directly here)
    subprocess.run(
        [
            py,
            wr,
            "tts",
            "--a",
            TEXT,
            "--b",
            wav,
            "--c",
            json.dumps({"engine": "xtts", "stability": 0.65}),
        ],
        check=True,
    )
    assert os.path.exists(wav), "render failed"
    # ASR (faster-whisper) to get WER-ish proxy
    from faster_whisper import WhisperModel

    model = WhisperModel(
        "medium", device="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
    )
    segs, _ = model.transcribe(wav, language="en")
    hyp = " ".join([s.text.strip() for s in segs]).strip().lower()
    ref = TEXT.lower()
    wer = word_error_rate(ref, hyp)
    # LUFS
    data, sr = sf.read(wav)
    lufs = None
    if pyln:
        meter = pyln.Meter(sr)
        lufs = meter.integrated_loudness(data if data.ndim == 1 else data.mean(axis=1))
    return {"wav": wav, "wer": wer, "lufs": lufs}


def word_error_rate(ref, hyp):
    r = ref.split()
    h = hyp.split()
    # Levenshtein
    dp = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        dp[i][0] = i
    for j in range(1, len(h) + 1):
        dp[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            cost = 0 if r[i - 1] == h[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[len(r)][len(h)] / max(1, len(r))


def test_render_pipeline_metrics():
    m = render_and_metrics()
    assert os.path.exists(m["wav"])
    assert m["wer"] <= 0.40  # generous bound
