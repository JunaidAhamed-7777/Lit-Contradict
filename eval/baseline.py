"""Single-prompt baseline runner for contradiction detection.

This baseline takes two parsed papers and sends them to an LLM with a simple
prompt: "Read these two academic papers and list any direct claim contradictions
or conflicting results between them."

The output is parsed into the Contradiction Pydantic model format for direct
evaluation against ground-truth data.

Features:
- Handles API error states and rate limiting
- Supports raw text input or parsed Paper objects
- Truncates context if token bounds are reached
- Returns Contradiction objects compatible with eval/runner.py
"""

import time
import json
import os
from typing import Optional, Union, List, Dict, Any

from lit_contradict.core.schemas import Paper, Claim, Contradiction


# Prompt template for the single-prompt baseline
BASELINE_PROMPT = """Read the following two academic papers and list any direct claim contradictions 
or conflicting results between them. For each contradiction found, provide:
1. The exact quote from paper A that makes claim A
2. The exact quote from paper B that makes claim B  
3. The contradiction type (empirical, methodological, or theoretical)
4. A brief explanation of the contradiction

Paper A:
{paper_a_text}

Paper B:
{paper_b_text}

Output format - JSON list of contradictions:
[
  {{
    "claim_a_quote": "...",
    "claim_b_quote": "...",
    "contradiction_type": "empirical|methodological|theoretical",
    "explanation": "..."
  }}
]
"""


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call_time: float = 0.0

    def wait(self):
        """Wait if needed to respect rate limit."""
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            import time as time_mod
            time_mod.sleep(self.min_interval - elapsed)
        self.last_call_time = time.time()


