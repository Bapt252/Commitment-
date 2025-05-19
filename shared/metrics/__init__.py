"""Metrics package for Prometheus integration."""

from .prometheus import (
    setup_prometheus_middleware,
    track_ml_operation,
    track_openai_call,
    PrometheusMiddleware,
    SystemMetricsCollector,
    # Métriques exportées
    REQUEST_COUNT,
    REQUEST_DURATION,
    ACTIVE_REQUESTS,
    ML_PROCESSING_TIME,
    ML_REQUESTS_TOTAL,
    ML_ERRORS_TOTAL,
    OPENAI_API_CALLS,
    OPENAI_TOKENS_USED
)

__all__ = [
    "setup_prometheus_middleware",
    "track_ml_operation",
    "track_openai_call",
    "PrometheusMiddleware",
    "SystemMetricsCollector",
    "REQUEST_COUNT",
    "REQUEST_DURATION",
    "ACTIVE_REQUESTS",
    "ML_PROCESSING_TIME",
    "ML_REQUESTS_TOTAL",
    "ML_ERRORS_TOTAL",
    "OPENAI_API_CALLS",
    "OPENAI_TOKENS_USED"
]