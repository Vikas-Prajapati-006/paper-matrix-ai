from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class PaperMatrixRow(BaseModel):
    """Structured extraction format for a single academic paper with dynamic key support."""
    model_config = ConfigDict(extra="allow")

    title: str = Field(default="Untitled Paper", description="Title of the research paper")
    authors: str = Field(default="N/A", description="Comma-separated authors or lead author et al.")
    year: Any = Field(default="N/A", description="Publication year")
    problem_statement: str = Field(default="N/A", description="Core problem or research gap being addressed")
    methodology: str = Field(default="N/A", description="Models, datasets, algorithms, or experimental setup used")
    key_findings: str = Field(default="N/A", description="Primary quantitative results or empirical conclusions")
    limitations: str = Field(default="Not explicitly stated", description="Reported shortcomings or constraints")
    future_scope: str = Field(default="Not specified", description="Proposed future directions")


class ParseResponse(BaseModel):
    """API response model after processing and analyzing a paper."""
    model_config = ConfigDict(extra="allow")

    status: str = "success"
    filename: str
    remaining_credits: int
    data: Union[PaperMatrixRow, Dict[str, Any]]


class QuotaStatusResponse(BaseModel):
    """Response model for device credit status check."""
    model_config = ConfigDict(extra="ignore")

    fingerprint: str
    remaining_credits: int
    ttl_seconds: int = 86400


class ExportRequest(BaseModel):
    """Payload containing rows to format into Excel or LaTeX."""
    model_config = ConfigDict(extra="ignore")

    format: Optional[str] = Field(default="xlsx", description="Export format: 'xlsx' or 'latex'")
    columns: Optional[List[str]] = Field(default=None, description="Optional custom ordered column headers")
    prose: Optional[str] = Field(default=None, description="Optional synthesized prose for unified LaTeX export")
    rows: List[Union[PaperMatrixRow, Dict[str, Any]]] = Field(default_factory=list)


# --- NAYA SCHEMA ADDITION (Purana code untouched) ---
class ProseSynthesisRequest(BaseModel):
    """Payload to generate an academic Related Work section from matrix rows."""
    model_config = ConfigDict(extra="ignore")
    rows: List[Union[PaperMatrixRow, Dict[str, Any]]] = Field(default_factory=list)


class ProseSynthesisResponse(BaseModel):
    """Generated Related Work prose response."""
    status: str = "success"
    prose: str


# --- CONTACT SCHEMA (Added for secure user inquiries) ---
class ContactMessageRequest(BaseModel):
    """Validated payload for incoming user contact & feedback messages."""
    model_config = ConfigDict(extra="ignore")

    email: EmailStr = Field(..., max_length=150, description="User's contact email")
    subject: str = Field(default="feedback", max_length=50, description="Inquiry category")
    message: str = Field(..., min_length=5, max_length=2500, description="Inquiry content")
    honeypot: Optional[str] = Field(default="", max_length=100, description="Anti-spam bot trap")


class ContactMessageResponse(BaseModel):
    """Response status for contact form submission."""
    status: str = "success"
    message: str