class BaselineEngine:
    """Baseline contradiction detection using a single LLM prompt."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.rate_limiter = RateLimiter()
        self.use_mock = api_key is None

    def _format_paper_text(self, paper: Union[Paper, str], section: str = "full") -> str:
        """Format paper text for the baseline prompt.

        Args:
            paper: A Paper object or raw text string
            section: Which section to use ("full", "abstract", "methods", etc.)

        Returns:
            Formatted text string for the prompt
        """
        if isinstance(paper, str):
            return paper[:5000]  # Truncate for safety

        paper_obj = paper
        if section == "full":
            text = paper_obj.full_text or ""
        elif section in paper_obj.sections:
            text = paper_obj.sections.get(section, "")
        else:
            text = paper_obj.abstract or ""

        # Truncate if too long
        if len(text) > 5000:
            text = text[:5000] + "...[truncated]"

        return text

    def _parse_llm_output(self, raw_output: str) -> List[Dict[str, Any]]:
        """Parse the LLM's JSON output from raw text.

        Args:
            raw_output: Raw text from the LLM response

        Returns:
            List of dicts with contradiction data
        """
        # Try to extract JSON from the response
        # Look for JSON array starting with [ and ending with ]
        start_idx = raw_output.find("[")
        end_idx = raw_output.rfind("]")

        if start_idx >= 0 and end_idx > start_idx:
            json_str = raw_output[start_idx:end_idx + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Fallback: try to find any JSON object
        # This is a best-effort parsing
        results = []
        # Simple heuristic - look for key-value pairs
        return results

    def _build_contradiction_from_dict(self, data: Dict[str, Any], paper_a_id: str, paper_b_id: str) -> Contradiction:
        """Build a Contradiction model from parsed LLM output.

        Args:
            data: Dict with contradiction data from LLM
            paper_a_id: ID of the first paper
            paper_b_id: ID of the second paper

        Returns:
            Contradiction model instance
        """
        claim_a_quote = data.get("claim_a_quote", "")
        claim_b_quote = data.get("claim_b_quote", "")
        contradiction_type_str = data.get("contradiction_type", "empirical")
        explanation = data.get("explanation", "")

        # Map string to enum
        try:
            from lit_contradict.core.schemas import ContradictionType
            contradiction_type = ContradictionType(contradiction_type_str.lower())
        except (ValueError, ImportError):
            contradiction_type = ContradictionType.Empirical

        # Generate IDs if not provided
        claim_a_id = f"{paper_a_id}-claim-a"
        claim_b_id = f"{paper_b_id}-claim-b"

        contradiction = Contradiction(
            id=f"baseline-{paper_a_id}-{paper_b_id}",
            claim_a_id=claim_a_id,
            claim_a_quote=claim_a_quote,
            claim_b_id=claim_b_id,
            claim_b_quote=claim_b_quote,
            contradiction_type=contradiction_type,
            confidence_score=0.5,  # Baseline default
            explanation=explanation,
        )

        return contradiction

    def run(
        self,
        paper_a: Union[Paper, str],
        paper_b: Union[Paper, str],
        section: str = "full",
        mock: bool = True,
    ) -> Optional[Contradiction]:
        """Run the baseline contradiction detection on two papers.

        Args:
            paper_a: First Paper object or raw text
            paper_b: Second Paper object or raw text
            section: Which paper section to analyze ("full", "abstract", etc.)
            mock: If True, simulate LLM output (for testing without API key)

        Returns:
            Contradiction object if found, None otherwise
        """
        # Rate limiting
        self.rate_limiter.wait()

        # Format paper text
        text_a = self._format_paper_text(paper_a, section)
        text_b = self._format_paper_text(paper_b, section)

        if not text_a.strip() or not text_b.strip():
            print("Warning: One or both papers have no text content")
            return None

        # Build the prompt
        prompt = BASELINE_PROMPT.format(paper_a_text=text_a, paper_b_text=text_b)

        # In mock mode or without API key, simulate LLM response
        if self.use_mock or mock:
            contradiction = self._mock_llm_response(prompt, paper_a, paper_b)
        else:
            contradiction = self._real_llm_response(prompt, paper_a, paper_b)

        return contradiction

    def _mock_llm_response(
        self, prompt: str, paper_a: Union[Paper, str], paper_b: Union[Paper, str]
    ) -> Optional[Contradiction]:
        """Simulate LLM response for testing purposes.

        Args:
            prompt: The full prompt sent to the LLM
            paper_a: First paper
            paper_b: Second paper

        Returns:
            Contradiction object or None
        """
        # Simulate API latency
        import time as time_mod
        time_mod.sleep(0.5)

        # Generate a simple mock contradiction based on keywords
        text_a_lower = str(paper_a).lower() if not isinstance(paper_a, Paper) else (paper_a.abstract or "").lower()
        text_b_lower = str(paper_b).lower() if not isinstance(paper_b, Paper) else (paper_b.abstract or "").lower()

        # Check for simple contradictory keywords
        mock_contradictions = []

        # If paper A mentions "high temperature" and paper B mentions "low temperature"
        if "temperature" in text_a_lower and "temperature" in text_b_lower:
            # Check if values contradict
            a_temp_units = ["celsius", "°c", "centigrade"]
            b_temp_units = ["celsius", "°c", "centigrade"]

            # Simple mock: always generate a contradiction if both mention temperature
            mock_data = {
                "claim_a_quote": text_a_lower.split("temperature")[0][:100] + "...temperature mentioned",
                "claim_b_quote": text_b_lower.split("temperature")[0][:100] + "...temperature mentioned",
                "contradiction_type": "empirical",
                "explanation": "Papers report different temperature conditions for their experiments.",
            }
            mock_contradictions.append(mock_data)

        # If no specific contradictions found, return a generic one
        if not mock_contradictions:
            mock_data = {
                "claim_a_quote": "Key finding from paper A",
                "claim_b_quote": "Key finding from paper B",
                "contradiction_type": "theoretical",
                "explanation": "The papers appear to take different theoretical approaches to the same problem.",
            }
            mock_contradictions.append(mock_data)

        # Parse the first mock contradiction
        if mock_contradictions:
            data = mock_contradictions[0]
            return self._build_contradiction_from_dict(data, 
                getattr(paper_a, 'id', 'paper_a') if isinstance(paper_a, Paper) else "paper_a",
                getattr(paper_b, 'id', 'paper_b') if isinstance(paper_b, Paper) else "paper_b"
            )

        return None

    def _real_llm_response(
        self, prompt: str, paper_a: Union[Paper, str], paper_b: Union[Paper, str]
    ) -> Optional[Contradiction]:
        """Send prompt to real LLM API (OpenAI compatible).

        Args:
            prompt: The full prompt sent to the LLM
            paper_a: First paper
            paper_b: Second paper

        Returns:
            Contradiction object or None if API fails
        """
        import httpx

        self.rate_limiter.wait()

        # Build API request
        api_url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = [
            {"role": "system", "content": "You are an academic researcher analyzing contradictions between papers."},
            {"role": "user", "content": prompt},
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1000,
        }

        try:
            client = httpx.Client(timeout=30)
            self.rate_limiter.wait()

            response = client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Parse the output
            parsed = self._parse_llm_output(content)

            if parsed and len(parsed) > 0:
                first_result = parsed[0]
                # Build contradiction from first result
                a_id = getattr(paper_a, 'id', 'paper_a') if isinstance(paper_a, Paper) else "paper_a"
                b_id = getattr(paper_b, 'id', 'paper_b') if isinstance(paper_b, Paper) else "paper_b"

                return self._build_contradiction_from_dict(first_result, a_id, b_id)

            print("Warning: LLM response did not contain parseable contradiction data")
            return None

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                print(f"Rate limit hit: {e}")
            else:
                print(f"API error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error calling LLM API: {e}")
            return None