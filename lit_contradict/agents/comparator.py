"""ComparatorAgent: Compares claims across papers to detect contradictions."""

from typing import List, Dict, Any, Optional
from lit_contradict.core.schemas import Claim, Contradiction, ContradictionType


class ComparatorAgent:
    """Compares pairs of claims from different papers to detect contradictions."""

    # If claims share at least this many words, consider them for contradiction
    SHARED_WORD_THRESHOLD = 2

    def compare_claims(
        self,
        claim_a: Claim,
        claim_b: Claim,
    ) -> Optional[Contradiction]:
        """Compare two claims and return a contradiction if detected.

        Analyzes claim pairs for logical, empirical, methodological, or theoretical
        contradictions based on normalized claim text, exact quotes, and methodology context.

        Args:
            claim_a: First claim to compare.
            claim_b: Second claim to compare.

        Returns:
            A Contradiction object if a contradiction is detected, None otherwise.
        """
        # Normalize both claims for comparison
        norm_a = claim_a.normalized_claim_text
        norm_b = claim_b.normalized_claim_text

        # Check for shared words - if claims share words, they're about the same topic
        # and can be contradictory
        words_a = set(norm_a.split())
        words_b = set(norm_b.split())
        shared_words = words_a.intersection(words_b)

        # If claims share at least the threshold number of words, they're about
        # the same topic and can be contradictory
        if len(shared_words) < self.SHARED_WORD_THRESHOLD:
            return None

        # Determine contradiction type based on shared word content
        contradiction_type = self._classify_contradiction_type(norm_a, norm_b)

        if contradiction_type is None:
            return None

        # Generate explanation based on the contradiction type
        explanation = self._generate_explanation(norm_a, norm_b, contradiction_type)

        # Compute confidence score
        confidence = self._compute_contradiction_confidence(len(shared_words))

        # Determine evidence level
        evidence_level = self._determine_evidence_level(len(shared_words))

        contradiction = Contradiction(
            id=f"contradiction-{claim_a.id}-{claim_b.id}",
            claim_a_id=claim_a.id,
            claim_a_quote=claim_a.exact_quote,
            claim_b_id=claim_b.id,
            claim_b_quote=claim_b.exact_quote,
            contradiction_type=contradiction_type,
            confidence_score=confidence,
            explanation=explanation,
            evidence_level=evidence_level,
        )

        return contradiction

    @staticmethod
    def _classify_contradiction_type(norm_a: str, norm_b: str) -> Optional[ContradictionType]:
        """Classify the type of contradiction between two claims based on shared words."""

        a_lower = norm_a.lower()
        b_lower = norm_b.lower()

        # Check for empirical contradictions (numeric metrics, results)
        empirical_keywords = ["result", "showed", "percentage", "rate", "found", "studied",
                              "trial", " experiment", "data", "measure"]
        a_has_empirical = any(kw in a_lower for kw in empirical_keywords)
        b_has_empirical = any(kw in b_lower for kw in empirical_keywords)

        # Check for methodological keywords
        methodological_keywords = ["method", "protocol", "approach", "procedure", "bootstrap",
                                   "randomized", "double-blind"]
        a_has_method = any(kw in a_lower for kw in methodological_keywords)
        b_has_method = any(kw in b_lower for kw in methodological_keywords)

        # Check for theoretical keywords
        theoretical_keywords = ["theory", "framework", "model", "assumes", "postulates",
                                "implies", "philosophy"]
        a_has_theory = any(kw in a_lower for kw in theoretical_keywords)
        b_has_theory = any(kw in b_lower for kw in theoretical_keywords)

        # Empirical vs Empirical: conflicting results
        if a_has_empirical and b_has_empirical:
            return ContradictionType.Empirical

        # Methodological vs Methodological: different procedures
        if a_has_method and b_has_method:
            return ContradictionType.Methodological

        # Theoretical vs Theoretical: different frameworks
        if a_has_theory and b_has_theory:
            return ContradictionType.Theoretical

        # Cross-type: if one is empirical and another is methodological/theoretical
        if a_has_empirical and (b_has_method or b_has_theory):
            return ContradictionType.Methodological if b_has_method else ContradictionType.Theoretical
        if a_has_method and b_has_empirical:
            return ContradictionType.Methodological
        if a_has_method and b_has_theory:
            return ContradictionType.Theoretical
        if a_has_theory and b_has_empirical:
            return ContradictionType.Theoretical
        if a_has_theory and b_has_method:
            return ContradictionType.Theoretical

        # Default: methodological if both have procedure-related words
        if a_has_method or b_has_method:
            return ContradictionType.Methodological

        # Default to empirical
        return ContradictionType.Empirical

    @staticmethod
    def _generate_explanation(norm_a: str, norm_b: str, contradiction_type: ContradictionType) -> str:
        """Generate a human-readable explanation for the contradiction."""
        a_words = set(norm_a.split())
        b_words = set(norm_b.split())
        shared = a_words.intersection(b_words)
        shared_str = ", ".join(list(shared)[:3])

        if contradiction_type == ContradictionType.Empirical:
            return f"Conflicting empirical findings share keywords: {shared_str}. " \
                   f"Claims differ in their reported results or metrics."
        elif contradiction_type == ContradictionType.Methodological:
            return f"Methodological disagreement based on shared approach: {shared_str}. " \
                   f"Claims differ in their described procedures or protocols."
        else:
            return f"Theoretical disagreement based on shared concept: {shared_str}. " \
                   f"Claims differ in their underlying assumptions or frameworks."

    @staticmethod
    def _compute_contradiction_confidence(shared_count: int) -> float:
        """Compute confidence score based on number of shared words.

        More shared words = higher confidence that these are genuinely
        related claims that could be contradictory.
        """
        # Base confidence + boost for more shared words
        # 2 shared words -> 0.6, 3 -> 0.7, 4+ -> 0.8
        base = 0.5
        boost = min(shared_count - 1, 3) * 0.1
        return round(min(base + boost, 0.9), 2)

    @staticmethod
    def _determine_evidence_level(shared_count: int) -> str:
        """Determine evidence level based on shared word count."""
        if shared_count >= 3:
            return "high"
        elif shared_count >= 2:
            return "medium"
        else:
            return "low"

    def find_contradictions(
        self,
        claims_by_paper: Dict[str, List[Claim]],
    ) -> List[Contradiction]:
        """Find all contradictions across papers' claims.

        Args:
            claims_by_paper: Mapping of paper_id to list of Claim objects.

        Returns:
            A list of detected Contradiction objects.
        """
        contradictions: List[Contradiction] = []
        paper_ids = list(claims_by_paper.keys())

        for i in range(len(paper_ids)):
            for j in range(i + 1, len(paper_ids)):
                claims_i = claims_by_paper[paper_ids[i]]
                claims_j = claims_by_paper[paper_ids[j]]
                for claim_a in claims_i:
                    for claim_b in claims_j:
                        contradiction = self.compare_claims(claim_a, claim_b)
                        if contradiction is not None:
                            contradictions.append(contradiction)

        return contradictions