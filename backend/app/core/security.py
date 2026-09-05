from fastapi import Header, UploadFile
from app.core.config import settings
from app.core.errors import FileTooLargeException, InvalidFileException


def validate_pdf_bytes(file_bytes: bytes) -> bool:
    """Verifies that raw bytes start with standard PDF magic numbers."""
    if not file_bytes.startswith(b"%PDF-"):
        raise InvalidFileException("Uploaded file does not have valid PDF magic signatures.")
    return True


async def validate_uploaded_pdf(file: UploadFile) -> bytes:
    """Validates file presence, mime-type, maximum size, and header signature."""
    if not file.filename.lower().endswith(".pdf"):
        raise InvalidFileException("Filename must end with .pdf extension.")

    contents = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if len(contents) > max_bytes:
        raise FileTooLargeException(max_mb=settings.MAX_FILE_SIZE_MB)

    validate_pdf_bytes(contents)
    return contents


def verify_admin_key(x_admin_key: str = Header(...)) -> bool:
    """Checks whether the incoming header matches the configured admin secret."""
    return x_admin_key == settings.ADMIN_SECRET_KEY