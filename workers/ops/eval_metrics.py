# eval_metrics.py — placeholder; integrate faster-whisper for WER, duration drift, LUFS
import sys, os, json

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: eval_metrics.py <dir>"}))
        sys.exit(2)
    d = sys.argv[1]
    if not os.path.isdir(d):
        print(json.dumps({"error": f"not a directory: {d}"}))
        sys.exit(2)
    files = [os.path.join(d,f) for f in os.listdir(d) if f.lower().endswith(".wav")]
    print(json.dumps({"files": len(files), "note": "plug whisper WER/loudness here"}))

if __name__ == "__main__":
    main()
