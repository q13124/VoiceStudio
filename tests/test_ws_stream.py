def test_ws_router_available():
    import app.core.api.ws_stream as ws
    assert hasattr(ws, "router")
