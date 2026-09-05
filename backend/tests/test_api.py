from unittest.mock import MagicMock, patch
from app.models.schema import PaperMatrixRow


def test_health_check(client):
    """Verifies the health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "redis_connected" in data


def test_parse_invalid_magic_bytes(client):
    """Verifies that non-PDF files disguised as PDF are rejected with 400."""
    fake_file_content = b"This is plain text pretending to be a PDF."
    response = client.post(
        "/api/v1/parse",
        files={"file": ("fake.pdf", fake_file_content, "application/pdf")},
        data={"fingerprint": "test_device_123"},
    )
    assert response.status_code == 400
    assert "magic" in response.json()["detail"].lower()


@patch("app.api.v1.endpoints.parse.limiter.check_and_consume_credit")
@patch("app.api.v1.endpoints.parse.groq_service.extract_paper_matrix")
def test_parse_success(mock_groq, mock_limiter, client, sample_pdf_bytes):
    """Verifies full parsing lifecycle with mocked external calls."""
    mock_limiter.return_value = {"remaining": 2, "ttl": 86400}
    mock_groq.return_value = PaperMatrixRow(
        title="Deep Learning in Healthcare",
        authors="John Doe, Jane Smith",
        year="2024",
        problem_statement="Early disease diagnosis",
        methodology="Transformer classification",
        key_findings="94.8% accuracy achieved",
        limitations="Edge latency",
        future_scope="On-device quantization",
    )

    response = client.post(
        "/api/v1/parse",
        files={"file": ("sample.pdf", sample_pdf_bytes, "application/pdf")},
        data={"fingerprint": "test_device_123"},
    )

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["remaining_credits"] == 2
    assert res_data["data"]["title"] == "Deep Learning in Healthcare"


def test_export_excel_stream(client):
    """Verifies in-memory Excel streaming response."""
    payload = {
        "format": "xlsx",
        "rows": [
            {
                "title": "Sample Paper",
                "authors": "Author A",
                "year": "2023",
                "problem_statement": "Problem",
                "methodology": "Method",
                "key_findings": "Findings",
                "limitations": "None",
                "future_scope": "Future",
            }
        ],
    }
    response = client.post("/api/v1/export/excel", json=payload)
    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment; filename=literature_survey_matrix.xlsx" in response.headers.get(
        "content-disposition", ""
    )


def test_export_latex_stream(client):
    """Verifies in-memory LaTeX streaming response."""
    payload = {
        "format": "latex",
        "rows": [
            {
                "title": "Sample Paper",
                "authors": "Author A",
                "year": "2023",
                "problem_statement": "Problem",
                "methodology": "Method",
                "key_findings": "Findings",
                "limitations": "None",
                "future_scope": "Future",
            }
        ],
    }
    response = client.post("/api/v1/export/latex", json=payload)
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "\\begin{table*}" in response.text