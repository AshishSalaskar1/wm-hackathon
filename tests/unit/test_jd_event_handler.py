"""Unit tests: JD Added event handler (SP2-007).

Tests the ``POST /events/jd`` endpoint for the ``jd.added`` event type:
  * Demand not found → 404.
  * Azure services not configured → 503.
  * JD vectorization failure → 500.
  * Happy-path: full pipeline runs, results stored, 202 returned.
  * Zero candidates above threshold: empty result list stored.
  * Idempotency: re-processing the same event produces the same DB state.
  * ``GET /demands/{id}/matches`` serves real results from the result store.
  * ``GET /demands/{id}/matches`` falls back to mock data for unprocessed demands.

No real Azure services are required; all external calls are mocked.
"""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass, field
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Stub all Azure SDK and OpenAI packages BEFORE importing src.api.main.
# This must run at module level before any local import that transitively
# pulls in those packages.
# ---------------------------------------------------------------------------
for _azure_mod in [
    "azure",
    "azure.identity",
    "azure.core",
    "azure.core.credentials",
    "azure.search",
    "azure.search.documents",
    "azure.search.documents.models",
    "openai",
]:
    if _azure_mod not in sys.modules:
        sys.modules[_azure_mod] = types.ModuleType(_azure_mod)

# Stub specific names used at import time in src.api.main.
_identity_stub = sys.modules["azure.identity"]
if not hasattr(_identity_stub, "DefaultAzureCredential"):
    _identity_stub.DefaultAzureCredential = MagicMock  # type: ignore[attr-defined]
if not hasattr(_identity_stub, "get_bearer_token_provider"):
    _identity_stub.get_bearer_token_provider = MagicMock()  # type: ignore[attr-defined]

_openai_stub = sys.modules["openai"]
if not hasattr(_openai_stub, "AzureOpenAI"):
    _openai_stub.AzureOpenAI = MagicMock  # type: ignore[attr-defined]

_search_docs_stub = sys.modules["azure.search.documents"]
if not hasattr(_search_docs_stub, "SearchClient"):
    _search_docs_stub.SearchClient = MagicMock  # type: ignore[attr-defined]

_search_models_stub = sys.modules["azure.search.documents.models"]
if not hasattr(_search_models_stub, "VectorizedQuery"):
    _search_models_stub.VectorizedQuery = MagicMock  # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Imports — must come AFTER the stubs above.
# ---------------------------------------------------------------------------
from fastapi.testclient import TestClient  # noqa: E402

import src.backend.matching.result_store as _rs_module  # noqa: E402
from src.backend.api.main import app  # noqa: E402
from src.backend.indexing.jd_vectorizer import JDVectorizeResult  # noqa: E402
from src.backend.matching.retriever import RetrievalCandidate  # noqa: E402
from src.backend.matching.result_store import get_result_store  # noqa: E402

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_result_store():
    """Reset the in-memory result store singleton between tests."""
    _rs_module._store = None
    yield
    _rs_module._store = None


def _make_candidate(
    employee_id: str = "EMP-00001",
    score_percent: int = 85,
    rank: int = 1,
) -> RetrievalCandidate:
    """Build a :class:`RetrievalCandidate` for use in mocked pipeline returns."""
    similarity = score_percent / 100.0
    return RetrievalCandidate(
        employee_id=employee_id,
        similarity_raw=similarity,
        similarity=similarity,
        score_percent=score_percent,
        rank=rank,
        document={
            "employee_name": f"Employee_{employee_id}",
            "band": "GROUP B2",
            "location": "HYDERABAD",
            "experience": "8Years 3Months",
            "work_mode": "OFFSHORE",
            "role_name": "Senior Developer",
            "skills_iaspire": "Python(L4), Azure(L3)",
            "certified_skills": None,
            "role_cluster": "DEVELOPER L3",
        },
    )


# ---------------------------------------------------------------------------
# Tests: jd.added — error paths
# ---------------------------------------------------------------------------


def test_jd_added_unknown_demand_returns_404() -> None:
    """Demand ID not in _MOCK_DEMANDS → 404 Not Found."""
    response = client.post(
        "/events/jd",
        json={"event_type": "jd.added", "demand_id": 9999},
    )
    assert response.status_code == 404
    assert "9999" in response.json()["detail"]


def test_jd_added_without_azure_config_returns_503() -> None:
    """Missing Azure endpoint env vars → 503 Service Unavailable."""
    # demand_id=1 exists in _MOCK_DEMANDS; no Azure env vars set.
    response = client.post(
        "/events/jd",
        json={"event_type": "jd.added", "demand_id": 1},
    )
    assert response.status_code == 503
    assert "AZURE_OPENAI_ENDPOINT" in response.json()["detail"]


