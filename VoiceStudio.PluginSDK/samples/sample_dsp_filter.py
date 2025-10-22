from http.server import BaseHTTPRequestHandler, HTTPServer
import json, subprocess, tempfile, os, sys

PORT = 59112

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        ln = int(self.headers.get("Content-Length","0"))
        body = self.rfile.read(ln)
        req = json.loads(body.decode("utf-8"))
        op = req.get("op")
        opts = req.get("options",{})
        inp = req.get("in")
        out = req.get("out")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if op=="highpass":
            f = float(opts.get("f",120.0))
            subprocess.run(["ffmpeg","-y","-i",inp,"-af",f"highpass=f={f}", out], check=True)
        elif op=="loudnorm":
            subprocess.run(["ffmpeg","-y","-i",inp,"-af","loudnorm=I=-23:TP=-1.5:LRA=7", out], check=True)
        else:
            subprocess.run(["ffmpeg","-y","-i",inp, out], check=True)
        self.send_response(200); self.end_headers(); self.wfile.write(b'{"ok":true}')

def main():
    print(f"Sample DSP filter plugin listening on {PORT}")
    HTTPServer(("127.0.0.1",PORT), H).serve_forever()

if __name__=="__main__":
    main()