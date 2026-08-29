"""Text processing modules for normalizing and preprocessing paper text."""

import re
from typing import List, Optional
from lit_contradict.core.schemas import Claim


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    return re.sub(r"\s+", " ", text).strip()


def normalize_claim_text(text: str) -> str:
    """Normalize claim text for comparison purposes."""
    text = normalize_whitespace(text)
    text = text.lower()
    # Remove punctuation for normalized comparison
    text = re.sub(r"[^\w\s]", "", text)
    return text


def extract_claims_from_text(text: str, source_id: str) -> List[Claim]:
    """Extract claims from raw paper text.

    Args:
        text: Raw text from a paper section.
        source_id: Identifier of the source paper.

    Returns:
        A list of Claim objects extracted from the text.
    """
    normalized = normalize_claim_text(text)
    # Placeholder: split by sentence and create claims
    sentences = [s.strip() for s in normalized.split(".") if s.strip()]
    claims = []
    for i, sentence in enumerate(sentences[:10]):  # Limit for placeholder
        claim = Claim(
            id=f"{source_id}-claim-{i}",
            paper_id=source_id,
            exact_quote=sentence,
            section_name="unknown",
            normalized_claim_text=normalized,
            methodology_context=None,
        )
        claims.append(claim)
    return claims