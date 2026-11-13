from unittest.mock import Mock

import pytest
from opentelemetry.trace import SpanContext, TraceFlags, TraceState

from config import observability


@pytest.mark.parametrize("value", ["1", "true", "YES", "on"])
def test_env_bool_accepts_common_true_values(monkeypatch, value):
    monkeypatch.setenv("FEATURE_ENABLED", value)

    assert observability.env_bool("FEATURE_ENABLED") is True


def test_env_bool_uses_default_and_false_values(monkeypatch):
    monkeypatch.delenv("FEATURE_ENABLED", raising=False)
    assert observability.env_bool("FEATURE_ENABLED", "1") is True
    monkeypatch.setenv("FEATURE_ENABLED", "off")
    assert observability.env_bool("FEATURE_ENABLED") is False


def test_parse_otel_headers_ignores_invalid_and_empty_entries():
    assert observability._parse_otel_headers(" token = abc,broken,=empty,key=, other = value ") == {
        "token": "abc",
        "other": "value",
    }


def test_resolve_service_name_uses_fallbacks(monkeypatch):
    monkeypatch.delenv("OTEL_SERVICE_NAME", raising=False)
    monkeypatch.delenv("SERVICE_NAME", raising=False)
    assert observability._resolve_service_name() == "wuchem"

    monkeypatch.setenv("SERVICE_NAME", "service")
    assert observability._resolve_service_name() == "service"
    monkeypatch.setenv("OTEL_SERVICE_NAME", "otel-service")
    assert observability._resolve_service_name() == "otel-service"


def test_build_trace_exporter_skips_empty_endpoint(monkeypatch):
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", raising=False)
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)

    assert observability._build_trace_exporter() is None


def test_build_trace_exporter_passes_environment_options(monkeypatch):
    exporter_factory = Mock(return_value=object())
    monkeypatch.setattr(observability, "OTLPSpanExporter", exporter_factory)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://otel.example/v1/traces")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_HEADERS", "token=secret")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_INSECURE", "0")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_TIMEOUT", "3.5")

    result = observability._build_trace_exporter()

    assert result is not None
    exporter_factory.assert_called_once_with(
        endpoint="https://otel.example/v1/traces",
        insecure=False,
        headers={"token": "secret"},
        timeout=3.5,
    )


def test_configure_opentelemetry_can_be_disabled(monkeypatch):
    monkeypatch.setattr(observability, "_otel_configured", False)
    monkeypatch.setenv("OTEL_ENABLED", "0")

    observability.configure_opentelemetry()

    assert observability._otel_configured is True


def test_configure_opentelemetry_instruments_django_when_enabled(monkeypatch):
    instrumentor = Mock(is_instrumented_by_opentelemetry=False)
    monkeypatch.setattr(observability, "_otel_configured", False)
    monkeypatch.setattr(observability.trace, "get_tracer_provider", lambda: object())
    monkeypatch.setattr(observability, "_build_trace_exporter", lambda: None)
    monkeypatch.setattr(observability, "DjangoInstrumentor", lambda: instrumentor)
    monkeypatch.setenv("OTEL_ENABLED", "1")

    observability.configure_opentelemetry()

    instrumentor.instrument.assert_called_once_with()


def test_add_otel_trace_context_skips_invalid_spans(monkeypatch):
    event = {"event": "hello"}
    monkeypatch.setattr(observability.trace, "get_current_span", lambda: None)
    assert observability.add_otel_trace_context(None, "info", event) is event

    span = Mock()
    span.get_span_context.return_value = None
    monkeypatch.setattr(observability.trace, "get_current_span", lambda: span)
    assert observability.add_otel_trace_context(None, "info", event) is event


def test_add_otel_trace_context_adds_ids_for_valid_span(monkeypatch):
    context = SpanContext(
        trace_id=0x1234,
        span_id=0x5678,
        is_remote=False,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
        trace_state=TraceState(),
    )
    span = Mock()
    span.get_span_context.return_value = context
    monkeypatch.setattr(observability.trace, "get_current_span", lambda: span)

    event = observability.add_otel_trace_context(None, "info", {"event": "hello"})

    assert event["trace_id"] == f"{0x1234:032x}"
    assert event["span_id"] == f"{0x5678:016x}"
    assert event["trace_flags"] == int(TraceFlags.SAMPLED)


def test_structlog_chain_and_logging_config_cover_renderers():
    assert len(observability.structlog_pre_chain()) > 0

    json_config = observability.build_logging_config("INFO")
    console_config = observability.build_logging_config("DEBUG", json_logs=False)

    assert json_config["formatters"]["structlog"]["processor"] is not None
    assert console_config["formatters"]["structlog"]["processor"] is not None


@pytest.mark.django_db
def test_health_and_readiness_endpoints(client):
    health = client.get("/healthz/")
    readiness = client.get("/readyz/")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert readiness.status_code == 200
    assert readiness.json()["status"] == "Operational"


def test_readiness_endpoint_returns_service_unavailable_when_degraded(client, monkeypatch):
    from config import urls

    payload = {"status": "Degraded", "dependencies": []}
    monkeypatch.setattr(urls, "get_system_status", lambda include_internal: payload)

    response = client.get("/readyz/")

    assert response.status_code == 503
    assert response.json() == payload
