import os
from typing import Any
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from src.core.config import settings


def setup_otel(app: FastAPI, db_engine: Any = None) -> None:
    """Configures global OpenTelemetry TracerProvider and registers FastAPI/SQLAlchemy instrumentations."""

    # 1. Establish trace resource identity attributes
    resource = Resource.create(
        attributes={
            "service.name": settings.PROJECT_NAME.lower().replace(" ", "-"),
            "service.version": settings.VERSION,
            "deployment.environment": settings.ENVIRONMENT,
        }
    )

    provider = TracerProvider(resource=resource)

    # 2. Add span exporters
    # Attempt to setup OTLP exporter if endpoint environment variables exist, otherwise fallback to ConsoleSpanExporter
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(exporter))
        except Exception:
            # Fallback to local console print in case of loading error
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter

            provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    else:
        # Default to console span logging in non-production/local environments
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)

    # 3. Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # 4. Instrument SQLAlchemy
    if db_engine:
        try:
            # For async SQLAlchemy engines, instrument the underlying sync_engine
            sync_engine = getattr(db_engine, "sync_engine", db_engine)
            SQLAlchemyInstrumentor().instrument(engine=sync_engine)
        except Exception:
            pass
