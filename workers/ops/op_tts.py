import json, os, tempfile
from .post_dsp import apply as apply_dsp
from .op_tts_xtts import run as xtts_run
from .op_tts_openvoice import run as ov_run
from .op_tts_cosyvoice import run as cosy_run


def run(text, dst, options_json, voice):
    opts = json.loads(options_json or "{}")
    engine = (opts.get("engine") or os.environ.get("VS_TTS_ENGINE", "xtts")).lower()
    pre = dst + ".pre.wav"
    if engine == "openvoice":
        ov_run(text, pre, options_json, voice)
    elif engine == "cosyvoice":
        cosy_run(text, pre, options_json, voice)
    else:
        xtts_run(text, pre, options_json, voice)

    dsp = {
        "deesser": opts.get("deesser", 0.3),
        "eq_high": opts.get("eq_high", 0.15),
        "compressor": opts.get("compressor", 0.45),
        "proximity": opts.get("proximity", 0.2),
    }
    apply_dsp(
        pre,
        dst,
        dsp,
        opts.get("output_mode", "Broadcast"),
        float(opts.get("lufs_target", -23)),
    )
    try:
        os.remove(pre)
    except:
        pass
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
