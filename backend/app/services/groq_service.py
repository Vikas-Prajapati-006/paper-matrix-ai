import json
from typing import List, Optional, Dict, Any
from groq import Groq
from app.core.config import settings
from app.core.errors import ExtractionLLMException
from app.core.logger import logger
from app.models.schema import PaperMatrixRow

DEFAULT_MATRIX_COLUMNS = [
    "title",
    "authors",
    "year",
    "problem_statement",
    "methodology",
    "key_findings",
    "limitations",
    "future_scope"
]


class GroqSynthesisService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def extract_paper_matrix(self, paper_text: str, custom_columns: Optional[List[str]] = None) -> PaperMatrixRow:
        """Extracts structured research matrix row using Groq JSON mode with dynamic column flexibility."""
        target_keys = custom_columns if custom_columns and len(custom_columns) > 0 else DEFAULT_MATRIX_COLUMNS

        # Strict JSON schema target generation
        schema_format = {k: f"Concise extraction for {k}" for k in target_keys}

        system_prompt = (
            "You are an expert academic research assistant specializing in literature reviews. "
            "Analyze the provided research paper excerpt and extract key details into a valid JSON object. "
            f"Your output MUST strictly be a JSON object with these target keys:\n{json.dumps(schema_format, indent=2)}\n"
            "Rules for output:\n"
            "- If any field cannot be found or is absent, populate it with 'Not explicitly stated'.\n"
            "- Never fabricate citations, metrics, or methods.\n"
            "- Output all values as clean, plain natural text strings only.\n"
            "- Do NOT inject raw LaTeX syntax, TeX tags, math mode backslashes, or formatting commands."
        )

        user_prompt = f"Research Paper Text Excerpt:\n\n{paper_text}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            raw_json = response.choices[0].message.content
            parsed_dict: Dict[str, Any] = json.loads(raw_json)

            # Ensure all requested keys are present in dictionary
            for key in target_keys:
                if key not in parsed_dict:
                    parsed_dict[key] = "Not explicitly stated"

            return PaperMatrixRow(**parsed_dict)

        except Exception as exc:
            logger.error(f"Groq matrix extraction failure: {exc}")
            raise ExtractionLLMException(f"Failed to generate structured synthesis: {str(exc)}")

    def generate_related_work_prose(self, rows: list) -> str:
        """Synthesizes extracted paper rows into a formal, publication-ready Related Work section."""
        if not rows:
            return "No papers provided to synthesize."

        context_items = []
        for idx, row in enumerate(rows, 1):
            if hasattr(row, "model_dump"):
                data = row.model_dump()
            elif hasattr(row, "dict"):
                data = row.dict()
            elif isinstance(row, dict):
                data = row
            else:
                data = getattr(row, "__dict__", {})

            context_items.append(
                f"Paper {idx}:\n"
                f"- Title: {data.get('title', 'Untitled')}\n"
                f"- Authors & Year: {data.get('authors', 'N/A')} ({data.get('year', 'N/A')})\n"
                f"- Problem: {data.get('problem_statement', 'N/A')}\n"
                f"- Methodology: {data.get('methodology', 'N/A')}\n"
                f"- Key Findings: {data.get('key_findings', 'N/A')}\n"
                f"- Limitations: {data.get('limitations', 'N/A')}\n"
            )

        context_str = "\n\n".join(context_items)

        system_prompt = (
            "You are a principal academic researcher in computer science. "
            "Write an IEEE/ACM-grade 'Related Work' synthesis section analyzing the provided research papers. "
            "Guidelines:\n"
            "1. Group papers conceptually by theme, paradigm, or lineage rather than simple disconnected summaries.\n"
            "2. Seamlessly weave in formal academic citations: e.g., Author et al. (Year).\n"
            "3. Critically contrast methodologies, trade-offs, and empirical findings.\n"
            "4. Conclude with a clear paragraph articulating the unresolved research gaps across all these works.\n"
            "5. Output clean, publication-ready academic paragraphs with no introductory conversational filler."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Synthesize these literature entries into a cohesive Related Work section:\n\n{context_str}"}
                ],
                temperature=0.2,
                max_tokens=1500
            )

            choice = response.choices[0] if response.choices else None
            content = choice.message.content if choice and choice.message else None

            if not content:
                return "Failed to synthesize literature prose: Empty response received from LLM."

            return content.strip()

        except Exception as exc:
            logger.error(f"Failed to generate related work prose: {exc}")
            raise ExtractionLLMException(f"Failed to generate synthesis prose: {str(exc)}")


groq_service = GroqSynthesisService()