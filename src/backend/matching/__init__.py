"""Vectorization and retrieval engine for demand-supply matching."""

from src.backend.matching.result_store import (
    InMemoryResultStore,
    StoredMatchResult,
    get_result_store,
)
from src.backend.matching.retriever import (
    DenseRetrievalStrategy,
    RetrievalCandidate,
    RetrievalStrategy,
    apply_threshold,
    build_demand_embedding_text,
    dense_retrieval,
    rank_shortlist,
)

__all__ = [
    "DenseRetrievalStrategy",
    "InMemoryResultStore",
    "RetrievalCandidate",
    "RetrievalStrategy",
    "StoredMatchResult",
    "apply_threshold",
    "build_demand_embedding_text",
    "dense_retrieval",
    "get_result_store",
    "rank_shortlist",
]
