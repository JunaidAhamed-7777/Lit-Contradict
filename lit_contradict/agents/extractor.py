"""ExtractorAgent: Extracts atomic scientific claims from paper sections."""

from typing import List, Optional
from lit_contradict.core.schemas import Claim, Paper, ContradictionType


class ExtractorAgent:
    """Extracts atomic scientific claims from a Paper object's structured sections."""

    # Standard academic section order for claim extraction
    SECTION_ORDER = ["Abstract", "Methods", "Results", "Discussion"]

    # Keywords/patterns that indicate different claim types
    EMPIRICAL_KEYWORDS = ["showed", "demonstrated", "found", "reduced", "increased", "effect", "effectiveness"]
    METHODOLOGICAL_KEYWORDS = ["method", "protocol", "approach", "methodology", "procedure"]
    THEORETICAL_KEYWORDS = ["theory", "framework", "model", "implies", "suggests", "postulates"]

    def extract(self, paper: Paper) -> List[Claim]:
        """Extract atomic scientific claims from all paper sections.

        Iterates through structured sections (Abstract, Methods, Results, Discussion)
        and extracts discrete claims instead of broad section summaries.

        Args:
            paper: The Paper instance to extract claims from.

        Returns:
            A list of Claim objects extracted from the paper, each containing:
            - paper_id: The source paper ID
            - claim_text: The normalized claim text
            - exact_quote: A direct quote from the paper supporting the claim
            - section_name: Which section the claim came from
            - methodology_context: Context about the methodology used
            - confidence_score: Extracted confidence (0.0-1.0)
        """
        claims: List[Claim] = []

        # Process sections in logical order
        sections_to_process = self._get_sections_in_order(paper)

        for section_name in sections_to_process:
            section_text = paper.get_section_text(section_name)
            if not section_text or not section_text.strip():
                continue

            # Extract 3-5 atomic claims per section
            section_claims = self._extract_claims_from_text(
                section_text, section_name, paper.id
            )
            claims.extend(section_claims)

        return claims

    def _get_sections_in_order(self, paper: Paper) -> List[str]:
        """Get paper sections in extraction order, falling back to available sections."""
        ordered: List[str] = []
        for sec in self.SECTION_ORDER:
            if sec in paper.sections:
                ordered.append(sec)
        # Add any remaining sections not in the standard order
        for sec in paper.sections:
            if sec not in ordered:
                ordered.append(sec)
        return ordered if ordered else ["Abstract"]

    def _extract_claims_from_text(
        self, text: str, section_name: str, paper_id: str
    ) -> List[Claim]:
        """Extract atomic claims from a single section's text.

        Uses sentence splitting and keyword detection to isolate distinct
        empirical findings, methodological setups, and theoretical conclusions.

        Args:
            text: The section text to extract claims from.
            section_name: The name of the section (e.g., "Results").
            paper_id: The source paper's ID.

        Returns:
            A list of Claim objects extracted from the text.
        """
        claims: List[Claim] = []
        sentences = [s.strip() for s in text.split(". ") if s.strip()]

        for sentence in sentences:
            if len(sentence) < 20:  # Skip very short sentences
                continue

            normalized = self._normalize_text(sentence)

            # Determine claim type based on keywords
            claim_type = self._detect_claim_type(normalized)

            # Extract methodology context from the section
            methodology_context = self._extract_methodology_context(
                section_name, text
            )

            # Compute confidence based on sentence characteristics
            confidence = self._compute_confidence(sentence, claim_type)

            # Use the sentence itself as the exact_quote, truncated if needed
            exact_quote = sentence[:200] if len(sentence) > 200 else sentence

            claim = Claim(
                id=f"claim-{paper_id}-{section_name}-{len(claims)}",
                paper_id=paper_id,
                exact_quote=exact_quote,
                section_name=section_name,
                normalized_claim_text=normalized,
                methodology_context=methodology_context,
                confidence_score=confidence,
            )
            claims.append(claim)

        # If no claims were extracted via sentence splitting, fall back to
        # a single claim from the full section text
        if not claims and text.strip():
            claim = Claim(
                id=f"claim-{paper_id}-{section_name}-0",
                paper_id=paper_id,
                exact_quote=text[:200],
                section_name=section_name,
                normalized_claim_text=self._normalize_text(text),
                methodology_context=self._extract_methodology_context(
                    section_name, text
                ),
                confidence_score=0.5,
            )
            claims.append(claim)

        return claims

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize claim text by lowercasing, removing extra whitespace, and stripping punctuation."""
        import re
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s]", "", text)
        return text

    def _detect_claim_type(self, normalized: str) -> str:
        """Detect the type of claim: empirical, methodological, or theoretical."""
        if any(kw in normalized for kw in self.EMPIRICAL_KEYWORDS):
            return "empirical"
        if any(kw in normalized for kw in self.METHODOLOGICAL_KEYWORDS):
            return "methodological"
        if any(kw in normalized for kw in self.THEORETICAL_KEYWORDS):
            return "theoretical"
        return "empirical"  # default

    def _extract_methodology_context(self, section_name: str, text: str) -> Optional[str]:
        """Extract methodology context from a section.

        Args:
            section_name: The section name (e.g., "Methods").
            text: The full section text.

        Returns:
            A brief description of the methodology context, or None if not applicable.
        """
        if section_name == "Methods":
            # Extract key methodological phrases
            import re
            methods_patterns = re.findall(
                r"(?i)(?:we used|we tested|we analyzed|employed|utilized)\s+(\w+(?:\s+\w+){0,4})",
                text,
            )
            if methods_patterns:
                return "; ".join(methods_patterns[:3])
        elif section_name == "Results":
            # Methodology context in results refers to what was measured
            import re
            measures = re.findall(r"(?i)(measured|observed|tracked)\s+(\w+(?:\s+\w+)*)", text)
            if measures:
                return "; ".join(f"{m[0]} {m[1]}" for m in measures[:3])
        return None

    @staticmethod
    def _compute_confidence(sentence: str, claim_type: str) -> float:
        """Compute a confidence score (0.0-1.0) for the extracted claim.

        Longer sentences with more specific details receive higher confidence.
        """
        base = 0.5
        # Length factor: longer sentences with more detail = higher confidence
        length_factor = min(len(sentence) / 200, 0.3)
        # Keyword presence factor
        keyword_factor = 0.2 if claim_type != "empirical" else 0.1
        # Cap at 1.0
        return round(base + length_factor + keyword_factor, 2)