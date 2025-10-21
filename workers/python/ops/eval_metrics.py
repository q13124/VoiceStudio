# eval_metrics.py — placeholder; integrate faster-whisper for WER, duration drift, LUFS
import sys, os, json

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error":"usage: eval_metrics.py <dir>"}))
        return
    d = sys.argv[1]
    try:
        files = [f for f in os.listdir(d) if f.lower().endswith('.wav')]
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return
    print(json.dumps({"files": len(files), "note": "plug whisper WER/loudness here"}))

if __name__ == "__main__":
    main()
