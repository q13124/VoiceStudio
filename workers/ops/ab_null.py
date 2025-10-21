import sys, subprocess

if len(sys.argv) != 4:
    print("usage: ab_null.py A.wav B.wav out.wav", file=sys.stderr)
    sys.exit(2)

a, b, dst = sys.argv[1], sys.argv[2], sys.argv[3]
# Very small difference signal using ffmpeg; placeholder for DAW inspection
subprocess.run([
    "ffmpeg","-y",
    "-i", a,
    "-i", b,
    "-filter_complex",
    "[0:a][1:a]anullsink; amerge=inputs=2,pan=mono|c0=c0-c1",
    "-c:a","pcm_s16le",
    dst
], check=False)