def test_jd_added_jd_vectorize_failure_returns_500(monkeypatch: pytest.MonkeyPatch) -> None:
    """JD vectorization failure → 500 Internal Server Error."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake-openai.azure.com")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://fake-search.azure.com")

    failed_result = JDVectorizeResult(demand_id=1, status="failed", reason="upsert failed")
    with patch("src.api.main.vectorize_and_index_jd", return_value=failed_result):
        response = client.post(
            "/events/jd",
            json={"event_type": "jd.added", "demand_id": 1},
        )

    assert response.status_code == 500
    assert "vectorization failed" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Tests: jd.added — happy path
# ---------------------------------------------------------------------------


def test_jd_added_runs_pipeline_and_returns_202(monkeypatch: pytest.MonkeyPatch) -> None:
    """Happy path: full pipeline runs, results stored, 202 returned."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake-openai.azure.com")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://fake-search.azure.com")

    indexed_result = JDVectorizeResult(demand_id=1, status="indexed")
    candidates = [
        _make_candidate("EMP-00001", score_percent=90, rank=1),
        _make_candidate("EMP-00002", score_percent=82, rank=2),
    ]

    with (
        patch("src.api.main.vectorize_and_index_jd", return_value=indexed_result),
        patch("src.api.main.dense_retrieval", return_value=candidates),
    ):
        response = client.post(
            "/events/jd",
            json={"event_type": "jd.added", "demand_id": 1},
        )

    assert response.status_code == 202
    body = response.json()
    assert body["accepted"] is True
    assert "jd.added" in body["event_type"]
    assert "2 match result(s) stored" in body["message"]


def test_jd_added_pipeline_stores_results_in_result_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pipeline must persist ranked results to the Search Result DB."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake-openai.azure.com")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://fake-search.azure.com")

    indexed_result = JDVectorizeResult(demand_id=1, status="indexed")
    candidates = [
        _make_candidate("EMP-00001", score_percent=90, rank=1),
        _make_candidate("EMP-00002", score_percent=78, rank=2),
    ]

    with (
        patch("src.api.main.vectorize_and_index_jd", return_value=indexed_result),
        patch("src.api.main.dense_retrieval", return_value=candidates),
    ):
        client.post("/events/jd", json={"event_type": "jd.added", "demand_id": 1})

    store = get_result_store()
    assert store.demand_exists(1)
    results = store.get_results(1)
    assert results is not None
    assert len(results) == 2
    assert results[0].employee_id == "EMP-00001"
    assert results[0].score_percent == 90
    assert results[0].rank == 1
    assert results[1].employee_id == "EMP-00002"
    assert results[1].rank == 2


def test_jd_added_stored_results_contain_all_contract_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stored result documents must satisfy the SP0-009 contract schema."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake-openai.azure.com")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://fake-search.azure.com")

    indexed_result = JDVectorizeResult(demand_id=1, status="indexed")
    candidates = [_make_candidate("EMP-00001", score_percent=87, rank=1)]

    with (
        patch("src.api.main.vectorize_and_index_jd", return_value=indexed_result),
        patch("src.api.main.dense_retrieval", return_value=candidates),
    ):
        client.post("/events/jd", json={"event_type": "jd.added", "demand_id": 1})

    result = get_result_store().get_results(1)[0]  # type: ignore[index]
    # SP0-009 required fields
    assert result.demand_id == 1
    assert result.employee_id == "EMP-00001"
    assert isinstance(result.similarity_raw, float)
    assert 0.0 <= result.similarity <= 1.0
    assert 0 <= result.score_percent <= 100
    assert result.rank == 1
    assert result.retrieval_strategy in {"dense", "sparse", "hybrid"}
    assert result.timestamp  # non-empty ISO string


def test_jd_added_zero_candidates_above_threshold_stores_empty_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When no candidates pass the threshold, an empty result list is stored."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake-openai.azure.com")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://fake-search.azure.com")

    indexed_result = JDVectorizeResult(demand_id=1, status="indexed")
    # All candidates below the 70% threshold.
    low_candidates = [
        _make_candidate("EMP-00099", score_percent=60, rank=0),
        _make_candidate("EMP-00100", score_percent=55, rank=0),
    ]

    with (
        patch("src.api.main.vectorize_and_index_jd", return_value=indexed_result),
        patch("src.api.main.dense_retrieval", return_value=low_candidates),
    ):
        response = client.post(
            "/events/jd",
            json={"event_type": "jd.added", "demand_id": 1},
        )

    assert response.status_code == 202
    store = get_result_store()
    assert store.demand_exists(1)
    assert store.get_results(1) == []


