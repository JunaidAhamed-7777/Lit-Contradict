from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import Field, model_validator, BaseModel


class ContradictionType(str, Enum):
    Empirical = "empirical"
    Methodological = "methodological"
    Theoretical = "theoretical"


class EvidenceLevel(str, Enum):
    High = "high"
    Medium = "medium"
    Low = "low"


class PaperStatus(str, Enum):
    Pending = "pending"
    In_Progress = "in_progress"
    Completed = "completed"


class Paper(BaseModel):
    """Schema representing an academic paper."""

    id: str
    title: str
    authors: List[str]
    abstract: str
    sections: Dict[str, str] = Field(default_factory=dict)
    full_text: Optional[str] = None
    source: Optional[str] = None  # e.g., "arxiv", "pdf_path"
    fetched_at: Optional[datetime] = None
    status: PaperStatus = PaperStatus.Pending

    @model_validator(mode="before")
    @classmethod
    def validate_required_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure id and title are always present."""
        if not values.get("id"):
            raise ValueError("Paper 'id' is required")
        if not values.get("title"):
            raise ValueError("Paper 'title' is required")
        return values

    def get_section_text(self, section_name: str) -> str:
        """Retrieve text for a named section, falling back to full_text."""
        if section_name in self.sections:
            return self.sections[section_name]
        return self.full_text or ""


class Claim(BaseModel):
    """Schema representing a extracted claim from a paper."""

    id: str
    paper_id: str
    exact_quote: str
    section_name: str
    normalized_claim_text: str
    methodology_context: Optional[str] = None
    claim_type: Optional[str] = None  # e.g., "empirical", "theoretical"

    @model_validator(mode="before")
    @classmethod
    def validate_required_fields(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not values.get("id"):
            raise ValueError("Claim 'id' is required")
        if not values.get("exact_quote"):
            raise ValueError("Claim 'exact_quote' is required")
        if not values.get("section_name"):
            raise ValueError("Claim 'section_name' is required")
        return values


class Contradiction(BaseModel):
    """Schema representing a detected contradiction between two claims."""

    id: str
    claim_a_id: str
    claim_a_quote: str
    claim_b_id: str
    claim_b_quote: str
    contradiction_type: ContradictionType
    confidence_score: float = Field(ge=0.0, le=1.0)
    explanation: str
    evidence_level: EvidenceLevel = EvidenceLevel.Medium
    evaluated_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def validate_contradiction(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not values.get("id"):
            raise ValueError("Contradiction 'id' is required")
        if not values.get("claim_a_id"):
            raise ValueError("Contradiction 'claim_a_id' is required")
        if not values.get("claim_b_id"):
            raise ValueError("Contradiction 'claim_b_id' is required")
        if not values.get("contradiction_type"):
            raise ValueError("Contradiction 'contradiction_type' is required")
        if not values.get("explanation"):
            raise ValueError("Contradiction 'explanation' is required")
        if not (0.0 <= values.get("confidence_score", 0.0) <= 1.0):
            raise ValueError("Contradiction 'confidence_score' must be between 0.0 and 1.0")
        return values


class EvaluationResult(BaseModel):
    """Schema representing evaluation metrics for a contradiction detection run."""

    run_id: str
    total_pairs_evaluated: int
    total_contradictions_found: int
    precision: float = Field(ge=0.0, le=1.0)
    recall: float = Field(ge=0.0, le=1.0)
    f1_score: float = Field(ge=0.0, le=1.0)
    execution_time_seconds: float
    human_baseline_precision: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    human_baseline_recall: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    human_baseline_f1: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    papers_evaluated: int = 0

    @model_validator(mode="before")
    @classmethod
    def validate_metrics(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not (0.0 <= values.get("precision", 0.0) <= 1.0):
            raise ValueError("Precision must be between 0.0 and 1.0")
        if not (0.0 <= values.get("recall", 0.0) <= 1.0):
            raise ValueError("Recall must be between 0.0 and 1.0")
        if not (0.0 <= values.get("f1_score", 0.0) <= 1.0):
            raise ValueError("F1 score must be between 0.0 and 1.0")
        return values