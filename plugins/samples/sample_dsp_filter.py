from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import os

PORT = 59112


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length)
            req = json.loads(body.decode("utf-8"))

            op = req.get("op")
            options = req.get("options", {})
            input_path = req.get("in")
            output_path = req.get("out")

            if not input_path or not output_path:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"ok":false,"error":"missing in/out"}')
                return

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if op == "highpass":
                cutoff = float(options.get("f", 120.0))
                subprocess.run([
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", input_path,
                    "-af", f"highpass=f={cutoff}",
                    output_path,
                ], check=True)
            elif op == "loudnorm":
                subprocess.run([
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", input_path,
                    "-af", "loudnorm=I=-23:TP=-1.5:LRA=7",
                    output_path,
                ], check=True)
            else:
                subprocess.run([
                    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", input_path,
                    output_path,
                ], check=True)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except Exception as ex:
            self.send_response(500)
            self.end_headers()
            msg = ("{" + f"\"ok\":false,\"error\":\"{str(ex)}\"" + "}").encode("utf-8")
            self.wfile.write(msg)


def main():
    print(f"Sample DSP filter plugin listening on {PORT}")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
