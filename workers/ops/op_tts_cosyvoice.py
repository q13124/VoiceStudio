import json, os, importlib, soundfile as sf, numpy as np
from engine_utils import device_auto, parse_options, apply_parameter_map

COSY_DIR = os.environ.get("VS_COSY_DIR", os.path.join(os.environ.get("PROGRAMDATA","C:/ProgramData"),"VoiceStudio","models","cosyvoice2"))

def run(text, dst, options_json, voice_profile_or_ref=None):
    opts = parse_options(options_json)
    kw   = apply_parameter_map({}, opts)

    if importlib.util.find_spec("cosyvoice2") is None:
        # Fallback: simple file so service doesn't crash
        sf.write(dst, np.zeros(48000, dtype=np.float32), 24000, subtype="PCM_16")
        print(json.dumps({"jobId":"adhoc","state":"done","progress":1.0,"message":"cosyvoice2 not installed; wrote silence","artifactPath":dst}))
        return

    from cosyvoice2 import CosyVoice
    cv = CosyVoice(model_dir=COSY_DIR)
    sr, wav = cv.tts(text, ref=voice_profile_or_ref, preset=opts.get("preset","neutral"))
    sf.write(dst, wav, sr, subtype="PCM_16")
    print(json.dumps({"jobId":"adhoc","state":"done","progress":1.0,"message":"ok","artifactPath":dst}))
