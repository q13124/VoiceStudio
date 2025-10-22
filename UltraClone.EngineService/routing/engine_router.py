# UltraClone.EngineService/routing/engine_router.py
# Selects best engine by language, quality, speed; provides fallback & A/B hooks.
import json, os

class EngineRouter:
    def __init__(self, engines_cfg_path):
        with open(engines_cfg_path,"r",encoding="utf-8") as f:
            self.cfg = json.load(f)
        self.policy = self.cfg.get("routing_policy", {})

    def choose(self, lang="en", need_quality="high", need_latency="normal"):
        prefer = self.policy.get("prefer", {})
        primary = prefer.get(lang, prefer.get("multi","xtts"))
        chain = [primary]+[e for e in self.policy.get("fallback",[]) if e!=primary]
        # simple latency-based tweak
        if need_latency=="ultra":
            chain = [e for e in chain if e in ("openvoice","xtts")] + [e for e in chain if e not in ("openvoice","xtts")]
        return chain[0], chain

# Example usage inside your TTS endpoint: router.choose(lang)