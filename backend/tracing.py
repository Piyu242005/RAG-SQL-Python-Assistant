"""Observability tracing using OpenTelemetry."""
import logging
from typing import Optional
from config import settings

logger = logging.getLogger("tracing")

# Global tracer instance
_tracer = None

def get_tracer():
    """Initialize and return the OpenTelemetry tracer."""
    global _tracer
    if _tracer is not None:
        return _tracer

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource

        # Set up the resource
        resource = Resource.create({"service.name": "rag-assistant"})
        
        # Set up the provider
        provider = TracerProvider(resource=resource)
        
        # Add a console exporter for visibility (as requested for OTLP console)
        if settings.tracing_backend == "otlp_console":
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)
        
        # Set the global provider
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer("rag-pipeline")
        
        logger.info(f"[OK] Tracing initialized with backend: {settings.tracing_backend}")
        return _tracer
    except ImportError:
        logger.warning("OpenTelemetry libraries not found. Tracing will be disabled.")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize tracing: {e}")
        return None

class TraceSpan:
    """Context manager for tracing spans that works even if OTel is missing."""
    def __init__(self, name: str, attributes: Optional[dict] = None):
        self.name = name
        self.attributes = attributes or {}
        self.tracer = get_tracer()
        self.span = None
        self.context_manager = None

    def __enter__(self):
        if self.tracer:
            try:
                self.span = self.tracer.start_as_current_span(self.name)
                for key, value in self.attributes.items():
                    self.span.set_attribute(key, value)
                self.context_manager = self.span.__enter__()
                return self.span
            except Exception as e:
                logger.error(f"Error starting span {self.name}: {e}")
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.context_manager:
            try:
                if exc_val:
                    self.span.set_attribute("error", True)
                    self.span.set_attribute("error.message", str(exc_val))
                self.context_manager.__exit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                logger.error(f"Error exiting span {self.name}: {e}")
