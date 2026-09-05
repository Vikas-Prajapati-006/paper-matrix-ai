from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logger import logger
from app.db.redis_client import check_redis_health

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS configuration for AstroJS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4321",
        "http://127.0.0.1:4321",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=False,  # Wildcard origins ke sath False hona browser-safe rehta hai
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]  # File streaming download allow karne ke liye
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback handler to prevent unhandled runtime server crashes."""
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing the request."}
    )


# Mount v1 modular router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System Health"])
async def health_check():
    """Health check endpoint validating core API status and Redis reachability."""
    redis_ok = check_redis_health()
    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis_connected": redis_ok,
        "project": settings.PROJECT_NAME
    }