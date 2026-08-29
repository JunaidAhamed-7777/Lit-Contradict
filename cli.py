"""CLI entry point for Lit-Contradiction."""

import json
from typing import List, Optional
import typer
from lit_contradict.core.schemas import Paper, Claim, Contradiction, EvaluationResult
from eval.runner import EvaluationRunner

app = typer.Typer()


@app.command()
def ingest(
    arxiv_id: Optional[str] = typer.Argument(None, help="arXiv paper ID to fetch"),
    pdf_path: Optional[str] = typer.Argument(None, help="Local PDF path to parse"),
):
    """Fetch or parse PDFs for paper ingestion."""
    from lit_contradict.tools.pdf_fetch import PDFDownloader
    from lit_contradict.tools.pdf_parse import PDFParser

    downloader = PDFDownloader()
    parser = PDFParser()

    if arxiv_id:
        typer.echo(f"Fetching arXiv paper: {arxiv_id}")
        result = downloader.fetch_arxiv_paper(arxiv_id)
        typer.echo(f"PDF URL: {result.get('pdf_url', 'N/A')}")
    elif pdf_path:
        typer.echo(f"Parsing local PDF: {pdf_path}")
        paper = parser.parse(pdf_path)
        typer.echo(f"Extracted text length: {len(paper.full_text or '')} chars")
    else:
        typer.echo("Usage: lit-contradict ingest <arxiv_id|pdf_path>")


@app.command()
def run(
    paper_ids: Optional[List[str]] = typer.Argument(
        None, help="List of paper IDs to run pipeline on"
    ),
):
    """Execute the contradiction detection pipeline."""
    typer.echo("Running contradiction detection pipeline...")
    # Placeholder: In production, this would orchestrate the extractor,
    # comparator, and verifier agents.
    typer.echo("Pipeline execution complete (placeholder mode).")


@app.command()
def eval(
    ground_truth_path: str = typer.Argument(..., help="Path to ground-truth dataset"),
    mode: str = typer.Option("baseline", help="Evaluation mode: 'baseline' or 'agent'"),
):
    """Run evaluation suite against ground-truth data."""
    typer.echo(f"Loading ground-truth from: {ground_truth_path}")
    try:
        with open(ground_truth_path) as f:
            data = json.load(f)
        typer.echo(f"Loaded {data.get('total_paper_pairs', 0)} evaluation pairs")
    except Exception as e:
        typer.echo(f"Error loading ground-truth: {e}")
        raise typer.Exit(code=1)

    runner = EvaluationRunner(ground_truth_path)

    if mode == "baseline":
        typer.echo("Running baseline evaluation (single-prompt LLM)...")
        result = runner.run_baseline()
    elif mode == "agent":
        typer.echo("Running agent-based evaluation...")
        # Placeholder: In production, this would use actual agent outputs
        result = runner.run_agent([])
    else:
        typer.echo(f"Unknown mode: {mode}. Use 'baseline' or 'agent'.")
        raise typer.Exit(code=1)

    typer.echo(f"Evaluation result: P={result.precision:.2f} R={result.recall:.2f} F1={result.f1_score:.2f} "
               f"({result.execution_time_seconds}s)")


if __name__ == "__main__":
    app()