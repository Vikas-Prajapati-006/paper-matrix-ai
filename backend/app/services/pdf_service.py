import fitz  # PyMuPDF
import re
from app.core.errors import ParsingException
from app.core.logger import logger


class PDFExtractionService:
    @staticmethod
    def extract_targeted_text(pdf_bytes: bytes, max_pages: int = 12) -> str:
        """Parses raw PDF bytes in-memory and extracts high-signal research sections."""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            
            if total_pages == 0:
                raise ParsingException("Uploaded PDF file is completely empty.")

            # Process up to max_pages to avoid token bloat
            pages_to_read = min(total_pages, max_pages)
            extracted_pages = []

            for page_num in range(pages_to_read):
                page = doc[page_num]
                text = page.get_text("text")
                if text.strip():
                    extracted_pages.append(text)

            doc.close()
            full_raw_text = "\n\n".join(extracted_pages)

            if not full_raw_text.strip():
                raise ParsingException("Could not extract readable text from PDF (scanned/rasterized).")

            cleaned_text = PDFExtractionService._clean_and_truncate(full_raw_text)
            return cleaned_text

        except ParsingException:
            raise
        except Exception as exc:
            logger.error(f"Error during PDF processing: {exc}")
            raise ParsingException(f"Failed to parse PDF document structure: {str(exc)}")

    @staticmethod
    def _clean_and_truncate(text: str, max_chars: int = 18000) -> str:
        """Removes duplicate whitespaces, cuts references/bibliography, and truncates."""
        # 1. Truncate at References/Bibliography section if present
        ref_split = re.split(r'\n(?:\d+[\.\s]+)?(?:REFERENCES|BIBLIOGRAPHY|References|Bibliography)\b', text)
        primary_text = ref_split[0]

        # 2. Normalize whitespace and clean junk symbols
        cleaned = re.sub(r'[ \t]+', ' ', primary_text)
        cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)

        # 3. Limit characters to fit within Groq context window easily
        return cleaned[:max_chars].strip()


pdf_service = PDFExtractionService()