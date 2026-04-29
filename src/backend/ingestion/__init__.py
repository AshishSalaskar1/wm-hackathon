"""Supply profile ingestion, vectorization, and demand validation utilities."""

from src.backend.ingestion.demand_validator import (
    DemandRecordInput,
    IncompleteDemandError,
    validate_demand_completeness,
)
from src.backend.ingestion.vectorizer import (
    InsufficientDataError,
    build_embedding_text,
    vectorize_and_index,
)

__all__ = [
    "DemandRecordInput",
    "IncompleteDemandError",
    "InsufficientDataError",
    "build_embedding_text",
    "validate_demand_completeness",
    "vectorize_and_index",
]
