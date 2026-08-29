"""Evaluation runner for Lit-Contradiction pipeline."""

import json
import time
from typing import Dict, Any, List
from lit_contradict.core.schemas import EvaluationResult


class EvaluationRunner:
    """Runs evaluation benchmarks for contradiction detection systems."""

    def __init__(self, ground_truth_path: str):
        self.ground_truth_path = ground_truth_path
        with open(ground_truth_path) as f:
            self.ground_truth = json.load(f)

    def run_baseline(self, system_results: List[Dict[str, Any]]) -> EvaluationResult:
        """Run baseline evaluation against ground-truth.

        Args:
            system_results: List of contradiction results from the system being evaluated.

        Returns:
            EvaluationResult with precision, recall, f1_score metrics.
        """
        start_time = time.time()

        # Parse ground-truth contradictions
        gt_contradictions = self.ground_truth.get("contradictions", [])
        gt_paper_pairs = self.ground_truth.get("paper_pairs", [])

        # Simple matching logic: count true positives
        # In production, this would use proper entity matching
        true_positives = 0
        false_positives = 0
        false_negatives = len(gt_contradictions)

        for system_result in system_results:
            # Check if this system result matches a ground-truth contradiction
            matched = False
            for gt_idx, gt in enumerate(gt_contradictions):
                if not gt.get("verified", False):
                    continue
                # Simple match: same paper pair and contradiction type
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
                    gt[("verified")] = True
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