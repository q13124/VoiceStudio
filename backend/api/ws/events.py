import asyncio
import contextlib

from fastapi import WebSocket


async def stream(ws: WebSocket):
    await ws.accept()
    try:
        # Send a demo heartbeat event every 2s
        i = 0
        while True:
            await ws.send_json({"topic": "heartbeat", "payload": {"n": i}})
            i += 1
            await asyncio.sleep(2.0)
    except Exception:
        with contextlib.suppress(Exception):
            await ws.close()

