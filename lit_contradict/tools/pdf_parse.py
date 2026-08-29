"""PDF parsing modules for extracting text content."""

import pdfplumber
from pypdf import PdfReader
from typing import Dict, List, Optional
from lit_contradict.core.schemas import Paper


class PDFParser:
    """Parses PDF files and extracts text content."""

    def __init__(self):
        pass

    def parse(self, pdf_path: str) -> Paper:
        """Parse a PDF file and return a Paper object.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            A Paper object populated with extracted content.
        """
        reader = PdfReader(pdf_path)
        full_text = ""
        sections: Dict[str, str] = {}

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        # Simple section detection based on common academic section headers
        # In production, this would use more sophisticated section segmentation
        return Paper(
            id="",
            title="",
            authors=[],
            abstract="",
            sections=sections,
            full_text=full_text,
        )

    def parse_with_pdfplumber(self, pdf_path: str) -> Paper:
        """Parse PDF using pdfplumber for potentially better text extraction.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            A Paper object populated with extracted content.
        """
        paper = Paper(id="", title="", authors=[], abstract="", sections={})
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    paper.full_text += text + "\n"
        return paper