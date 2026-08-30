import os
import pymupdf
from lit_contradict.core.schemas import Paper

class PDFParser:
    """Extracts text content from local PDF files using PyMuPDF."""

    def parse(self, pdf_path: str) -> Paper:
        resolved_path = pdf_path

        # If file is not in root, check common subdirectories
        if not os.path.exists(resolved_path):
            possible_dirs = ["data", "eval", "tests", "sample_data"]
            for d in possible_dirs:
                candidate = os.path.join(d, os.path.basename(pdf_path))
                if os.path.exists(candidate):
                    resolved_path = candidate
                    break

        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"PDF file not found at path: {pdf_path} (also checked subdirectories)")

        doc = pymupdf.open(resolved_path)
        full_text = []

        for page in doc:
            full_text.append(page.get_text("text"))

        doc.close()

        extracted_text = "\n\n".join(full_text)
        return Paper(id=resolved_path, full_text=extracted_text)