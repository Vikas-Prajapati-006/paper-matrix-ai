import io
import sys
from pathlib import Path

# Ensure backend root is always in sys.path for test discovery
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

import fitz  # PyMuPDF
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client():
    """Provides a unified FastAPI TestClient instance."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_pdf_bytes():
    """Generates an in-memory valid research paper PDF for testing."""
    doc = fitz.open()
    page = doc.new_page()
    text_content = (
        "Title: Deep Learning in Healthcare\n"
        "Authors: John Doe, Jane Smith\n\n"
        "Abstract\n"
        "This study investigates neural network architectures for early diagnosis.\n\n"
        "Proposed Methodology\n"
        "We employ a transformer-based multi-modal classification pipeline.\n\n"
        "Results and Findings\n"
        "The model achieves 94.8% accuracy on the benchmark validation set.\n\n"
        "Limitations\n"
        "High computational latency on edge devices remains a barrier.\n\n"
        "References\n"
        "[1] A. Vaswani et al., Attention is all you need, 2017."
    )
    page.insert_text((50, 72), text_content)
    pdf_stream = io.BytesIO()
    doc.save(pdf_stream)
    doc.close()
    pdf_stream.seek(0)
    return pdf_stream.getvalue()