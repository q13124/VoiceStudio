import json, os, torch, soundfile as sf
from engine_utils import device_auto, parse_options, apply_parameter_map

# Expect model assets path (can be HF or local cache). Adjust to your path.
XTTS_MODEL_DIR = os.environ.get("VS_XTTS_DIR", os.path.join(os.environ.get("PROGRAMDATA", "C:/ProgramData"), "VoiceStudio", "models", "xtts"))

def _load_tts():
    from TTS.api import TTS
    model_name = os.environ.get("VS_XTTS_NAME", "tts_models/multilingual/multi-dataset/xtts_v2")
    if os.path.isdir(XTTS_MODEL_DIR):
        return TTS(model_path=XTTS_MODEL_DIR, progress_bar=False, gpu=torch.cuda.is_available())
    return TTS(model_name, progress_bar=False, gpu=torch.cuda.is_available())

def run(text, dst, options_json, voice_profile_or_ref=None):
    opts = parse_options(options_json)
    kw   = apply_parameter_map({}, opts)
    device = device_auto()
    tts = _load_tts()

    # Speaker ref: either path to .wav in a profile or a raw ref file
    speaker_wav = None
    if voice_profile_or_ref and os.path.exists(voice_profile_or_ref):
        # Accept profile folder or a direct wav
        if os.path.isdir(voice_profile_or_ref):
            cand = os.path.join(voice_profile_or_ref, "ref.wav")
            speaker_wav = cand if os.path.isfile(cand) else None
        elif voice_profile_or_ref.lower().endswith((".wav",".flac",".mp3")):
            speaker_wav = voice_profile_or_ref

    # XTTS parameters that loosely map to our UI
    xtts_kwargs = dict(
        temperature=1.0 - float(kw.get("stability", 0.6)),  # lower temp ~ more stable
        speed=1.0, 
        # NOTE: XTTS API evolves; keep conservative and expand as needed
    )
    wav = tts.tts(text=text, speaker_wav=speaker_wav, language=opts.get("language","en"), **xtts_kwargs)
    sf.write(dst, wav, 24000, subtype="PCM_16")
    print(json.dumps({"jobId":"adhoc","state":"done","progress":1.0,"message":"ok","artifactPath":dst}))
