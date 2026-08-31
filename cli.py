"""CLI entry point for Lit-Contradiction."""

import json
import os
from typing import List, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

from lit_contradict.core.schemas import Paper, Claim, Contradiction, EvaluationResult
from eval.runner import EvaluationRunner

import sys
from pathlib import Path

# Ensure root directory is added to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Setup Rich console styling
console = Console(theme=Theme({
    "primary": "#34d399",
    "secondary": "#5af0b3",
    "alert": "#ffb4ab",
    "dim_text": "#bbcac0"
}))

app = typer.Typer(help="Lit-Contradict: Academic Research Contradiction Detection CLI")


def display_ascii_art():
    """Reads and displays ascii-art.txt before command execution."""
    art_path = "ascii-art.txt"
    if os.path.exists(art_path):
        try:
            with open(art_path, "r", encoding="utf-8") as f:
                art_content = f.read()
            console.print(f"[primary]{art_content}[/primary]")
        except Exception:
            console.print("[primary]=== Lit-Contradict CLI ===[/primary]\n")
    else:
        console.print("[primary]=== Lit-Contradict CLI ===[/primary]\n")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Callback to display ASCII art on CLI launch."""
    display_ascii_art()


@app.command()
def ingest(
    target: Optional[str] = typer.Argument(None, help="arXiv paper ID or local PDF file path to parse"),
):
    """Fetch or parse PDFs for paper ingestion."""
    from lit_contradict.tools.pdf_fetch import PDFDownloader
    from lit_contradict.tools.pdf_parse import PDFParser

    downloader = PDFDownloader()
    parser = PDFParser()

    if not target:
        console.print("[alert]Error:[/alert] Please provide an arXiv ID or PDF file path.")
        console.print("Usage: python cli.py ingest <arxiv_id_or_pdf_path>")
        raise typer.Exit(code=1)

    # Check if target is a local PDF file
    if target.endswith(".pdf") or os.path.exists(target):
        console.print(f"[secondary]Parsing local PDF with PyMuPDF:[/secondary] {target}")
        try:
            paper = parser.parse(target)
            console.print(f"[primary]✓[/primary] Extracted text length: {len(paper.full_text or '')} chars")
        except Exception as e:
            console.print(f"[alert]Error parsing PDF:[/alert] {e}")
            raise typer.Exit(code=1)
    else:
        # Treat as arXiv ID
        console.print(f"[secondary]Fetching arXiv paper:[/secondary] {target}")
        result = downloader.fetch_arxiv_paper(target)
        if result["status"] == "success":
            console.print(f"[primary]✓[/primary] PDF downloaded to: {result['local_path']}")
        else:
            console.print(f"[alert]Error downloading arXiv paper:[/alert] {result.get('error')}")


@app.command()
def run(
    paper_ids: Optional[List[str]] = typer.Argument(
        None, help="List of paper IDs to run pipeline on"
    ),
    pdf_a: Optional[str] = typer.Option(None, "--pdf-a", "-a", help="Path to first local PDF"),
    pdf_b: Optional[str] = typer.Option(None, "--pdf-b", "-b", help="Path to second local PDF"),
):
    """Execute the contradiction detection pipeline on specified papers or PDF files."""
    if pdf_a and pdf_b:
        from lit_contradict.tools.pdf_parse import PDFParser
        parser = PDFParser()
        
        console.print(f"[secondary]Parsing PDF A:[/secondary] {pdf_a}")
        paper_a = parser.parse(pdf_a)
        console.print(f"[secondary]Parsing PDF B:[/secondary] {pdf_b}")
        paper_b = parser.parse(pdf_b)
        
        console.print(f"[primary]✓[/primary] Loaded Paper A ({len(paper_a.full_text)} chars) and Paper B ({len(paper_b.full_text)} chars)")
        console.print("Running contradiction detection pipeline...")
        # Pipeline execution goes here
        return

    # Fallback to ground-truth pipeline evaluation
    ground_truth_path = "eval/ground_truth.json"
    try:
        with open(ground_truth_path) as f:
            data = json.load(f)
        console.print(f"Loaded ground-truth from: [dim_text]{ground_truth_path}[/dim_text]")
    except Exception as e:
        console.print(f"[alert]Error loading ground-truth:[/alert] {e}")
        raise typer.Exit(code=1)

    runner = EvaluationRunner(ground_truth_path)
    result = runner.run_agent()
    console.print(f"[primary]Evaluation result:[/primary] P={result.precision:.2f} R={result.recall:.2f} F1={result.f1_score:.2f}")

@app.command()
def eval(
    ground_truth_path: str = typer.Argument(..., help="Path to ground-truth dataset"),
    mode: str = typer.Option("baseline", help="Evaluation mode: 'baseline' or 'agent'"),
):
    """Run evaluation suite against ground-truth data."""
    console.print(f"Loading ground-truth from: {ground_truth_path}")
    try:
        with open(ground_truth_path) as f:
            data = json.load(f)
        console.print(f"Loaded {data.get('total_paper_pairs', 0)} evaluation pairs")
    except Exception as e:
        console.print(f"[alert]Error loading ground-truth:[/alert] {e}")
        raise typer.Exit(code=1)

    runner = EvaluationRunner(ground_truth_path)

    if mode == "baseline":
        console.print("Running baseline evaluation (single-prompt LLM)...")
        result = runner.run_baseline()
    elif mode == "agent":
        console.print("Running agent-based evaluation (multi-agent pipeline)...")
        result = runner.run_agent()
    else:
        console.print(f"[alert]Unknown mode: {mode}. Use 'baseline' or 'agent'.[/alert]")
        raise typer.Exit(code=1)

    console.print(
        f"[primary]Evaluation result:[/primary] P={result.precision:.2f} R={result.recall:.2f} F1={result.f1_score:.2f} "
        f"({result.execution_time_seconds}s)"
    )


@app.command()
def serve():
    """Start the FastAPI server for the Lit-Contradiction API."""
    import subprocess
    import sys

    console.print("[primary]Starting Lit-Contradiction API server...[/primary]")
    console.print("Visit [secondary]http://127.0.0.1:8000/docs[/secondary] for the interactive API docs")
    subprocess.run(
        [sys.executable, "-m", "lit_contradict.api.server"],
        check=True,
    )


if __name__ == "__main__":
    app()