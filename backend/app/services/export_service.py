import io
import re
import pandas as pd
from typing import List, Optional, Any, Union
from app.models.schema import PaperMatrixRow


class ExportService:
    @staticmethod
    def sanitize_latex(text: str) -> str:
        """Sanitizes text against Unicode artifacts, reserved LaTeX characters, and unescaped breaks."""
        if not text:
            return ""
        val = str(text)

        # 1. Strip raw internal newlines so tabular row parsing never breaks
        val = val.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")

        # 2. Convert smart/curly quotes to standard LaTeX format
        val = val.replace("“", "``").replace("”", "''")
        val = val.replace("‘", "`").replace("’", "'")

        # 3. Unicode ligatures and spaces that crash pdflatex
        val = val.replace("Ł", r"\L{}").replace("ł", r"\l{}")
        val = val.replace("\u2011", "-")   # Non-breaking hyphen
        val = val.replace("\u2013", "--")  # En-dash
        val = val.replace("\u2014", "---") # Em-dash
        val = val.replace("\u202f", " ")   # Narrow no-break space
        val = val.replace("\u00a0", " ")   # Non-breaking space

        # 4. Reserved LaTeX syntax escaping (Order matters: reserved chars escaped directly)
        replacements = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }

        # Safe regex mapping to avoid double-escaping
        pattern = re.compile("|".join(re.escape(k) for k in replacements.keys()))
        val = pattern.sub(lambda m: replacements[m.group(0)], val)

        # Clean multiple whitespaces
        val = re.sub(r"\s+", " ", val).strip()

        return val

    @staticmethod
    def generate_excel(rows: List[Union[PaperMatrixRow, Any]]) -> io.BytesIO:
        """Converts extracted rows to an in-memory formatted Excel document."""
        data = [row.model_dump() if hasattr(row, "model_dump") else row for row in rows]
        df = pd.DataFrame(data)

        # Rename columns to publication-ready headers
        column_mapping = {
            "title": "Paper Title",
            "authors": "Authors",
            "year": "Year",
            "problem_statement": "Problem Statement / Gap",
            "methodology": "Proposed Methodology",
            "key_findings": "Key Findings / Results",
            "limitations": "Limitations",
            "future_scope": "Future Scope"
        }
        df.rename(columns=column_mapping, inplace=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Literature Survey")

            # Auto-fit column widths
            worksheet = writer.sheets["Literature Survey"]
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

        output.seek(0)
        return output

    @staticmethod
    def generate_latex(rows: List[Union[PaperMatrixRow, Any]], prose: Optional[str] = None) -> io.BytesIO:
        """Converts matrix rows to academic LaTeX tabular code, bundling synthesized prose if provided."""
        latex_lines = []

        # Agar auto-drafted prose exist karta hai toh use Section 2 banakar add karo
        if prose and prose.strip():
            safe_prose = prose.strip()
            # Markdown bold tags ko LaTeX bold format me map karna
            safe_prose = safe_prose.replace("**Related Work**", r"\section{Related Work}").replace("**Research Gaps**", r"\subsection{Identified Research Gaps}")
            safe_prose = safe_prose.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
            latex_lines.extend([
                r"\section{Literature Review \& Related Work}",
                safe_prose,
                r"\vspace{1.5em}",
                r"\subsection{Literature Survey Matrix}",
                ""
            ])

        latex_lines.extend([
            r"\begin{table*}[t]",
            r"\centering",
            r"\caption{Comprehensive Literature Survey Matrix}",
            r"\label{tab:lit_survey}",
            r"\resizebox{\textwidth}{!}{%",
            r"\begin{tabular}{|p{3.5cm}|p{2cm}|p{1.2cm}|p{4.5cm}|p{4.5cm}|p{3.5cm}|}",
            r"\hline",
            r"\textbf{Title} & \textbf{Authors} & \textbf{Year} & \textbf{Methodology} & \textbf{Key Findings} & \textbf{Limitations} \\ \hline"
        ])

        for row in rows:
            r_title = getattr(row, "title", row.get("title", "")) if not isinstance(row, PaperMatrixRow) else row.title
            r_authors = getattr(row, "authors", row.get("authors", "")) if not isinstance(row, PaperMatrixRow) else row.authors
            r_year = getattr(row, "year", row.get("year", "")) if not isinstance(row, PaperMatrixRow) else row.year
            r_method = getattr(row, "methodology", row.get("methodology", "")) if not isinstance(row, PaperMatrixRow) else row.methodology
            r_findings = getattr(row, "key_findings", row.get("key_findings", "")) if not isinstance(row, PaperMatrixRow) else row.key_findings
            r_limits = getattr(row, "limitations", row.get("limitations", "")) if not isinstance(row, PaperMatrixRow) else row.limitations

            title = ExportService.sanitize_latex(r_title)
            authors = ExportService.sanitize_latex(r_authors)
            year = ExportService.sanitize_latex(r_year)
            method = ExportService.sanitize_latex(r_method)
            findings = ExportService.sanitize_latex(r_findings)
            limits = ExportService.sanitize_latex(r_limits)

            latex_lines.append(
                f"{title} & {authors} & {year} & {method} & {findings} & {limits} \\\\ \\hline"
            )

        latex_lines.extend([
            r"\end{tabular}%",
            r"}",
            r"\end{table*}"
        ])

        output = io.BytesIO("\n".join(latex_lines).encode("utf-8"))
        output.seek(0)
        return output

    @staticmethod
    def generate_bibtex(rows: List[Union[PaperMatrixRow, Any]]) -> str:
        """Generates standard BibTeX references from matrix rows."""
        bib_entries = []
        for row in rows:
            data = row if isinstance(row, dict) else (row.model_dump() if hasattr(row, "model_dump") else row.__dict__)
            title = data.get("title", "Untitled Document")
            authors = data.get("authors", "Unknown Authors")
            year = data.get("year", "N/A")

            # Clean citation key e.g. vaswani2017
            first_word = re.sub(r'[^a-zA-Z0-9]', '', str(title).split()[0].lower()) if str(title).split() else "paper"
            safe_year = re.sub(r'[^0-9]', '', str(year)) or "nd"
            cite_key = f"{first_word}_{safe_year}"

            entry = (
                f"@article{{{cite_key},\n"
                f"  title = {{{title}}},\n"
                f"  author = {{{authors}}},\n"
                f"  year = {{{year}}}\n"
                f"}}"
            )
            bib_entries.append(entry)
        return "\n\n".join(bib_entries)


export_service = ExportService()