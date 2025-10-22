# --- DSP hook added ---
import json, subprocess, tempfile, os
from .post_dsp import apply as apply_dsp


def run(src, dst, options_json):
    opts = json.loads(options_json or "{}")
    tmp = dst + ".pre.wav"
    try:
        # transcode to PCM
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                src,
                "-ar",
                "24000",
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                tmp,
            ],
            check=True,
        )
        dsp = {
            "deesser": opts.get("deesser", 0.3),
            "eq_high": opts.get("eq_high", 0.15),
            "compressor": opts.get("compressor", 0.45),
            "proximity": opts.get("proximity", 0.2),
        }
        apply_dsp(
            tmp,
            dst,
            dsp,
            opts.get("output_mode", "Broadcast"),
            float(opts.get("lufs_target", -23)),
        )
        os.remove(tmp)
        print(
            json.dumps(
                {
                    "jobId": "adhoc",
                    "state": "done",
                    "progress": 1.0,
                    "message": "ok",
                    "artifactPath": dst,
                }
            )
        )
    except Exception as e:
        print(json.dumps({"state": "error", "message": str(e)}))
