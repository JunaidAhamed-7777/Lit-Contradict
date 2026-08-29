"""FastAPI server for Lit-Contradiction Web UI integration."""

from fastapi import FastAPI
from lit_contradict.core.schemas import Paper, Claim, Contradiction, EvaluationResult

app = FastAPI(
    title="Lit-Contradiction API",
    description="Academic Paper Contradiction Detector",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "Lit-Contradiction API is running"}


@app.post("/papers/")
async def create_paper(paper: Paper):
    """Endpoint to submit a paper for contradiction analysis."""
    return {"status": "paper_received", "paper_id": paper.id}


@app.get("/papers/{paper_id}")
async def get_paper(paper_id: str):
    """Endpoint to retrieve a paper by ID."""
    return {"paper_id": paper_id, "status": "placeholder"}


@app.post("/evaluate/")
async def evaluate_results(result: EvaluationResult):
    """Endpoint to submit evaluation results."""
    return {"status": "evaluation_received", "metrics": {
        "precision": result.precision,
        "recall": result.recall,
        "f1_score": result.f1_score,
    }}