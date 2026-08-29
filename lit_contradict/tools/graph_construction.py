"""Graph construction modules for representing contradictions as networks."""

from typing import List, Dict, Any
from lit_contradict.core.schemas import Contradiction, ContradictionType, EvidenceLevel


def build_contradiction_graph(
    contradictions: List[Contradiction],
    papers: Dict[str, Any],
) -> Dict[str, Any]:
    """Build a JSON-compatible graph representation of contradictions.

    Args:
        contradictions: List of detected Contradiction objects.
        papers: Mapping of paper_id to Paper objects.

    Returns:
        A dict representing the contradiction graph with nodes and edges.
    """
    nodes = []
    edges = []

    # Add paper nodes
    for paper_id, paper in papers.items():
        nodes.append({
            "id": paper_id,
            "label": paper.title[:50] if paper.title else paper_id,
            "type": "paper",
        })

    # Add claim nodes (limited to first 5 claims per paper for readability)
    for paper_id, paper in papers.items():
        claims = getattr(paper, "claims", []) or []
        for i, claim in enumerate(claims[:5]):
            nodes.append({
                "id": claim.id,
                "label": claim.normalized_claim_text[:60] if claim.normalized_claim_text else claim.id,
                "type": "claim",
                "paper_id": paper_id,
            })

    # Add contradiction edges
    for contradiction in contradictions:
        edges.append({
            "id": contradiction.id,
            "source": contradiction.claim_a_id,
            "target": contradiction.claim_b_id,
            "type": contradiction.contradiction_type,
            "label": f"confidence: {contradiction.confidence_score:.2f}",
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "total_contradictions": len(contradictions),
            "total_papers": len(papers),
        },
    }