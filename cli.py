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
    """Execute the contradiction detection pipeline on specified papers.

    Runs the full multi-agent pipeline (Extractor → Comparator → Verifier)
    on the specified paper IDs from the ground-truth dataset.

    If no paper IDs are specified, runs on all papers in the ground-truth dataset.
    """
    import sys

    ground_truth_path = "eval/ground_truth.json"

    try:
        with open(ground_truth_path) as f:
            data = json.load(f)
        typer.echo(f"Loaded ground-truth from: {ground_truth_path}")
    except Exception as e:
        typer.echo(f"Error loading ground-truth: {e}")
        raise typer.Exit(code=1)

    runner = EvaluationRunner(ground_truth_path)

    # Determine which papers to run on
    if paper_ids:
        # Run on specified paper IDs
        paper_pair_ids = []
        for pid in paper_ids:
            # Parse paper ID to find pair
            # Paper IDs in ground truth are like "paper1", "paper2", etc.
            # We need to form pairs from them
            if pid in ["paper1", "paper2", "paper3", "paper4", "paper5"]:
                # Form pairs based on ground-truth paper_pairs
                pass
        # For now, just run on first available pair
        if len(paper_ids) >= 2:
            pair_info = {"paper_a_id": paper_ids[0], "paper_b_id": paper_ids[1]}
        elif len(paper_ids) == 1:
            # Find a pair involving this paper
            pair_info = None
            for pair in [["paper1", "paper2"], ["paper3", "paper4"], ["paper3", "paper5"], ["paper5", "paper1"], ["paper3", "paper4"]]:
                if pair[0] == paper_ids[0] or pair[1] == paper_ids[0]:
                    pair_info = {"paper_a_id": pair[0], "paper_b_id": pair[1]}
                    break
            else:
                typer.echo(f"Paper ID '{paper_ids[0]}' not found in ground-truth pairs.")
                raise typer.Exit(code=1)
        else:
            typer.echo("No paper IDs specified.")
            raise typer.Exit(code=1)
    else:
        # Run on all paper pairs from ground-truth
        pair_info = None

    # Run the agent pipeline
    if pair_info:
        typer.echo(f"Running agent pipeline on {pair_info['paper_a_id']} vs {pair_info['paper_b_id']}...")
        result = runner.run_agent([pair_info])
    else:
        typer.echo("Running agent pipeline on all ground-truth paper pairs...")
        result = runner.run_agent()

    typer.echo(f"Evaluation result: P={result.precision:.2f} R={result.recall:.2f} F1={result.f1_score:.2f} "
               f"({result.execution_time_seconds}s)")


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
        typer.echo("Running agent-based evaluation (multi-agent pipeline)...")
        result = runner.run_agent()
    else:
        typer.echo(f"Unknown mode: {mode}. Use 'baseline' or 'agent'.")
        raise typer.Exit(code=1)

    typer.echo(f"Evaluation result: P={result.precision:.2f} R={result.recall:.2f} F1={result.f1_score:.2f} "
               f"({result.execution_time_seconds}s)")


if __name__ == "__main__":
    app()