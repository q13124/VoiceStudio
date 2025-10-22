# tools/plugin_watcher.py (dev helper) — touches registry.json.stamp when registry.json changes
import os, time, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
reg = ROOT / "plugins" / "registry" / "registry.json"
stamp = reg.with_suffix(".json.stamp")

last = 0.0
while True:
    try:
        t = os.path.getmtime(reg)
        if t>last:
            last=t
            open(stamp,"w").close()
            print("Plugin registry changed.")
    except FileNotFoundError:
        pass
    time.sleep(1.0)