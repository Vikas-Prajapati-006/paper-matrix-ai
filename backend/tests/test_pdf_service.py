import pytest
from app.core.errors import ParsingException
from app.services.pdf_service import pdf_service


def test_extract_targeted_text_success(sample_pdf_bytes):
    """Verifies targeted text extraction from a valid research PDF."""
    text = pdf_service.extract_targeted_text(sample_pdf_bytes)

    assert "Deep Learning in Healthcare" in text
    assert "Proposed Methodology" in text
    assert "94.8% accuracy" in text
    # Ensures reference cutting logic works properly
    assert "Attention is all you need" not in text


def test_extract_empty_pdf_raises_exception():
    """Verifies that an empty byte stream triggers a ParsingException."""
    with pytest.raises(ParsingException):
        pdf_service.extract_targeted_text(b"")


def test_extract_corrupt_pdf_bytes():
    """Verifies that corrupted non-PDF bytes raise a ParsingException."""
    corrupt_bytes = b"%PDF-corrupted_junk_data_without_structure"
    with pytest.raises(ParsingException):
        pdf_service.extract_targeted_text(corrupt_bytes)