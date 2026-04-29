"""Unit tests: dense semantic retrieval — SP2-001.

Tests the demand embedding text builder and the DenseRetrievalStrategy using
fully mocked Azure OpenAI and Azure AI Search clients.  No real Azure services
are required.
"""

from __future__ import annotations

import sys
import types
from datetime import date
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Stub missing Azure SDK packages so tests run without the SDK installed.
# This must happen before any local module that transitively imports azure.
# ---------------------------------------------------------------------------
for _azure_mod in [
    "azure",
    "azure.identity",
    "azure.core",
    "azure.core.credentials",
    "azure.search",
    "azure.search.documents",
    "azure.search.documents.models",
]:
    if _azure_mod not in sys.modules:
        sys.modules[_azure_mod] = types.ModuleType(_azure_mod)

# Ensure VectorizedQuery is importable from the stub
_search_models_stub = sys.modules["azure.search.documents.models"]
if not hasattr(_search_models_stub, "VectorizedQuery"):
    _search_models_stub.VectorizedQuery = MagicMock  # type: ignore[attr-defined]

from src.backend.matching.retriever import (  # noqa: E402
    DenseRetrievalStrategy,
    RetrievalCandidate,
    RetrievalStrategy,
    build_demand_embedding_text,
    dense_retrieval,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_demand(**overrides) -> Any:
    """Return a SimpleNamespace that mimics DemandRecord attribute access.

    Using SimpleNamespace avoids importing src.api.main (which requires the
    azure SDK) while still exercising build_demand_embedding_text, which only
    performs attribute reads.
    """
    import types as _types  # noqa: PLC0415

    defaults = {
        "demand_id": 1,
        "customer_name": "CustomerA",
        "essential_skill": "Python",
        "location": "BANGALORE",
        "country": "INDIA",
        "created_on": date(2026, 4, 1),
        "start_date": date(2026, 5, 1),
        "end_date": date(2026, 6, 30),
        "role_description": "Data Engineer L2",
        "work_mode": "OFFSHORE",
        "band": "GROUP C1",
        "open_positions": 2,
        "job_description": "Seeking a Data Engineer with Python and Azure skills.",
        "role_cluster": "DATA ENGINEER L2",
    }
    defaults.update(overrides)
    return _types.SimpleNamespace(**defaults)


def _make_openai_client(vector: list[float] | None = None) -> MagicMock:
    """Return a mock AzureOpenAI client that returns a fixed embedding."""
    if vector is None:
        vector = [0.1] * 1536

    mock_item = MagicMock()
    mock_item.embedding = vector

    mock_response = MagicMock()
    mock_response.data = [mock_item]

    client = MagicMock()
    client.embeddings.create.return_value = mock_response
    return client


def _make_search_result(employee_id: str, score: float, **extra) -> dict:
    """Return a dict that behaves like an Azure AI Search result document."""
    doc = {
        "employee_id": employee_id,
        "id": employee_id,
        "@search.score": score,
        "band": "GROUP B2",
        "location": "BANGALORE",
        "experience": "5Years 0Months",
        "role_name": "Engineer",
        "work_mode": "OFFSHORE",
        "country": "INDIA",
        "skills_iaspire": "Python(L4)",
        "certified_skills": None,
        "role_cluster": "DATA ENGINEER L2",
    }
    doc.update(extra)
    return doc


def _make_search_client(results: list[dict]) -> MagicMock:
    """Return a mock SearchClient that returns the given result dicts.

    Azure AI Search results support dict-style ``.get()`` access and can be
    passed to ``dict()``.  Plain Python dicts satisfy both contracts.
    """
    client = MagicMock()
    client.search.return_value = iter(results)
    return client


# ---------------------------------------------------------------------------
# build_demand_embedding_text tests
# ---------------------------------------------------------------------------


class TestBuildDemandEmbeddingText:
    def test_all_fields_appear_in_text(self) -> None:
        demand = _make_demand()
        text = build_demand_embedding_text(demand)
        assert "Role: Data Engineer L2." in text
        assert "Role Cluster: DATA ENGINEER L2." in text
        assert "Essential Skill: Python." in text
        assert "Band: GROUP C1." in text
        assert "Location: BANGALORE." in text
        assert "Country: INDIA." in text
        assert "Work Mode: OFFSHORE." in text
        assert "Job Description:" in text
        assert "Python and Azure" in text

    def test_text_is_non_empty(self) -> None:
        demand = _make_demand()
        text = build_demand_embedding_text(demand)
        assert len(text) > 0

    def test_structure_mirrors_supply_profile_format(self) -> None:
        """Key: demand text starts with structured fields, ends with free-text JD."""
        demand = _make_demand()
        text = build_demand_embedding_text(demand)
        # Role is the first structured field
        assert text.startswith("Role:")
        # JD content appears last (after structured attributes)
        jd_pos = text.index("Job Description:")
        band_pos = text.index("Band:")
        assert band_pos < jd_pos

    def test_deterministic_for_same_input(self) -> None:
        demand = _make_demand()
        assert build_demand_embedding_text(demand) == build_demand_embedding_text(demand)


# ---------------------------------------------------------------------------
# DenseRetrievalStrategy unit tests
# ---------------------------------------------------------------------------


class TestDenseRetrievalStrategy:
    """Tests using fully mocked clients — no real Azure services required."""

    def _run(
        self,
        demand=None,
        search_results: list[dict] | None = None,
        top_n: int = 50,
    ) -> list[RetrievalCandidate]:
        if demand is None:
            demand = _make_demand()
        if search_results is None:
            search_results = [
                _make_search_result("EMP-001", 0.92),
                _make_search_result("EMP-002", 0.81),
                _make_search_result("EMP-003", 0.74),
            ]

        openai_client = _make_openai_client()
        search_client = _make_search_client(search_results)

        strategy = DenseRetrievalStrategy()
        return strategy.retrieve(
            demand, openai_client, search_client, top_n=top_n
        )

    def test_returns_list_of_retrieval_candidates(self) -> None:
        candidates = self._run()
        assert isinstance(candidates, list)
        assert all(isinstance(c, RetrievalCandidate) for c in candidates)

    def test_candidates_sorted_descending_by_similarity(self) -> None:
        results = [
            _make_search_result("EMP-B", 0.70),
            _make_search_result("EMP-A", 0.92),
            _make_search_result("EMP-C", 0.55),
        ]
        candidates = self._run(search_results=results)
        scores = [c.similarity_raw for c in candidates]
        assert scores == sorted(scores, reverse=True)

    def test_correct_candidate_order_matches_expected(self) -> None:
        results = [
            _make_search_result("EMP-LOW", 0.60),
            _make_search_result("EMP-HIGH", 0.95),
            _make_search_result("EMP-MID", 0.80),
        ]
        candidates = self._run(search_results=results)
        assert candidates[0].employee_id == "EMP-HIGH"
        assert candidates[1].employee_id == "EMP-MID"
        assert candidates[2].employee_id == "EMP-LOW"

    def test_similarity_raw_preserved_from_search_score(self) -> None:
        results = [_make_search_result("EMP-001", 0.871234)]
        candidates = self._run(search_results=results)
        assert len(candidates) == 1
        assert abs(candidates[0].similarity_raw - 0.871234) < 1e-6

    def test_document_dict_attached_to_candidate(self) -> None:
        results = [_make_search_result("EMP-001", 0.90, band="GROUP C1")]
        candidates = self._run(search_results=results)
        assert candidates[0].document.get("band") == "GROUP C1"

    def test_empty_search_results_returns_empty_list(self) -> None:
        candidates = self._run(search_results=[])
        assert candidates == []

    def test_openai_embedding_called_once_per_demand(self) -> None:
        demand = _make_demand()
        openai_client = _make_openai_client()
        search_client = _make_search_client([])

        DenseRetrievalStrategy().retrieve(demand, openai_client, search_client)

        openai_client.embeddings.create.assert_called_once()

    def test_search_called_with_vector_query(self) -> None:
        demand = _make_demand()
        openai_client = _make_openai_client()
        search_client = _make_search_client([])

        DenseRetrievalStrategy().retrieve(demand, openai_client, search_client)

        search_client.search.assert_called_once()
        call_kwargs = search_client.search.call_args
        # search_text should be None for a pure vector query
        assert call_kwargs.kwargs.get("search_text") is None
        vector_queries = call_kwargs.kwargs.get("vector_queries")
        assert vector_queries is not None
        assert len(vector_queries) == 1

    def test_large_candidate_set_sorted_correctly(self) -> None:
        """50 candidates returned in expected descending order."""
        import random

        rng = random.Random(42)
        scores = [rng.uniform(0.5, 1.0) for _ in range(50)]
        results = [
            _make_search_result(f"EMP-{i:03d}", scores[i]) for i in range(50)
        ]
        candidates = self._run(search_results=results, top_n=50)
        assert len(candidates) == 50
        retrieved_scores = [c.similarity_raw for c in candidates]
        assert retrieved_scores == sorted(retrieved_scores, reverse=True)


# ---------------------------------------------------------------------------
# RetrievalStrategy protocol conformance
# ---------------------------------------------------------------------------


def test_dense_strategy_conforms_to_protocol() -> None:
    """DenseRetrievalStrategy satisfies the RetrievalStrategy protocol."""
    strategy = DenseRetrievalStrategy()
    assert isinstance(strategy, RetrievalStrategy)


# ---------------------------------------------------------------------------
# dense_retrieval convenience function
# ---------------------------------------------------------------------------


def test_dense_retrieval_function_delegates_to_strategy() -> None:
    """dense_retrieval() produces the same results as DenseRetrievalStrategy.retrieve()."""
    demand = _make_demand()
    search_results = [
        _make_search_result("EMP-A", 0.90),
        _make_search_result("EMP-B", 0.75),
    ]
    openai_client = _make_openai_client()
    search_client = _make_search_client(search_results)

    result = dense_retrieval(demand, openai_client, search_client)

    assert len(result) == 2
    assert result[0].similarity_raw >= result[1].similarity_raw
