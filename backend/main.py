"""
Main application entry point for Punjab GrainWatch Backend.
Provides FastAPI instance with routing, CORS, and health verification.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .logger import logger
from .api.routes import (
    health,
    datasets,
    quality,
    production,
    yields,
    prices,
    weather,
    procurement,
    stocks,
    geography,
    coverage,
    sources,
    methodology,
    analytics,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Workspace Root: {settings.WORKSPACE_ROOT}")
    logger.info(f"Allowed CORS Origins: {settings.all_allowed_origins}")
    
    # Pre-flight check for Phase 1 catalog
    if settings.catalog_json.exists():
        logger.info(f"Verified dataset catalog exists: {settings.catalog_json}")
    else:
        logger.warning(f"Dataset catalog missing at {settings.catalog_json}. Run validation pipeline first.")
        
    yield
    logger.info(f"Stopping {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Factual, auditable agricultural intelligence backend for Punjab GrainWatch.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Check backend logs for safe diagnosis."}
    )

# Include Routers
app.include_router(health.router)
app.include_router(datasets.router)
app.include_router(quality.router)
app.include_router(production.router)
app.include_router(yields.router)
app.include_router(prices.router)
app.include_router(weather.router)
app.include_router(procurement.router)
app.include_router(stocks.router)
app.include_router(geography.router)
app.include_router(coverage.router)
app.include_router(sources.router)
app.include_router(methodology.router)
app.include_router(analytics.router)


@app.get("/", summary="Root API welcome & pointer")
def read_root():
    """Root endpoint welcoming clients and linking to API documentation."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/api/v1/health",
        "status_url": "/api/v1/status",
        "endpoints": {
            "datasets": "/api/v1/datasets",
            "coverage": "/api/v1/coverage",
            "production": "/api/v1/production",
            "yields": "/api/v1/yields",
            "market_prices": "/api/v1/markets/prices",
            "weather": "/api/v1/weather",
            "procurement": "/api/v1/procurement",
            "stocks": "/api/v1/stocks",
            "districts_geo": "/api/v1/geo/districts",
            "district_crosswalk": "/api/v1/geo/crosswalk",
            "sources": "/api/v1/sources",
            "quality_summary": "/api/v1/quality/summary",
            "quality_issues": "/api/v1/quality/issues",
            "methodology": "/api/v1/methodology",
            "analytics_eligibility": "/api/v1/analytics/eligibility-gate",
            "readiness_metrics": "/api/v1/analytics/readiness-metrics",
            "synthetic_scenario": "/api/v1/analytics/synthetic-scenario",
        },
        "evidence_standard": "Strict empirical evidence; no simulated hoarding scores or fabricated grain arrivals."
    }

