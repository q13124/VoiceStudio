import json, os, subprocess, tempfile, shutil


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _build_filter(dsp: dict, output_mode: str | None, lufs_target: float | None):
    # Map 0..1 UI sliders to "sensible" ffmpeg values
    deesser = _clamp(float(dsp.get("deesser", 0.3)), 0, 1)  # de-ess strength
    eq_high = _clamp(float(dsp.get("eq_high", 0.15)), 0, 1)  # high shelf boost
    comp = _clamp(float(dsp.get("compressor", 0.45)), 0, 1)  # compression amount
    prox = _clamp(float(dsp.get("proximity", 0.2)), 0, 1)  # "mic distance"
    lufs = float(lufs_target if lufs_target is not None else -23)

    # De-esser: use afftdn tuned to 6k–10k band reduction
    deess = f"afftdn=nr={10+deesser*20}:nt=w"

    # High-shelf EQ: highshelf at ~6kHz, gain up to +6dB
    hs_gain = round(eq_high * 6, 2)
    eq = f"equalizer=f=6000:t=h:width=2000:g={hs_gain}"

    # Compressor: threshold -t, ratio r, attack/release fixed, makeup auto
    thr = round(-6 - comp * 10, 2)  # -6..-16 dB
    ratio = round(1.2 + comp * 3.8, 2)  # 1.2..5.0
    compf = f"acompressor=threshold={thr}dB:ratio={ratio}:attack=8:release=120:makeup=1"

    # Proximity: shape low-mid bump and high rolloff to emulate mic distance
    # Use two filters: lowshelf bump + highshelf attenuation
    low_bump = round(prox * 6, 2)  # +0..+6 dB
    high_cut = round(prox * 8, 2)  # 0..8 dB attenuation
    proxf = f"bass=g={low_bump}:f=120, treble=g={-high_cut}:f=8000"

    # Output mode tweaks
    mode = (output_mode or "Broadcast").lower()
    if mode == "asmr":
        # softer comp, more highs detail
        compf = f"acompressor=threshold={thr+4}dB:ratio={max(1.1,ratio-0.5)}:attack=6:release=200:makeup=1"
        hs_gain = round(hs_gain + 1.5, 2)
        eq = f"equalizer=f=6000:t=h:width=2000:g={hs_gain}"
    elif mode == "game":
        # brighter + slightly louder pre-normalization
        hs_gain = round(hs_gain + 1.0, 2)
        eq = f"equalizer=f=6500:t=h:width=2400:g={hs_gain}"
    elif mode == "dialoguestem":
        # conservative dynamics
        compf = f"acompressor=threshold={thr+2}dB:ratio={max(1.2,ratio-0.3)}:attack=10:release=160:makeup=1"

    # LUFS normalize (EBU R128)
    loud = f"loudnorm=I={lufs}:TP=-1.5:LRA=11:print_format=summary"
    # Chain
    chain = ",".join([deess, eq, compf, proxf, loud])
    return chain


def apply(
    in_wav: str,
    out_wav: str,
    dsp: dict,
    output_mode: str | None,
    lufs_target: float | None,
):
    filt = _build_filter(dsp or {}, output_mode, lufs_target)
    # ffmpeg: 24k or 48k ok; keep PCM s16le
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        in_wav,
        "-af",
        filt,
        "-ar",
        "24000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        out_wav,
    ]
    subprocess.run(cmd, check=True)
