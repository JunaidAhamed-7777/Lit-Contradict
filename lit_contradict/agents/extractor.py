"""ExtractorAgent: Extracts claims from paper sections."""

from typing import List, Dict, Any
from lit_contradict.core.schemas import Claim, Paper


class ExtractorAgent:
    """Extracts structured claims from a Paper object."""

    def extract(self, paper: Paper) -> List[Claim]:
        """Extract claims from all sections of a paper.

        Args:
            paper: The Paper instance to extract claims from.

        Returns:
            A list of Claim objects extracted from the paper.
        """
        claims: List[Claim] = []
        # Placeholder: In a real implementation, this would use NLP to
        # identify claim sentences across paper sections.
        for section_name, section_text in paper.sections.items():
            if section_text.strip():
                claim_id = f"claim-{paper.id}-{section_name}"
                claim = Claim(
                    id=claim_id,
                    paper_id=paper.id,
                    exact_quote=f"[Extracted from {section_name}]",
                    section_name=section_name,
                    normalized_claim_text=section_text.strip()[:200],
                    methodology_context=None,
                )
                claims.append(claim)
        return claims