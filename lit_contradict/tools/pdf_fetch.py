"""PDF Downloader module for fetching papers from arXiv or URLs."""

import os
import urllib.request
from typing import Dict, Any

class PDFDownloader:
    """Downloader for arXiv and web-hosted PDF files."""
    
    def fetch_arxiv_paper(self, arxiv_id: str, download_dir: str = "./data") -> Dict[str, Any]:
        """Fetches PDF URL and downloads PDF given an arXiv ID (e.g., '2305.18290')."""
        os.makedirs(download_dir, exist_ok=True)
        
        # Clean ID in case user passed full URL or prefix
        clean_id = arxiv_id.replace("arxiv:", "").replace("abs/", "").replace("pdf/", "")
        pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"
        output_path = os.path.join(download_dir, f"{clean_id}.pdf")

        try:
            urllib.request.urlretrieve(pdf_url, output_path)
            return {
                "arxiv_id": clean_id,
                "pdf_url": pdf_url,
                "local_path": output_path,
                "status": "success"
            }
        except Exception as e:
            return {
                "arxiv_id": clean_id,
                "pdf_url": pdf_url,
                "local_path": None,
                "status": "error",
                "error": str(e)
            }