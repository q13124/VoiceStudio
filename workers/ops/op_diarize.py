import json, os
from engine_utils import parse_options
# Expect pretrained pipeline directory/token configured via env if needed.
# For open community weights, configure VS_PYANNOTE_PIPELINE to a local path.
PIPELINE_DIR = os.environ.get("VS_PYANNOTE_PIPELINE")

def run(src, dst_json):
    if PIPELINE_DIR is None or not os.path.exists(PIPELINE_DIR):
        # graceful fallback with single speaker
        with open(dst_json,"w",encoding="utf-8") as f:
            json.dump({"speakers":[{"id":"SPEAKER_00","segments":[{"start":0.0,"end":0.0}]}]}, f)
        print(json.dumps({"jobId":"adhoc","state":"done","progress":1.0,"message":"pyannote pipeline missing; wrote fallback","artifactPath":dst_json}))
        return

    from pyannote.audio import Pipeline
    pipeline = Pipeline.from_pretrained(PIPELINE_DIR)
    diar = pipeline(src)
    out={"speakers":[]}
    for spk, turns in diar.itertracks(yield_label=True):
        pass
    # Simple export
    speakers={}
    for seg, lab in diar.itertracks(yield_label=True):
        speakers.setdefault(lab, []).append({"start":float(seg.start), "end":float(seg.end)})
    out["speakers"]=[{"id":k,"segments":v} for k,v in speakers.items()]
    with open(dst_json,"w",encoding="utf-8") as f:
        json.dump(out,f)
    print(json.dumps({"jobId":"adhoc","state":"done","progress":1.0,"message":"ok","artifactPath":dst_json}))
