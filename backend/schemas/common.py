"""
Shared domain models and pagination primitives for Punjab GrainWatch API.
"""

from typing import Generic, List, Literal, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

EvidenceStatus = Literal[
    "observed",
    "derived",
    "metadata only",
    "blocked",
    "stale",
    "missing",
    "synthetic demo",
]

SourceRegistryStatus = Literal[
    "working-tested",
    "blocked-auth",
    "blocked-captcha",
    "metadata-only",
    "not-tested",
    "stale",
    "unavailable",
]


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard pagination wrapper for list endpoints."""
    total: int = Field(..., description="Total number of items matching filters")
    limit: int = Field(..., description="Number of items requested per page")
    offset: int = Field(..., description="Offset index from start of results")
    items: List[T] = Field(..., description="List of items for current page")


class ErrorResponse(BaseModel):
    """Standard error response structure."""
    detail: str = Field(..., description="Human-readable error description")
    error_code: Optional[str] = Field(default=None, description="Optional machine-readable error code")
