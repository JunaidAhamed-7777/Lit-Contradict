# I will not waste your time, this project is incomplete and proved to be too ambitious for me.
## I have abandoned this idea because it's bricked my laptop almost a dozen times and I've been hitting multiple walls.
### If you are still curious, check the documentation down below.


```txt
                                                                         ,   ,
                                                                        /////|
 _     _ _          _____             _                 _ _      _     ///// |
| |   (_) |        /  __ \           | |               | (_)    | |   |~~~|  |
| |    _| |_       | /  \/ ___  _ __ | |_ _ __ __ _  __| |_  ___| |_  |===|  |
| |   | | __|      | |    / _ \| '_ \| __| '__/ _` |/ _` | |/ __| __| |   |  |
| |___| | |_       | \__/\ (_) | | | | |_| | | (_| | (_| | | (__| |_  |   |  |
\_____/_|\__|       \____/\___/|_| |_|\__|_|  \__,_|\__,_|_|\___|\__| |   | /
Developed By Junaid                                                   |===|/
                                                                      '---'
```

**Automated Academic Claim Verification & Contradiction Detection Pipeline**

---

## System Overview

### 1. The Problem

The velocity of scientific publishing creates an overwhelming volume of literature, making it difficult for researchers to evaluate conflicting evidence across publications. Manual literature review suffers from critical bottlenecks:

* **Information Overload**: Researchers cannot manually cross-reference hundreds of papers to track shifting empirical findings, methodological variances, or conflicting results.
* **Granular Discrepancies**: Subtle contradictions—such as conflicting empirical outcomes across clinical trial durations or divergent evaluation metrics—are easily missed during standard peer review.
* **Format Fragmentation**: Unstructured, multi-column PDF layouts impede fast information extraction and structured comparative analysis.

---

### 2. The Solution

**Lit-Contradict** is an end-to-end, agentic NLP framework and CLI tool designed to automatically parse, extract, and compare claims between scientific papers.

By leveraging a pipeline of specialized agents (Extraction, Comparison, and Verification) alongside PyMuPDF and graph-based structural modeling, Lit-Contradict extracts core research claims from PDFs or arXiv IDs and evaluates them for empirical, methodological, and theoretical contradictions.

---

### 3. How Lit-Contradict Fixes It

Lit-Contradict addresses literature reconciliation by automating claim alignment and contradiction analysis:

* **Automated PDF & arXiv Ingestion**: Standardizes parsing of local multi-page PDFs and remote arXiv publications via `pymupdf` and `PDFDownloader`, converting unstructured formatting into clean markdown/text schemas.
* **Agentic Tripartite Pipeline**:
1. **Extractor Agent**: Segregates full-text papers into isolated, verifiable empirical, methodological, or theoretical claims.
2. **Comparator Agent**: Pairs claims across documents and executes targeted cross-document semantic comparisons.
3. **Verifier Agent**: Computes confidence scores ($0.0 - 1.0$) and categorizes contradiction evidence levels (**High**, **Medium**, **Low**) to eliminate false positives.


* **Multiple LLM Runtime Support**: Natively supports cloud-based endpoints (OpenAI API, NVIDIA NIM Microservices) as well as fully offline open-weights local LLM runners via Ollama (`llama3.2`, `mixtral`, etc.).
* **Extensible Delivery**: Exposes functionality as a global CLI (`lit-contradict`), a RESTful API server via FastAPI, and an automated evaluation engine for benchmark tracking.

---

## Architecture & Workflow

```
[ PDF / arXiv ID ] ──> [ PDFParser / PyMuPDF ] ──> [ Schema Object (Paper) ]
                                                            │
                                                            ▼
                                                    [ Extractor Agent ]
                                                            │
                                                            ▼
                                                    [ Comparator Agent ]
                                                            │
                                                            ▼
                                                    [ Verifier Agent ]
                                                            │
                                                            ▼
                                                [ Contradiction Graph / JSON ]

```

---

## Installation

### Prerequisites

* Python 3.9+
* Recommended: Virtual environment (`venv` or `conda`)

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/YourUsername/Lit-Contradict.git
cd Lit-Contradict

```


2. Install dependencies and register the global CLI executable:
```bash
pip install -e .

```


3. Verify installation:
```bash
lit-contradict --help

```



---

## Configuration & Environment Setup

Configure your LLM provider by setting environment variables in a `.env` file or directly in your terminal session.

### Option A: NVIDIA NIM API (Recommended for Cloud)

```bash
export OPENAI_API_KEY="nvapi-YOUR_NVIDIA_NIM_KEY"
export OPENAI_API_BASE="https://integrate.api.nvidia.com/v1"
export LLM_MODEL="meta/llama-3.3-70b-instruct"

```

### Option B: Local Inference with Ollama (Offline / Free)

```bash
export OPENAI_API_KEY="ollama"
export OPENAI_API_BASE="http://localhost:11434/v1"
export LLM_MODEL="llama3.2:1b"

```

---

## Usage

### 1. Ingest a Paper

Parse local PDFs or fetch directly from arXiv:

```bash
# Ingest local PDF
lit-contradict ingest data/sample_data.pdf

# Ingest via arXiv ID
lit-contradict ingest 2305.18290

```

### 2. Run Contradiction Pipeline

Compare two papers for conflicting claims:

```bash
lit-contradict run --pdf-a data/paper1.pdf --pdf-b data/paper2.pdf

```

### 3. Run Benchmark Evaluation

Evaluate pipeline performance against ground-truth datasets:

```bash
lit-contradict eval eval/ground_truth.json --mode baseline

```

### 4. Launch REST API Server

Start the FastAPI server for web interface or programmatic access:

```bash
lit-contradict serve

```

*API docs will be available at `http://localhost:8000/docs`.*

---

## Project Structure

```
Lit-Contradict/
├── data/                  # Local PDF storage & sample data
├── eval/                  # Ground truth datasets & evaluation runners
│   ├── ground_truth.json
│   └── runner.py
├── lit_contradict/
│   ├── agents/            # Extractor, Comparator, Verifier agents
│   ├── api/               # FastAPI server endpoints
│   ├── core/              # Pipeline orchestration & Pydantic schemas
│   └── tools/             # PyMuPDF parsers, arXiv fetcher, text processors
├── cli.py                 # Typer CLI application entrypoint
├── pyproject.toml         # Build system & console script definitions
└── requirements.txt       # Project dependencies

```

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

running server
{
    uvicorn lit_contradict.api.server:app --host 127.0.0.1 --port 8000
}