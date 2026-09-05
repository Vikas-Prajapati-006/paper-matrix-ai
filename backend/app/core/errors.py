from fastapi import HTTPException, status


class QuotaExceededException(HTTPException):
    def __init__(self, detail: str = "Daily free quota reached. Upgrade or try again tomorrow."):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class InvalidFileException(HTTPException):
    def __init__(self, detail: str = "Invalid file type. Only valid PDF files are allowed."):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class FileTooLargeException(HTTPException):
    def __init__(self, max_mb: int = 15):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {max_mb}MB."
        )


class ParsingException(HTTPException):
    def __init__(self, detail: str = "Failed to extract targeted sections from the PDF document."):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class ExtractionLLMException(HTTPException):
    def __init__(self, detail: str = "AI model failed to synthesize paper matrix. Please retry."):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)