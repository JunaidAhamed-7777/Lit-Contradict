# Architecture Breakdown

- Core Engine (Python CLI): Houses your multi-agent system, paper parsers, claim extraction pipeline, contradiction comparator, and ground-truth evaluation benchmark.
- Frontend Dashboard (Web UI): Displays interactive conflict graphs, side-by-side citation quotes, and precision/recall metrics for the demo.

---

# System Architecture & Agent Flow
┌─────────────────┐     ┌──────────────────────┐     ┌───────────────────────┐
│ PDF Ingestion   │ ──> │ Claim Extractor      │ ──> │ Contradiction Agent   │
│ (ArXiv / OA)    │     │ (Claims + Quotes)    │     │ (Pairwise Matrix)     │
└─────────────────┘     └──────────────────────┘     └───────────────────────┘
                                                                 │
                                                                 ▼
┌─────────────────┐     ┌──────────────────────┐     ┌───────────────────────┐
│ Ground-Truth    │ <── │ Knowledge Graph      │ <── │ Verification Agent    │
│ Benchmark Eval  │     │ Generator (JSON)     │     │ (Quote-Level Audit)   │
└─────────────────┘     └──────────────────────┘     └───────────────────────┘
---

# Phased Execution Plan
- Phase 1: CLI Core Engine & Baseline Setup
    - Set up lit-contradict structure with Python (FastAPI/Typer).
    - Build arXiv/PDF full-text extraction tool.
    - Build a simple single-prompt baseline (e.g., asking LLM directly: "Find contradictions in these 2 papers").
    - Build the 10-paper ground-truth benchmark dataset and evaluation script.
- Phase 2: Multi-Agent Orchestration Pipeline
    - Extractor Agent: Extracts specific claims, methodology parameters, and direct quote mappings.
    - Comparator Agent: Runs pairwise cross-paper claim checks to flag direct logical/empirical contradictions.
    - Verifier Agent: Audits flagged contradictions against raw text quotes to prevent hallucinations.
    - Graph Builder: Exports structured JSON with claims, nodes, edges (agrees/disagrees), and confidence scores.
- Phase 3: Web UI Dashboard
    - Build an single-page UI (via Stitch.ai or light frontend) rendering paper nodes, red conflict links, and side-by-side claim/quote panels.
- Phase 4: Hackathon Deliverables & Benchmarking
    - Run evaluation suite to generate precision/recall metrics (Baseline vs. Agent System).  
    - Generate changelog.md, reproducibility.md, and record the 5-minute video.  