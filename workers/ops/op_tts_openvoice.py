import json, os, soundfile as sf, numpy as np
from engine_utils import device_auto, parse_options, apply_parameter_map

# This assumes you installed openvoice and placed models under VS_OPENVOICE_DIR
OPENVOICE_DIR = os.environ.get("VS_OPENVOICE_DIR", os.path.join(os.environ.get("PROGRAMDATA","C:/ProgramData"),"VoiceStudio","models","openvoice"))

def _load_openvoice():
    # Typical OpenVoice usage pattern (api can vary across forks)
    from openvoice.api import OpenVoice
    return OpenVoice(model_dir=OPENVOICE_DIR)

def run(text, dst, options_json, voice_profile_or_ref=None):
    opts = parse_options(options_json)
    kw   = apply_parameter_map({}, opts)
    eng  = _load_openvoice()

    ref = None
    if voice_profile_or_ref and os.path.exists(voice_profile_or_ref):
        ref = voice_profile_or_ref if voice_profile_or_ref.lower().endswith((".wav",".flac",".mp3")) else os.path.join(voice_profile_or_ref,"ref.wav")

    sr, wav = eng.tts(text, ref_audio=ref, language=opts.get("language","en"), prosody=kw.get("emotion_curve"))
    sf.write(dst, np.array(wav), sr, subtype="PCM_16")
    print(json.dumps({"jobId":"adhoc","state":"done","progress":1.0,"message":"ok","artifactPath":dst}))
