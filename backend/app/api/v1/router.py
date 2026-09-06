from fastapi import APIRouter
from app.api.v1.endpoints import admin, export, parse

api_router = APIRouter()

# Register modular sub-routers
api_router.include_router(parse.router, tags=["Synthesis & Quota"])
api_router.include_router(export.router, prefix="/export", tags=["Export & Streaming"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])