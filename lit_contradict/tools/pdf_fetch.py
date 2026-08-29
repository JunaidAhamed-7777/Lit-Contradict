"""PDF fetching and downloading modules."""

import httpx
from typing import Optional


ARXIV_API_BASE = "http://export.arxiv.org/api/query"


class PDFDownloader:
    """Downloads PDFs from arXiv or local paths."""

    def __init__(self, timeout: int = 30, max_size_mb: int = 50):
        self.timeout = timeout
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.client = httpx.Client(timeout=self.timeout)

    def fetch_arxiv_paper(self, arxiv_id: str) -> dict:
        """Fetch paper metadata and PDF from arXiv.

        Args:
            arxiv_id: arXiv identifier (e.g., "2101.00001").

        Returns:
            A dict with paper metadata and PDF download info.
        """
        search_url = f"{ARXIV_API_BASE}"
        params = {
            "search_query": f"id:{arxiv_id}",
            "search": "search",
            "start": "0",
            "max_results": "1",
        }
        response = self.client.get(search_url, params=params)
        response.raise_for_status()
        # Parse the arXiv XML response to extract PDF link and metadata
        # This is a simplified placeholder
        return {
            "arxiv_id": arxiv_id,
            "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            "metadata": {"status": "fetched"},
        }

    def download_pdf(self, pdf_url: str) -> bytes:
        """Download PDF content from a URL.

        Args:
            pdf_url: Direct PDF URL.

        Returns:
            PDF content as bytes.
        """
        response = self.client.get(pdf_url)
        response.raise_for_status()
        content = response.content
        if len(content) > self.max_size_bytes:
            raise ValueError(
                f"PDF exceeds maximum size of {self.max_size_mb}MB"
            )
        return content