def test_jd_added_is_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Re-processing the same jd.added event must produce the same DB state."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake-openai.azure.com")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://fake-search.azure.com")

    indexed_result = JDVectorizeResult(demand_id=2, status="indexed")
    candidates = [_make_candidate("EMP-00002", score_percent=88, rank=1)]

    payload = {"event_type": "jd.added", "demand_id": 2}
    with (
        patch("src.api.main.vectorize_and_index_jd", return_value=indexed_result),
        patch("src.api.main.dense_retrieval", return_value=candidates),
    ):
        client.post("/events/jd", json=payload)
        # Second call — same event.
        client.post("/events/jd", json=payload)

    store = get_result_store()
    results = store.get_results(2)
    assert results is not None
    assert len(results) == 1
    assert results[0].employee_id == "EMP-00002"
    assert results[0].score_percent == 88


# ---------------------------------------------------------------------------
# Tests: jd.modified and jd.deleted (pass-through until SP3-001/SP3-002)
# ---------------------------------------------------------------------------


def test_jd_modified_returns_202_without_pipeline() -> None:
    """jd.modified events are accepted without running the pipeline (SP3-001 scope)."""
    response = client.post(
        "/events/jd",
        json={"event_type": "jd.modified", "demand_id": 1},
    )
    assert response.status_code == 202
    assert response.json()["accepted"] is True


def test_jd_deleted_returns_202_without_pipeline() -> None:
    """jd.deleted events are accepted without running the pipeline (SP3-002 scope)."""
    response = client.post(
        "/events/jd",
        json={"event_type": "jd.deleted", "demand_id": 1},
    )
    assert response.status_code == 202


# ---------------------------------------------------------------------------
# Tests: GET /demands/{id}/matches — result store integration
# ---------------------------------------------------------------------------


def test_get_demand_matches_serves_real_results_from_store(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """After a jd.added pipeline run, GET /demands/{id}/matches returns real results."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake-openai.azure.com")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://fake-search.azure.com")

    indexed_result = JDVectorizeResult(demand_id=1, status="indexed")
    candidates = [_make_candidate("EMP-00001", score_percent=91, rank=1)]

    with (
        patch("src.api.main.vectorize_and_index_jd", return_value=indexed_result),
        patch("src.api.main.dense_retrieval", return_value=candidates),
    ):
        client.post("/events/jd", json={"event_type": "jd.added", "demand_id": 1})

    response = client.get("/demands/1/matches")
    assert response.status_code == 200
    body = response.json()
    assert body["demand_id"] == 1
    assert body["status"] == "READY"
    assert len(body["results"]) == 1
    result = body["results"][0]
    assert result["employee_id"] == "EMP-00001"
    assert result["similarity_score"] == 91
    assert result["rank"] == 1
    assert result["band"] == "GROUP B2"
    assert result["location"] == "HYDERABAD"
    assert result["below_threshold"] is False


def test_get_demand_matches_no_results_above_threshold_returns_no_results_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When zero candidates passed the threshold, status is NO_RESULTS."""
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake-openai.azure.com")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://fake-search.azure.com")

    indexed_result = JDVectorizeResult(demand_id=2, status="indexed")
    # No candidates above threshold.
    with (
        patch("src.api.main.vectorize_and_index_jd", return_value=indexed_result),
        patch("src.api.main.dense_retrieval", return_value=[]),
    ):
        client.post("/events/jd", json={"event_type": "jd.added", "demand_id": 2})

    response = client.get("/demands/2/matches")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "NO_RESULTS"
    assert body["results"] == []


def test_get_demand_matches_falls_back_to_mock_for_unprocessed_demand() -> None:
    """Demands never processed by the pipeline fall back to mock data."""
    # No pipeline run → result store is empty → mock data served.
    response = client.get("/demands/1/matches")
    assert response.status_code == 200
    body = response.json()
    # Mock data for demand_id=1 has READY status with results.
    assert body["status"] == "READY"
    assert len(body["results"]) > 0


def test_get_demand_matches_unknown_id_still_returns_404_from_mock() -> None:
    """Demand not in store or mock data → 404."""
    response = client.get("/demands/9999/matches")
    assert response.status_code == 404
