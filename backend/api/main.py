from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import os

app = FastAPI(
    title="CloudPilot API",
    description="AI-Powered Cloud Cost Optimization",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Prometheus metrics at /metrics
Instrumentator().instrument(app).expose(app)

# Only enable Jaeger tracing when running inside Kubernetes
if os.getenv("KUBERNETES_SERVICE_HOST"):
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    provider = TracerProvider()
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_HOST", "jaeger.monitoring.svc.cluster.local"),
        agent_port=6831,
    )
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)

from routes import costs, recommendations, actions, forecast, health
app.include_router(health.router)
app.include_router(costs.router,           prefix="/api/costs",    tags=["costs"])
app.include_router(recommendations.router, prefix="/api",          tags=["ai"])
app.include_router(actions.router,         prefix="/api/actions",  tags=["actions"])
app.include_router(forecast.router,        prefix="/api/forecast", tags=["forecast"])

@app.get("/")
def root():
    return {
        "service": "CloudPilot",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }
