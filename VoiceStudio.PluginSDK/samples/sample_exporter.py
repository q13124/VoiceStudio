# Simple exporter: WAV -> OGG (for game engines / web)
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, subprocess, os
PORT=59113
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        body=self.rfile.read(int(self.headers.get("Content-Length","0")))
        req=json.loads(body.decode("utf-8"))
        inp=req["in"]; out=req["out"]
        os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run(["ffmpeg","-y","-i",inp,"-c:a","libvorbis","-q:a","5",out],check=True)
        self.send_response(200); self.end_headers(); self.wfile.write(b'{"ok":true}')
HTTPServer(("127.0.0.1",PORT),H).serve_forever()