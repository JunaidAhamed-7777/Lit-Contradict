"""Pipeline Orchestrator: Contradiction Detection Pipeline.

Central class that orchestrates the execution flow:
    Paper A, B → ExtractorAgent → ComparatorAgent → VerifierAgent → Final Validated Contradictions.

Handles error states, token limit safe-guards, and structured output formatting.
"""

from typing import List, Dict, Any, Optional
from lit_contradict.core.schemas import Paper, Claim, Contradiction, EvaluationResult
from lit_contradict.agents.extractor import ExtractorAgent
from lit_contradict.agents.comparator import ComparatorAgent
from lit_contradict.agents.verifier import VerifierAgent


class ContradictionPipeline:
    """Orchestrates the multi-agent contradiction detection pipeline."""

    def __init__(self, max_claims_per_paper: int = 20, max_contradictions: int = 10):
        self.extractor = ExtractorAgent()
        self.comparator = ComparatorAgent()
        self.verifier = VerifierAgent()

        self.max_claims_per_paper = max_claims_per_paper
        self.max_contradictions = max_contradictions

    def run(self, paper_a: Paper, paper_b: Paper) -> dict:
        """Run the full contradiction detection pipeline on two papers.

        Args:
            paper_a: The first Paper object.
            paper_b: The second Paper object.

        Returns:
            A dict containing:
                - contradictions: List of final validated Contradiction objects
                - total_claims_extracted: Total claims extracted from both papers
                - total_contradictions_found: Total contradictions before verification
                - verified_contradictions: Count after verification
                - execution_successful: Whether the pipeline completed without errors
                - error_message: Error message if pipeline failed, None otherwise
        """
        result: Dict[str, Any] = {
            "contradictions": [],
            "total_claims_extracted": 0,
            "total_contradictions_found": 0,
            "verified_contradictions": 0,
            "execution_successful": False,
            "error_message": None,
        }

        try:
            # Step 1: Extract claims from both papers
            claims_a = self._extract_claims_safe(paper_a)
            claims_b = self._extract_claims_safe(paper_b)

            result["total_claims_extracted"] = len(claims_a) + len(claims_b)

            if not claims_a or not claims_b:
                result["error_message"] = "Insufficient claims extracted from one or both papers"
                return result

            # Step 2: Find contradictions via pairwise comparison
            claims_dict = {paper_a.id: claims_a, paper_b.id: claims_b}
            raw_contradictions = self._find_raw_contradictions(claims_dict)

            result["total_contradictions_found"] = len(raw_contradictions)

            if not raw_contradictions:
                result["execution_successful"] = True
                return result

            # Step 3: Verify each candidate contradiction
            verified = self._verify_contradictions(raw_contradictions, claims_dict)

            result["verified_contradictions"] = len(verified)

            # Step 4: Sort by confidence and limit output
            verified.sort(key=lambda c: c.confidence_score, reverse=True)
            result["contradictions"] = verified[:self.max_contradictions]

            result["execution_successful"] = True

        except Exception as e:
            result["execution_successful"] = False
            result["error_message"] = f"Pipeline error: {str(e)}"

        return result

    def _extract_claims_safe(self, paper: Paper) -> List[Claim]:
        """Safely extract claims from a paper with error handling and limits."""

        try:
            claims = self.extractor.extract(paper)
            # Limit number of claims per paper
            return claims[:self.max_claims_per_paper]
        except Exception as e:
            # Return empty list on error rather than crashing
            return []

    def _find_raw_contradictions(
        self, claims_dict: Dict[str, List[Claim]]
    ) -> List[Contradiction]:
        """Find raw contradictions between claims from two papers.

        Args:
            claims_dict: Mapping of paper_id to list of Claim objects.

        Returns:
            A list of raw (unverified) Contradiction objects.
        """
        contradictions = []

        paper_ids = list(claims_dict.keys())
        if len(paper_ids) < 2:
            return contradictions

        claims_a = claims_dict.get(paper_ids[0], [])
        claims_b = claims_dict.get(paper_ids[1], [])

        # Limit comparison pairs for efficiency
        claims_a_limited = claims_a[: self.max_claims_per_paper]
        claims_b_limited = claims_b[: self.max_claims_per_paper]

        for claim_a in claims_a_limited:
            for claim_b in claims_b_limited:
                contradiction = self.comparator.compare_claims(claim_a, claim_b)
                if contradiction is not None:
                    contradictions.append(contradiction)

        return contradictions

    def _verify_contradictions(
        self, raw_contradictions: List[Contradiction],
        claims_dict: Dict[str, List[Claim]]
    ) -> List[Contradiction]:
        """Verify raw contradictions against source text and filter false positives.

        Args:
            raw_contradictions: List of raw Contradiction objects from the comparator.
            claims_dict: Mapping of paper_id to list of Claim objects.

        Returns:
            A list of verified Contradiction objects with updated confidence scores
            and evidence levels.
        """
        verified: List[Contradiction] = []

        for contradiction in raw_contradictions:
            # Get the source claims
            claim_a_id = contradiction.claim_a_id
            claim_b_id = contradiction.claim_b_id

            # Find the original claims
            all_claims = []
            for paper_id, claims in claims_dict.items():
                all_claims.extend(claims)

            claim_a = next((c for c in all_claims if c.id == claim_a_id), None)
            claim_b = next((c for c in all_claims if c.id == claim_b_id), None)

            if claim_a is None or claim_b is None:
                # Skip if we can't find the source claims
                continue

            # Run the verifier
            verification_result = self.verifier.verify(contradiction, claim_a, claim_b)

            if verification_result.get("is_valid", False):
                # Update the contradiction with verified confidence and evidence level
                contradiction.confidence_score = verification_result.get(
                    "final_confidence", contradiction.confidence_score
                )
                contradiction.evidence_level = verification_result.get(
                    "evidence_level", contradiction.evidence_level
                )
                # Update evidence notes if available
                if "evidence_notes" in verification_result:
                    # Store notes as explanation extension
                    if contradiction.explanation:
                        contradiction.explanation += " | " + verification_result["evidence_notes"]
                    else:
                        contradiction.explanation = verification_result["evidence_notes"]
                verified.append(contradiction)
            # If not valid, simply drop it (no need to add to results)

        return verified