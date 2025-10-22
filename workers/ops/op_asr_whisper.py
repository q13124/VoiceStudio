import json, os
from faster_whisper import WhisperModel
from engine_utils import parse_options

def run(src, dst_json, options_json):
    opts = parse_options(options_json)
    model_size = opts.get("model_size","large-v3")
    compute_type = opts.get("compute_type","auto")  # "float16" on GPU, "int8" if constrained
    device = "cuda" if opts.get("force_cpu","false").lower()!="true" else "cpu"

    model = WhisperModel(model_size, device=device, compute_type=compute_type, download_root=os.environ.get("VS_WHISPER_DIR"))
    segments, info = model.transcribe(src, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=200))
    data = []
    for seg in segments:
        data.append({"start":seg.start, "end":seg.end, "text":seg.text})
    with open(dst_json,"w",encoding="utf-8") as f:
        import json; json.dump({"language":info.language, "segments":data}, f, ensure_ascii=False)
    print(json.dumps({"jobId":"adhoc","state":"done","progress":1.0,"message":"ok","artifactPath":dst_json}))
