from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.core.logger import logger
from app.core.security import verify_admin_key
from app.db.redis_client import get_redis_client

router = APIRouter()


class ResetQuotaRequest(BaseModel):
    fingerprint: str


@router.post("/reset-quota")
async def reset_device_quota(
    payload: ResetQuotaRequest,
    is_admin: bool = Depends(verify_admin_key)
):
    """Resets the usage quota for a specific device fingerprint in Redis."""
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing administrative secret key."
        )

    client = get_redis_client()
    key = f"quota:{payload.fingerprint}"

    try:
        deleted = client.delete(key)
        logger.info(f"Admin reset quota for device fingerprint: {payload.fingerprint}")
        return {
            "status": "success",
            "fingerprint": payload.fingerprint,
            "reset": bool(deleted)
        }
    except Exception as exc:
        logger.error(f"Failed to reset quota in Redis: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redis error during quota reset: {str(exc)}"
        )