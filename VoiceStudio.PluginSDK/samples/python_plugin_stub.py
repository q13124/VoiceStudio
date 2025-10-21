#!/usr/bin/env python3
import json
import socket
import sys

# Placeholder: not gRPC yet; just a simple TCP protocol for illustration
# Implementors should replace with gRPC server exposing ListPlugins and Run

PLUGINS = [
    {
        "id": "sample.null",
        "name": "Null Analyzer",
        "category": "analyzer",
        "version": "0.1.0",
        "icon": ""
    }
]


def handle(conn):
    data = conn.recv(65536)
    try:
        req = json.loads(data.decode("utf-8"))
    except Exception:
        conn.sendall(b"{\"error\":\"bad json\"}")
        return
    if req.get("op") == "ListPlugins":
        conn.sendall(json.dumps({"plugins": PLUGINS}).encode("utf-8"))
    elif req.get("op") == "Run":
        conn.sendall(json.dumps({"status": "ok", "outputs": []}).encode("utf-8"))
    else:
        conn.sendall(b"{\"error\":\"unknown op\"}")


def main():
    host = "127.0.0.1"
    port = 59110
    with socket.create_server((host, port)) as s:
        print(json.dumps({"listening": f"{host}:{port}"}))
        while True:
            conn, _ = s.accept()
            with conn:
                handle(conn)


if __name__ == "__main__":
    main()
