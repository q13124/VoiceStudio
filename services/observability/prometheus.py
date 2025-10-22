from __future__ import annotations
from typing import Iterable
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator, metrics

from services.settings import settings

def _ms_buckets_from_env() -> Iterable[float]:
    try:
        parts = [p.strip() for p in settings.prom_latency_buckets_ms.split(",") if p.strip()]
        return [float(p) / 1000.0 for p in parts]  # convert ms → seconds
    except Exception:
        # sensible default
        return (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)

def setup_prometheus(app: FastAPI) -> None:
    """
    Additive: exposes /metrics when PROM_ENABLED=true. No-ops otherwise.
    """
    if not settings.prom_enabled:
        return

    buckets = tuple(_ms_buckets_from_env())

    inst = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=settings.prom_group_paths,
        excluded_handlers=None,
        inprogress_name="http_inprogress",
        inprogress_labels=True,
    )

    if settings.prom_instrument_app:
        inst.add(metrics.default())
        inst.add(metrics.default_inprogress())
        inst.add(
            metrics.latency(
                buckets=buckets,
                metric_name="http_request_duration_seconds",
                labels=True,
            )
        )
        inst.add(metrics.requests())
        inst.add(metrics.responses())
        inst.add(metrics.exceptions())

    # Expose at configured endpoint; hidden from OpenAPI
    inst.instrument(app).expose(
        app,
        endpoint=settings.prom_endpoint,
        include_in_schema=False,
    )
