"""Data directory for sample inputs/outputs and cached PDFs."""

from lit_contradict.core.schemas import Paper, Claim, Contradiction, EvaluationResult

# Sample paper instances (populated during pipeline execution)
sample_papers: Dict[str, Paper] = {}

# Sample claims cache
sample_claims: Dict[str, List[Claim]] = {}

# Cached PDF metadata
cached_pdfs: Dict[str, dict] = {}

# Generated contradiction graphs
generated_graphs: Dict[str, dict] = {}

# Evaluation results
evaluation_results: List[EvaluationResult] = []