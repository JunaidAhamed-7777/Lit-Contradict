"""Evaluation runner for Lit-Contradiction pipeline.

Supports both baseline (single-prompt LLM) and agent-based evaluation modes.
Wires into eval/baseline.py for the baseline comparison pipeline.
"""

import json
import time
import os
from typing import Dict, Any, List, Optional
from lit_contradict.core.schemas import EvaluationResult
from eval.baseline import BaselineEngine


class EvaluationRunner:
    """Runs evaluation benchmarks for contradiction detection systems."""

    def __init__(self, ground_truth_path: str, baseline_model: Optional[str] = None):
        self.ground_truth_path = ground_truth_path
        with open(ground_truth_path) as f:
            self.ground_truth = json.load(f)

        self.baseline_engine = BaselineEngine(api_key=None, model=baseline_model or "gpt-4o-mini")

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

        # Load paper objects from the data directory or construct identifiers
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

    def _load_paper(self, paper_id: str) -> Any:
        """Load a Paper object by ID from cached data or return placeholder.

        Args:
            paper_id: The paper identifier

        Returns:
            Paper object or string placeholder
        """
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
        # The baseline engine will handle missing text gracefully
        from lit_contradict.core.schemas import Paper
        return Paper(id=paper_id, title=paper_id, authors=[], abstract="", sections={}, full_text="")

    def run_agent(self, system_results: List[Dict[str, Any]]) -> EvaluationResult:
        """Run agent-based evaluation (placeholder for future multi-agent pipeline).

        Args:
            system_results: List of contradiction results from the agent system.

        Returns:
            EvaluationResult with precision, recall, f1_score metrics.
        """
        # This delegates to the existing evaluation logic
        # but can be extended to use actual agent outputs
        from lit_contradict.core.schemas import EvaluationResult

        start_time = time.time()

        # Parse ground-truth contradictions
        gt_contradictions = self.ground_truth.get("contradictions", [])
        gt_paper_pairs = self.ground_truth.get("paper_pairs", [])

        true_positives = 0
        false_positives = 0
        false_negatives = len(gt_contradictions)

        for system_result in system_results:
            matched = False
            for gt_idx, gt in enumerate(gt_contradictions):
                if not gt.get("verified", False):
                    continue
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
            total_pairs_evaluated=len(gt_paper_pairs),
            total_contradictions_found=true_positives,
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            execution_time_seconds=round(execution_time, 2),
        )