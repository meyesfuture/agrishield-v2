"""
Domain schema for methodology, guardrails, and analytical rules.
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class MethodologicalPrinciple(BaseModel):
    title: str = Field(..., description="Principle name")
    rule: str = Field(..., description="Operational policy / rule definition")
    rationale: str = Field(..., description="Technical and ethical rationale")


class MethodologyResponse(BaseModel):
    """Methodological framework, evidence boundaries, and anti-hoarding policies."""
    title: str = Field(default="Punjab GrainWatch Analytical Methodology & Evidence Contracts", description="Title")
    version: str = Field(default="1.0.0", description="Methodology version")
    last_updated_utc: str = Field(..., description="Timestamp of latest revision")
    anti_hoarding_charter: str = Field(
        ...,
        description="Core prohibition against calculating hoarding scores without ground-truth labels and market arrivals"
    )
    core_principles: List[MethodologicalPrinciple] = Field(..., description="Foundational operating principles")
    evidence_statuses: Dict[str, str] = Field(..., description="Definition of evidence levels")
    data_contracts: Dict[str, str] = Field(..., description="Domain rules enforced on each specific dataset")
