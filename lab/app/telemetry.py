"""OpenTelemetry setup shared by the three services. Real SDK, OTLP over HTTP.

Configuration comes from the standard environment variables, so nothing is vendor-specific:
  OTEL_EXPORTER_OTLP_ENDPOINT          where the Collector listens, e.g. http://otel-collector:4318
  OTEL_SEMCONV_STABILITY_OPT_IN=http   use the stable HTTP attribute names (http.request.method ...)
"""
import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

BUILD_ID = os.environ.get("BUILD_ID", "dev")


def setup(service: str, app):
    """Wire traces and metrics for one service and auto-instrument Flask + requests."""
    resource = Resource.create({
        "service.name": service,
        "service.version": BUILD_ID,                       # lets you compare builds (ch2, ch25)
        "deployment.environment.name": os.environ.get("DEPLOY_ENV", "lab"),
    })
    tp = TracerProvider(resource=resource)
    tp.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tp)

    reader = PeriodicExportingMetricReader(OTLPMetricExporter(),
                                           export_interval_millis=int(os.environ.get("METRIC_INTERVAL_MS", "10000")))
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))

    # Auto-instrumentation: a server span per request, a client span per outgoing call, and
    # W3C traceparent + baggage headers injected and extracted for us (ch6, ch7).
    FlaskInstrumentor().instrument_app(app, excluded_urls="healthz")
    RequestsInstrumentor().instrument()
    return trace.get_tracer("shop"), metrics.get_meter("shop")
