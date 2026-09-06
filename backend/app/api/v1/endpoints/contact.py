import logging
from fastapi import APIRouter, HTTPException, status
from app.models.schema import ContactMessageRequest, ContactMessageResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("", response_model=ContactMessageResponse, status_code=status.HTTP_200_OK)
async def submit_contact_form(payload: ContactMessageRequest):
    """
    Secure endpoint for handling user inquiries and feedback.
    Includes honeypot anti-spam verification.
    """
    # 1. Anti-spam bot trap verification (invisible input filled only by bots)
    if payload.honeypot and payload.honeypot.strip():
        logger.warning("Spam bot triggered honeypot filter on contact form.")
        return ContactMessageResponse(
            status="success",
            message="Your message has been received."
        )

    # 2. Secure audit logging of inquiry (safe on servers, no public email exposure)
    logger.info(
        f"[CONTACT INQUIRY] Type: {payload.subject} | From: {payload.email} | Message Length: {len(payload.message)}"
    )

    return ContactMessageResponse(
        status="success",
        message="Thank you! Your message has been safely received."
    )