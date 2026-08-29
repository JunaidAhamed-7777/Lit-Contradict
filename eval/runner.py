"""Evaluation runner for Lit-Contradiction pipeline.

Supports both baseline (single-prompt LLM) and agent-based evaluation modes.
Wires into eval/baseline.py for the baseline comparison pipeline,
and into lit_contradict.core.pipeline.ContradictionPipeline for the agent mode.
"""

import json
import time
import os
from typing import Dict, Any, List, Optional
from lit_contradict.core.schemas import EvaluationResult
from eval.baseline import BaselineEngine
from lit_contradict.core.pipeline import ContradictionPipeline


class EvaluationRunner:
    """Runs evaluation benchmarks for contradiction detection systems."""

    def __init__(self, ground_truth_path: str, baseline_model: Optional[str] = None):
        self.ground_truth_path = ground_truth_path
        with open(ground_truth_path) as f:
            self.ground_truth = json.load(f)

        self.baseline_engine = BaselineEngine(api_key=None, model=baseline_model or "gpt-4o-mini")
        self.pipeline = ContradictionPipeline(max_claims_per_paper=15, max_contradictions=10)

    def _load_paper(self, paper_id: str) -> Any:
        """Load a Paper object by ID from cached data or return placeholder.

        Args:
            paper_id: The paper identifier

        Returns:
            Paper object or string placeholder
        """
        # First, try to load from sample_data module papers
        try:
            import eval.sample_data as sd
            paper_map = {
                "paper1": sd.paper1,
                "paper2": sd.paper2,
                "paper3": sd.paper3,
                "paper4": sd.paper4,
                "paper5": sd.paper5,
            }
            if paper_id in paper_map:
                return paper_map[paper_id]
        except Exception:
            pass

        # Try to load from data directory cache
        data_path = os.path.join("data", f"{paper_id}.json")
        if os.path.exists(data_path):
            try:
                with open(data_path) as f:
                    data = json.load(f)
                # Reconstruct Paper object (simplified)
                from lit_contradict.core.schemas import Paper
                paper = Paper(
                    id=data.get("id", paper_id),
                    title=data.get("title", paper_id),
                    authors=data.get("authors", []),
                    abstract=data.get("abstract", ""),
                    sections=data.get("sections", {}),
                    full_text=data.get("full_text", ""),
                )
                return paper
            except Exception:
                pass

        # Return a minimal paper object with just the ID
        # The pipeline will handle missing text gracefully
        from lit_contradict.core.schemas import Paper
        return Paper(id=paper_id, title=paper_id, authors=[], abstract="", sections={}, full_text="")

    def run_baseline(self, paper_pairs: Optional[List[Dict[str, Any]]] = None) -> EvaluationResult:
        """Run baseline evaluation against ground-truth data.

        Uses the single-prompt LLM baseline from eval/baseline.py to detect
        contradictions between paper pairs from the ground-truth dataset.

        Args:
            paper_pairs: Optional list of paper pair dicts with 'paper_a_id' and 'paper_b_id'.
                        If None, uses pairs from ground-truth data.

        Returns:
            EvaluationResult with precision, recall, f1_score, and execution time.
        """
        start_time = time.time()

        # Parse ground-truth contradictions
        gt_contradictions = self.ground_truth.get("contradictions", [])
        gt_paper_pairs = self.ground_truth.get("paper_pairs", [])

        # Use provided pairs or fall back to ground-truth pairs
        if paper_pairs is None:
            paper_pairs = gt_paper_pairs

        # Normalize pairs: ground-truth format is List[List[str]], convert to dicts
        normalized_pairs = []
        for pair_info in paper_pairs:
            if isinstance(pair_info, list) and len(pair_info) >= 2:
                normalized_pairs.append({
                    "paper_a_id": pair_info[0],
                    "paper_b_id": pair_info[1],
                })
            elif isinstance(pair_info, dict):
                normalized_pairs.append({
                    "paper_a_id": pair_info.get("paper_a_id", ""),
                    "paper_b_id": pair_info.get("paper_b_id", ""),
                })

        # Load paper objects and run baseline contradiction detection
        system_results: List[Dict[str, Any]] = []

        for pair_info in normalized_pairs:
            paper_a_id = pair_info.get("paper_a_id", "")
            paper_b_id = pair_info.get("paper_b_id", "")

            # Try to load actual Paper objects
            paper_a = self._load_paper(paper_a_id)
            paper_b = self._load_paper(paper_b_id)

            # Run baseline contradiction detection
            contradiction = self.baseline_engine.run(
                paper_a, paper_b, section="full", mock=True
            )

            if contradiction:
                result_dict = {
                    "claim_a_id": contradiction.claim_a_id,
                    "claim_b_id": contradiction.claim_b_id,
                    "contradiction_type": contradiction.contradiction_type,
                    "confidence_score": contradiction.confidence_score,
                }
                system_results.append(result_dict)

        execution_time = time.time() - start_time

        # Evaluate against ground-truth
        true_positives = 0
        false_positives = 0
        false_negatives = len(gt_contradictions)

        for system_result in system_results:
            matched = False
            for gt_idx, gt in enumerate(gt_contradictions):
                # Simple match: same paper pair IDs and contradiction type
                system_pair = (
                    system_result.get("claim_a_id", ""),
                    system_result.get("claim_b_id", ""),
                )
                gt_pair = (
                    gt.get("claim_a_id", ""),
                    gt.get("claim_b_id", ""),
                )
                if system_pair == gt_pair:
                    true_positives += 1
                    false_negatives -= 1
                    # Mark as verified so we don't count it again
                    gt["verified"] = True
                    matched = True
                    break
            if not matched:
                false_positives += 1

        execution_time = time.time() - start_time

        total = len(gt_contradictions) + false_positives
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return EvaluationResult(
            run_id=f"eval-{int(time.time())}",
            total_pairs_evaluated=len(paper_pairs),
            total_contradictions_found=true_positives,
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            execution_time_seconds=round(execution_time, 2),
        )

    def run_agent(self, paper_pairs: Optional[List[Dict[str, Any]]] = None) -> EvaluationResult:
        """Run agent-based evaluation using the multi-agent ContradictionPipeline.

        Executes the full 3-agent system (Extractor → Comparator → Verifier)
        against the ground-truth dataset and computes Precision, Recall, F1 scores.

        The evaluation matches detected contradictions against ground-truth by
        paper pair (extracted from claim IDs) and contradiction type, rather than
        exact claim ID matching, to account for pipeline-generated claim ID differences.

        Args:
            paper_pairs: Optional list of paper pair dicts with 'paper_a_id' and 'paper_b_id'.
                        If None, uses pairs from ground-truth data.

        Returns:
            EvaluationResult with precision, recall, f1_score, and execution time.
        """
        start_time = time.time()

        # Parse ground-truth contradictions
        gt_contradictions = self.ground_truth.get("contradictions", [])
        gt_paper_pairs = self.ground_truth.get("paper_pairs", [])

        # Use provided pairs or fall back to ground-truth pairs
        if paper_pairs is None:
            paper_pairs = gt_paper_pairs

        # Normalize pairs
        normalized_pairs = []
        for pair_info in paper_pairs:
            if isinstance(pair_info, list) and len(pair_info) >= 2:
                normalized_pairs.append({
                    "paper_a_id": pair_info[0],
                    "paper_b_id": pair_info[1],
                })
            elif isinstance(pair_info, dict):
                normalized_pairs.append({
                    "paper_a_id": pair_info.get("paper_a_id", ""),
                    "paper_b_id": pair_info.get("paper_b_id", ""),
                })

        # Track results across all paper pairs
        all_system_contradictions: List = []
        total_claims_extracted = 0

        for pair_info in normalized_pairs:
            paper_a_id = pair_info.get("paper_a_id", "")
            paper_b_id = pair_info.get("paper_b_id", "")

            # Load paper objects
            paper_a = self._load_paper(paper_a_id)
            paper_b = self._load_paper(paper_b_id)

            if not paper_a or not paper_b:
                continue

            # Run the full multi-agent pipeline
            pipeline_result = self.pipeline.run(paper_a, paper_b)

            total_claims_extracted += pipeline_result["total_claims_extracted"]

            # Collect verified contradictions
            all_system_contradictions.extend(pipeline_result["contradictions"])

        # Build lookup for ground-truth contradictions by (paper_a_id, paper_b_id, type)
        gt_lookup = {}
        for gt in gt_contradictions:
            gt_key = (gt.get("claim_a_id", "")[:7], gt.get("claim_b_id", "")[:7], gt.get("contradiction_type", ""))
            if gt_key not in gt_lookup:
                gt_lookup[gt_key] = gt

        # Build lookup for detected contradictions by (paper_a_id, paper_b_id, type)
        # Extract paper IDs from the pipeline's claim IDs
        detected_lookup = {}
        for con in all_system_contradictions:
            # Extract paper IDs from claim IDs format: "contradiction-claim-paper1-Abstract-1-claim-paper2-Results-0"
            a_id = con.claim_a_id
            b_id = con.claim_b_id
            
            # Extract paper names from the IDs
            a_paper = self._extract_paper_id(a_id)
            b_paper = self._extract_paper_id(b_id)
            
            det_key = (a_paper, b_paper, con.contradiction_type)
            if det_key not in detected_lookup:
                detected_lookup[det_key] = con

        # Match detected contradictions against ground-truth
        true_positives = 0
        false_positives = 0
        false_negatives = len(gt_contradictions)

        # For each ground-truth contradiction, check if a matching detection exists
        for gt in gt_contradictions:
            gt_a_paper = self._extract_paper_id(gt.get("claim_a_id", "")[:20])
            gt_b_paper = self._extract_paper_id(gt.get("claim_b_id", "")[:20])
            gt_type = gt.get("contradiction_type", "")

            det_key = (gt_a_paper, gt_b_paper, gt_type)
            if det_key in detected_lookup:
                true_positives += 1
                gt["verified"] = True
            else:
                false_negatives -= 1

        # Count false positives: detected contradictions not matching any GT entry
        for det_key, det_con in detected_lookup.items():
            # Check if this detection matches any unverified GT entry
            matched = False
            for gt in gt_contradictions:
                if not gt.get("verified", False):
                    gt_a_paper = self._extract_paper_id(gt.get("claim_a_id", "")[:20])
                    gt_b_paper = self._extract_paper_id(gt.get("claim_b_id", "")[:20])
                    gt_type = gt.get("contradiction_type", "")
                    if (det_key[0] == gt_a_paper and 
                        det_key[1] == gt_b_paper and
                        det_key[2] == gt_type):
                        matched = True
                        break
            if not matched:
                false_positives += 1

        execution_time = time.time() - start_time

        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return EvaluationResult(
            run_id=f"eval-{int(time.time())}",
            total_pairs_evaluated=len(paper_pairs),
            total_contradictions_found=true_positives,
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            execution_time_seconds=round(execution_time, 2),
        )

    @staticmethod
    def _extract_paper_id(claim_id: str) -> str:
        """Extract the paper ID from a pipeline-generated claim ID.

        Pipeline claim IDs format: 'contradiction-claim-paper1-Abstract-1-claim-paper2-Results-0'
        We extract the paper names between 'contradiction-claim-' and '-Abstract' / '-Results' etc.
        """
        # Try to extract paper name from the claim ID
        known_papers = ["paper1", "paper2", "paper3", "paper4", "paper5"]
        for p in known_papers:
            if p in claim_id:
                return p
        # Fallback: try to find any capitalized word that looks like a paper ID
        import re
        match = re.search(r'paper\d+', claim_id)
        if match:
            return match.group()
        return "unknown"