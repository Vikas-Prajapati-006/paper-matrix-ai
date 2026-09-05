import json
from typing import Optional, List
from fastapi import APIRouter, File, Form, UploadFile
from app.core.limiter import limiter
from app.core.logger import logger
from app.core.security import validate_uploaded_pdf
from app.models.schema import ParseResponse, QuotaStatusResponse
from app.services.groq_service import groq_service
from app.services.pdf_service import pdf_service

router = APIRouter()


@router.post("/parse", response_model=ParseResponse)
async def parse_research_paper(
    file: UploadFile = File(...),
    fingerprint: str = Form(..., description="Client device hardware fingerprint"),
    columns: Optional[str] = Form(None, description="Optional JSON array string of custom columns, e.g. ['dataset', 'baseline']")
):
    """Handles PDF validation, quota deduction, targeted text extraction, and dynamic Groq matrix generation."""
    logger.info(f"Incoming parse request for file: {file.filename} | Device: {fingerprint}")

    # 1. Security checks & magic bytes validation
    pdf_bytes = await validate_uploaded_pdf(file)

    # 2. Atomic credit consumption via Redis
    quota_info = limiter.check_and_consume_credit(fingerprint)

    # 3. Targeted PDF chunk extraction
    targeted_text = pdf_service.extract_targeted_text(pdf_bytes)

    # 4. Process dynamic column payload if sent by frontend
    target_columns: Optional[List[str]] = None
    if columns:
        try:
            parsed_cols = json.loads(columns)
            if isinstance(parsed_cols, list) and len(parsed_cols) > 0:
                target_columns = [str(c).strip().lower().replace(" ", "_") for c in parsed_cols if str(c).strip()]
        except Exception as err:
            logger.warning(f"Could not parse custom columns parameter: {err}. Using default schema.")

    # 5. Groq Llama synthesis with dynamic column support
    extracted_row = groq_service.extract_paper_matrix(targeted_text, custom_columns=target_columns)

    logger.info(f"Successfully synthesized matrix for: {file.filename}")

    return ParseResponse(
        status="success",
        filename=file.filename or "paper.pdf",
        remaining_credits=quota_info["remaining"],
        data=extracted_row
    )


@router.get("/quota/{fingerprint}", response_model=QuotaStatusResponse)
async def check_quota_status(fingerprint: str):
    """Read-only check for available credits for a given fingerprint."""
    status = limiter.get_remaining_credits(fingerprint)
    return QuotaStatusResponse(
        status="success",
        fingerprint=fingerprint,
        remaining_credits=status["remaining"],
        ttl_seconds=status["ttl"]
    )