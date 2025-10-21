import os, csv, datetime, subprocess, json
def try_torch():
    try:
        import torch
        if not torch.cuda.is_available():
            return None
        info = {}
        d = 0
        torch.cuda.synchronize()
        total = torch.cuda.get_device_properties(d).total_memory//(1024*1024)
        used  = torch.cuda.memory_allocated(d)//(1024*1024)
        info["total_mb"]=int(total); info["used_mb"]=int(used)
        return info
    except Exception:
        return None

def try_nvidia_smi():
    try:
        out = subprocess.check_output(
            ["nvidia-smi","--query-gpu=memory.total,memory.used","--format=csv,noheader,nounits"],
            stderr=subprocess.STDOUT, text=True
        ).strip()
        if out:
            total, used = out.splitlines()[0].split(",")
            return {"total_mb": int(total.strip()), "used_mb": int(used.strip())}
    except Exception:
        return None

log_dir  = os.path.join(r"C:\VoiceStudio","logs")
os.makedirs(log_dir, exist_ok=True)
csv_path = os.path.join(log_dir, "vram_telemetry.csv")

stamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"
row = {"time_utc": stamp, "total_mb":"", "used_mb":"", "method":""}

info = try_torch()
method = "torch" if info else None
if not info:
    info = try_nvidia_smi(); method = "nvidia-smi" if info else None

if info:
    row["total_mb"] = info["total_mb"]
    row["used_mb"]  = info["used_mb"]
    row["method"]   = method
else:
    row["method"]   = "none"

exists = os.path.exists(csv_path)
with open(csv_path, "a", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["time_utc","total_mb","used_mb","method"])
    if not exists:
        w.writeheader()
    w.writerow(row)
