from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.config import settings
from src.core.exceptions import register_exception_handlers
from src.api.v1.users import router as user_router
from src.api.v1.auth import router as auth_router

# Initialize the primary FastAPI Application Context
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize the Global Corporate Exception Filtering Structure
register_exception_handlers(app)

# Expose Real-time Telemetry Metrics via Prometheus Instrumentation Engine
# This automatically calculates overhead latency, count states, and errors
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Hook Application Layer Multi-Routing Trees
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(user_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])

@app.get("/health", tags=["Infrastructure Checks"])
async def status_check() -> dict[str, str]:
    """
    Shallow health check endpoint for container orchestrators (like Kubernetes or ECS)
    to evaluate container health and traffic routing availability.
    """
    return {"status": "healthy", "environment": settings.ENVIRONMENT}