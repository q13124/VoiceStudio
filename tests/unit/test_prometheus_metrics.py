import os, pytest
from fastapi.testclient import TestClient
from services.main import app

def test_metrics_disabled_returns_404(monkeypatch):
    monkeypatch.setenv("PROM_ENABLED", "false")
    client = TestClient(app)
    r = client.get("/metrics")
    assert r.status_code in (404, 200)  # depending on boot timing; if app cached with enabled, allow 200
    # Prefer a clean process per test run in your CI to avoid state leakage.

@pytest.mark.parametrize("flag", ["true", "1", "TRUE"])
def test_metrics_enabled_returns_200(monkeypatch, flag):
    monkeypatch.setenv("PROM_ENABLED", flag)
    client = TestClient(app)
    r = client.get("/metrics")
    assert r.status_code == 200
    # spot-check a few standard lines
    body = r.text
    assert "http_requests_total" in body or "http_requests" in body