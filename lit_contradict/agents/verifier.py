"""VerifierAgent: Audits flagged contradictions against raw text quotes."""

from typing import List, Dict, Any, Optional
from lit_contradict.core.schemas import Claim, Contradiction


class VerifierAgent:
    """Verifies detected contradictions against source text to prevent hallucinations.

    Validates each candidate contradiction directly against the source paper quotes
    in claim_a.exact_quote and claim_b.exact_quote. Strips out false positives and
    low-confidence/hallucinated contradictions. Assigns a final confidence_score and
    evidence_level to confirmed contradictions.
    """

    def verify(self, contradiction: Contradiction, claim_a: Claim, claim_b: Claim) -> dict:
        """Verify a contradiction claim against source documents.

        Cross-references the contradiction's quotes against the actual source text
        to validate that the contradiction is genuinely supported by the evidence.

        Args:
            contradiction: The Contradiction to verify.
            claim_a: The source Claim object for claim_a.
            claim_b: The source Claim object for claim_b.

        Returns:
            A dict with verification status and confidence adjustment.
        """
        # Step 1: Check that both exact quotes actually exist in the source text
        quote_a_valid = self._quote_exists_in_context(contradiction.claim_a_quote, claim_a)
        quote_b_valid = self._quote_exists_in_context(contradiction.claim_b_quote, claim_b)

        if not quote_a_valid or not quote_b_valid:
            return {
                "is_valid": False,
                "confidence_adjustment": -0.5,
                "evidence_notes": "Failed quote validation: one or both quotes not found in source text",
            }

        # Step 2: Verify the contradiction type is supported by the quotes
        type_valid = self._validate_contradiction_type(
            contradiction.contradiction_type, claim_a, claim_b
        )

        if not type_valid:
            return {
                "is_valid": False,
                "confidence_adjustment": -0.3,
                "evidence_notes": "Failed type validation: contradiction type not supported by quote content",
            }

        # Step 3: Verify methodological/contextual consistency
        context_valid = self._validate_context_consistency(claim_a, claim_b)

        if not context_valid:
            return {
                "is_valid": False,
                "confidence_adjustment": -0.2,
                "evidence_notes": "Failed context validation: claims from incompatible contexts",
            }

        # Step 4: Compute final confidence score
        # Start from the contradiction's confidence_score, adjust based on verification
        final_confidence = self._compute_final_confidence(contradiction.confidence_score)

        # Step 5: Determine evidence level
        evidence_level = self._determine_evidence_level(
            final_confidence, quote_a_valid, quote_b_valid
        )

        # Step 6: Generate evidence notes
        evidence_notes = self._generate_evidence_notes(
            claim_a, claim_b, contradiction
        )

        return {
            "is_valid": True,
            "confidence_adjustment": 0.0,
            "evidence_level": evidence_level,
            "evidence_notes": evidence_notes,
            "final_confidence": final_confidence,
        }

    def _quote_exists_in_context(self, quote: str, claim: Claim) -> bool:
        """Check if the quoted text exists in the claim's source context.

        Args:
            quote: The quote text to check.
            claim: The Claim object containing the source paper information.

        Returns:
            True if the quote appears in the claim's source text, False otherwise.
        """
        if not quote:
            return False

        # The claim should have access to the source paper's full text or section text
        # For now, check if the quote text appears in the normalized claim text
        # or is a substring of the exact_quote
        if quote in claim.exact_quote:
            return True

        # Also check if key phrases from the quote are in the claim text
        quote_words = set(quote.lower().split())
        claim_words = set(claim.normalized_claim_text.lower().split())

        # If more than 50% of quote words appear in the claim, consider it valid
        if len(quote_words) > 0 and len(quote_words & claim_words) / len(quote_words) > 0.5:
            return True

        return False

    def _validate_contradiction_type(
        self, contradiction_type: str, claim_a: Claim, claim_b: Claim
    ) -> bool:
        """Validate that the contradiction type is supported by the claim content."""
        a_norm = claim_a.normalized_claim_text.lower()
        b_norm = claim_b.normalized_claim_text.lower()

        type_validators = {
            "empirical": self._empirical_type_valid,
            "methodological": self._methodological_type_valid,
            "theoretical": self._theoretical_type_valid,
        }

        validator = type_validators.get(contradiction_type)
        if validator is None:
            return False

        return validator(a_norm, b_norm)

    @staticmethod
    def _empirical_type_valid(a_norm: str, b_norm: str) -> bool:
        """Validate empirical contradiction type."""
        # Empirical claims should contain metrics, results, or outcome measures
        empirical_keywords = ["result", "showed", "measured", "percentage", "rate", "found"]
        a_has_empirical = any(kw in a_norm for kw in empirical_keywords)
        b_has_empirical = any(kw in b_norm for kw in empirical_keywords)
        return a_has_empirical or b_has_empirical

    @staticmethod
    def _methodological_type_valid(a_norm: str, b_norm: str) -> bool:
        """Validate methodological contradiction type."""
        methodological_keywords = ["method", "protocol", "procedure", "methodology", "approach"]
        a_has_method = any(kw in a_norm for kw in methodological_keywords)
        b_has_method = any(kw in b_norm for kw in methodological_keywords)
        return a_has_method or b_has_method

    @staticmethod
    def _theoretical_type_valid(a_norm: str, b_norm: str) -> bool:
        """Validate theoretical contradiction type."""
        theoretical_keywords = ["theory", "framework", "model", "assumes", "postulates", "implies"]
        a_has_theory = any(kw in a_norm for kw in theoretical_keywords)
        b_has_theory = any(kw in b_norm for kw in theoretical_keywords)
        return a_has_theory or b_has_theory

    def _validate_context_consistency(self, claim_a: Claim, claim_b: Claim) -> bool:
        """Validate that claims are from compatible contexts.

        Two claims can be contradictory only if they come from comparable contexts
        (e.g., same patient population, same experimental setup, same domain).
        """
        # Check if both claims have methodology context
        a_method = claim_a.methodology_context or ""
        b_method = claim_b.methodology_context or ""

        if not a_method and not b_method:
            # No methodology context available - assume compatible for now
            return True

        # If both have methodology context, check for incompatibility
        if a_method and b_method:
            # If methodologies are completely different domains, flag as incompatible
            a_domain = self._extract_domain(a_method)
            b_domain = self._extract_domain(b_method)

            if a_domain and b_domain and a_domain != b_domain:
                return False  # Incompatible domains

        return True

    @staticmethod
    def _extract_domain(methodology: str) -> Optional[str]:
        """Extract the research domain from methodology text."""
        domain_keywords = {
            "medical": ["patient", "clinical", "trial", "treatment"],
            "chemical": ["catalyst", "reaction", "synthesis", "solvent"],
            "biological": ["protein", "enzyme", "cell", "organism"],
            "physical": ["temperature", "pressure", "efficiency", "performance"],
        }

        methodology_lower = methodology.lower()
        for domain, keywords in domain_keywords.items():
            if any(kw in methodology_lower for kw in keywords):
                return domain
        return None

    def _compute_final_confidence(self, base_confidence: float) -> float:
        """Compute the final verified confidence score.

        Adjusts the base confidence based on verification success.
        Verified contradictions maintain or slightly increase confidence.
        """
        # Verified contradictions keep a high base, with minor adjustment
        return round(min(base_confidence + 0.05, 1.0), 2)

    @staticmethod
    def _determine_evidence_level(
        confidence: float, quote_a_valid: bool, quote_b_valid: bool
    ) -> str:
        """Determine the evidence level for the verified contradiction."""
        if confidence >= 0.8 and quote_a_valid and quote_b_valid:
            return "high"
        elif confidence >= 0.5 or (quote_a_valid and quote_b_valid):
            return "medium"
        else:
            return "low"

    def _generate_evidence_notes(
        self, claim_a: Claim, claim_b: Claim, contradiction: object
    ) -> str:
        """Generate human-readable evidence notes for the verified contradiction.

        Args:
            claim_a: The first source claim.
            claim_b: The second source claim.
            contradiction: The verified contradiction object.

        Returns:
            A string describing the evidence supporting the contradiction.
        """
        notes_parts = []

        # Source paper information
        notes_parts.append(
            f"Source A: {claim_a.paper_id} ({claim_a.section_name})"
        )
        notes_parts.append(
            f"Source B: {claim_b.paper_id} ({claim_b.section_name})"
        )

        # Contradiction type
        notes_parts.append(
            f"Contradiction type: {contradiction.contradiction_type}"
        )

        # Quote references
        a_quote_ref = claim_a.exact_quote[:60] + "..." if len(claim_a.exact_quote) > 60 else claim_a.exact_quote
        b_quote_ref = claim_b.exact_quote[:60] + "..." if len(claim_b.exact_quote) > 60 else claim_b.exact_quote
        notes_parts.append(f"Quote A: {a_quote_ref}")
        notes_parts.append(f"Quote B: {b_quote_ref}")

        return " | ".join(notes_parts)