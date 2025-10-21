import sys, subprocess
if len(sys.argv) < 4:
    print("usage: ab_null.py <a.wav> <b.wav> <dst.wav>")
    sys.exit(2)
a,b,dst = sys.argv[1], sys.argv[2], sys.argv[3]
subprocess.run(["ffmpeg","-y","-i",a,"-i",b,"-filter_complex","amerge=inputs=2,pan=mono|c0=c0-c1","-c:a","pcm_s16le",dst], check=False)
