from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse, PlainTextResponse
from app.core.logger import logger
from app.models.schema import ExportRequest, ProseSynthesisRequest, ProseSynthesisResponse
from app.services.export_service import export_service
from app.services.groq_service import groq_service

router = APIRouter()


@router.post("/excel")
async def export_to_excel(payload: ExportRequest):
    """Streams an in-memory generated Excel (.xlsx) file containing survey rows."""
    logger.info(f"Exporting {len(payload.rows)} rows to Excel.")
    excel_stream = export_service.generate_excel(payload.rows)

    response = StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response.headers["Content-Disposition"] = "attachment; filename=literature_survey_matrix.xlsx"
    return response


@router.post("/latex")
async def export_to_latex(payload: ExportRequest):
    """Streams an in-memory generated LaTeX (.tex) document containing tabular code & optional prose."""
    logger.info(f"Exporting {len(payload.rows)} rows to LaTeX (with prose: {bool(payload.prose)}).")
    latex_stream = export_service.generate_latex(payload.rows, prose=payload.prose)

    response = StreamingResponse(
        latex_stream,
        media_type="text/plain; charset=utf-8"
    )
    response.headers["Content-Disposition"] = "attachment; filename=literature_survey_matrix.tex"
    return response


@router.post("/synthesize-prose", response_model=ProseSynthesisResponse)
async def synthesize_related_work(payload: ProseSynthesisRequest):
    """Synthesizes extracted matrix rows into an academic Related Work section."""
    if not payload.rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one paper row is required to draft prose."
        )

    logger.info(f"Synthesizing related work prose for {len(payload.rows)} papers.")
    try:
        drafted_prose = groq_service.generate_related_work_prose(payload.rows)
        return ProseSynthesisResponse(status="success", prose=drafted_prose)
    except Exception as exc:
        logger.error(f"Prose synthesis failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate literature prose: {str(exc)}"
        )


@router.post("/bibtex")
async def export_to_bibtex(payload: ExportRequest):
    """Returns valid BibTeX (.bib) citations for the extracted papers."""
    if not payload.rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one paper row is required to generate BibTeX."
        )

    logger.info(f"Generating BibTeX citations for {len(payload.rows)} papers.")
    try:
        bib_content = export_service.generate_bibtex(payload.rows)
        return PlainTextResponse(bib_content, media_type="text/plain; charset=utf-8")
    except Exception as exc:
        logger.error(f"BibTeX export failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate BibTeX citations: {str(exc)}"
        )