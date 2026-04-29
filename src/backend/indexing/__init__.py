"""Event handlers for profile and JD indexing events."""

from src.backend.indexing.jd_vectorizer import JDVectorizeResult, vectorize_and_index_jd

__all__ = [
    "JDVectorizeResult",
    "vectorize_and_index_jd",
]
