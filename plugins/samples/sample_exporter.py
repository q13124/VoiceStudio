from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess
import os

PORT = 59113


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length)
            req = json.loads(body.decode("utf-8"))

            input_path = req.get("in")
            output_path = req.get("out")
            if not input_path or not output_path:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"ok":false,"error":"missing in/out"}')
                return

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            subprocess.run([
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", input_path,
                "-c:a", "libvorbis", "-q:a", "5",
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
    print(f"Sample exporter plugin listening on {PORT}")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
