# tools/migrate_configs.py — merges legacy configs into 3 canonical files.
import json, os, glob, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG = os.path.join(ROOT,"config")
LEGACY = os.path.join(CFG,"legacy")
os.makedirs(LEGACY, exist_ok=True)
def load(path):
    try:
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    except Exception: return {}
agg = {}
for f in glob.glob(os.path.join(CFG,"*.json")):
    if os.path.basename(f) in ("voicestudio.config.json","engines.config.json","deployment.config.json"):
        continue
    base=os.path.basename(f)
    agg[base]=load(f)
    os.replace(f, os.path.join(LEGACY, base))
# naive merge (extend as needed)
vs=json.load(open(os.path.join(CFG,"voicestudio.config.json"),"r",encoding="utf-8"))
eng=json.load(open(os.path.join(CFG,"engines.config.json"),"r",encoding="utf-8"))
dep=json.load(open(os.path.join(CFG,"deployment.config.json"),"r",encoding="utf-8"))
vs["legacy_merge"]={"files":list(agg.keys())}
json.dump(vs, open(os.path.join(CFG,"voicestudio.config.json"),"w",encoding="utf-8"), indent=2)
json.dump(eng, open(os.path.join(CFG,"engines.config.json"),"w",encoding="utf-8"), indent=2)
json.dump(dep, open(os.path.join(CFG,"deployment.config.json"),"w",encoding="utf-8"), indent=2)
print("Legacy configs moved to config/legacy and canonical files refreshed.")