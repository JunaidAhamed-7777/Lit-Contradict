"""Sample ground-truth dataset for contradiction detection."""

# This is a sample dataset representing known contradictions between academic papers.
# In a real project, this would be populated with carefully annotated pairs.

ground_truth_sample = {
    "dataset_name": "Sample Contradiction Benchmark",
    "total_paper_pairs": 5,
    "contradictions": [
        {
            "claim_a_id": "paper1-claim-0",
            "claim_a_quote": "The experiment showed a 95% success rate",
            "claim_b_id": "paper2-claim-0",
            "claim_b_quote": "The experiment showed a 5% success rate",
            "contradiction_type": "empirical",
            "evidence_level": "high",
        },
        {
            "claim_a_id": "paper3-claim-1",
            "claim_a_quote": "Methodology A requires temperatures above 1000°C",
            "claim_b_id": "paper4-claim-2",
            "claim_b_quote": "Methodology A is effective below 500°C",
            "contradiction_type": "methodological",
            "evidence_level": "medium",
        },
    ],
    "paper_pairs": [
        ("paper1", "paper2"),
        ("paper3", "paper4"),
    ],
}

if __name__ == "__main__":
    import json
    import sys
    output_path = sys.argv[1] if len(sys.argv) > 1 else "ground_truth_sample.json"
    with open(output_path, "w") as f:
        json.dump(ground_truth_sample, f, indent=2)
    print(f"Sample ground-truth written to {output_path}")