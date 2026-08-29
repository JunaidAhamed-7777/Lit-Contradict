"""PDF parsing modules for extracting text content and section segmentation."""

import re
from typing import Dict, List, Optional, Tuple
from lit_contradict.core.schemas import Paper


# Standard academic section headings (regex-friendly patterns)
SECTION_PATTERNS = [
    ("Abstract", r"(?i)^abstract(\s|$|\.)"),
    ("Introduction", r"(?i)^(\s*)?introduction(\s|$|\.)"),
    ("Methods", r"(?i)^(\s*)?(methods|methodology)(\s|$|\.)"),
    ("Results", r"(?i)^(\s*)?results(\s|$|\.)"),
    ("Discussion", r"(?i)^(\s*)?discussion(\s|$|\.)"),
    ("Conclusion", r"(?i)^(\s*)?conclusion(\s|$|\.)"),
]

# Pattern to clean common PDF artifacts
ARTIFACT_PATTERNS = [
    (r"\n\s*\d+\s*$", ""),  # Trailing page numbers
    (r"^\s*\d+\s*$", ""),   # Standalone page numbers
    (r"\n+", "\n"),         # Collapse multiple newlines
    (r"[ \t]+\n", "\n"),    # Trailing spaces before newline
]


def _clean_artifacts(text: str) -> str:
    """Remove common PDF artifacts from extracted text."""
    for pattern, replacement in ARTIFACT_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    return text.strip()


def _detect_sections(text: str) -> Tuple[Dict[str, str], str]:
    """Segment raw paper text into logical sections using heading detection.

    Uses regex patterns to identify standard academic section headers
    (Abstract, Introduction, Methods, Results, Discussion, Conclusion).
    Falls back to storing full text if headings are not detected.

    Args:
        text: Raw extracted text from a PDF.

    Returns:
        A tuple of (sections_dict, full_clean_text) where sections_dict
        maps section names to their text content, and full_clean_text
        is the complete text free of artifacts.
    """
    clean_text = _clean_artifacts(text)

    # Try to detect section boundaries
    lines = clean_text.split("\n")
    sections: Dict[str, str] = {header: "" for header in [s[0] for s in SECTION_PATTERNS]}
    section_order: List[str] = []
    current_section: Optional[str] = None
    current_text_parts: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if this line matches a section heading
        detected_section = None
        for header, pattern in SECTION_PATTERNS:
            if re.search(pattern, stripped):
                detected_section = header
                break

        if detected_section:
            # Save previous section content
            if current_section and current_text_parts:
                sections[current_section] += " ".join(current_text_parts) + " "

            # Start new section
            current_section = detected_section
            section_order.append(current_section)
            current_text_parts = []
        elif current_section:
            # Accumulate text within current section
            current_text_parts.append(stripped)
        else:
            # Text before any section heading - treat as abstract precursor
            if current_section is None:
                current_section = "Abstract"
                section_order.append(current_section)
                current_text_parts.append(stripped)

    # Save last section
    if current_section and current_text_parts:
        sections[current_section] += " ".join(current_text_parts)

    # Fallback: if no sections were detected, return full text as "Abstract"
    if not any(sections.values()):
        sections = {"Abstract": clean_text}

    # Trim trailing whitespace from section texts
    for key in sections:
        sections[key] = sections[key].strip()

    return sections, clean_text


class PDFParser:
    """Parses PDF files and extracts text content with section segmentation."""

    def __init__(self):
        pass

    def parse(self, pdf_path: str) -> Paper:
        """Parse a PDF file and return a Paper object with structured sections.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            A Paper object populated with extracted content and segmented sections.
        """
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
        except ImportError:
            from pypdf import PdfReader

        full_text_parts: List[str] = []
        sections: Dict[str, str] = {}

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text_parts.append(text)

        full_text = "\n".join(full_text_parts)
        detected_sections, clean_text = _detect_sections(full_text)

        # Ensure all standard sections exist even if empty
        default_sections = {
            "Abstract": "",
            "Introduction": "",
            "Methods": "",
            "Results": "",
            "Discussion": "",
            "Conclusion": "",
        }
        for key in default_sections:
            if key not in detected_sections:
                detected_sections[key] = ""
            else:
                # Ensure all sections are present
                if key not in default_sections:
                    default_sections[key] = detected_sections.get(key, "")

        # Merge detected sections with defaults
        merged_sections = {}
        for key in default_sections:
            merged_sections[key] = detected_sections.get(key, "")

        return Paper(
            id="",
            title="",
            authors=[],
            abstract=merged_sections.get("Abstract", ""),
            sections=merged_sections,
            full_text=clean_text,
        )

    def parse_with_pdfplumber(self, pdf_path: str) -> Paper:
        """Parse PDF using pdfplumber for potentially better text extraction.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            A Paper object populated with extracted content and sections.
        """
        try:
            import pdfplumber
        except ImportError:
            import pdfplumber

        paper = Paper(id="", title="", authors=[], abstract="", sections={})
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    paper.full_text += text + "\n"

        # Apply section detection if we have text
        if paper.full_text.strip():
            detected_sections, clean_text = _detect_sections(paper.full_text)
            # Ensure all standard sections exist
            default_sections = {
                "Abstract": "",
                "Introduction": "",
                "Methods": "",
                "Results": "",
                "Discussion": "",
                "Conclusion": "",
            }
            for key in default_sections:
                paper.sections[key] = detected_sections.get(key, "")
            paper.full_text = clean_text

        return paper