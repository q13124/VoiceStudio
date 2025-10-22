# tests/test_router.py
from UltraClone.EngineService.routing.engine_router import EngineRouter
import os, json
def test_choose_en_xtts(tmp_path):
    cfg = tmp_path/"eng.json"
    cfg.write_text(json.dumps({"routing_policy":{"prefer":{"en":"xtts"},"fallback":["openvoice","cosyvoice2","coqui"]}}))
    r=EngineRouter(str(cfg))
    e,chain = r.choose("en")
    assert e=="xtts" and "openvoice" in chain