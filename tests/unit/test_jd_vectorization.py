"""Unit tests: JD vectorization — SP2-006.

Tests ``vectorize_and_index_jd`` and the underlying ``build_demand_embedding_text``
serialiser using fully mocked Azure OpenAI and Azure AI Search clients.
No real Azure services are required.
"""

from __future__ import annotations

import os
import sys
import types
from datetime import date
from typing import Any
from unittest.mock import MagicMock

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

# Ensure VectorizedQuery is importable from the stub (required by retriever.py
# at import time so that the test module can import it transitively).
_search_models_stub = sys.modules["azure.search.documents.models"]
if not hasattr(_search_models_stub, "VectorizedQuery"):
    _search_models_stub.VectorizedQuery = MagicMock  # type: ignore[attr-defined]

from src.backend.indexing.jd_vectorizer import JDVectorizeResult, vectorize_and_index_jd  # noqa: E402
from src.backend.matching.retriever import build_demand_embedding_text  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_demand(**overrides) -> Any:
    """Return a SimpleNamespace that mimics DemandRecord attribute access.

    All 14 demand schema fields are populated by default.  Pass keyword
    overrides to create sparse or edge-case records.
    """
    defaults = {
        "demand_id": 101,
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
    return types.SimpleNamespace(**defaults)


def _make_openai_client(vector: list[float] | None = None) -> MagicMock:
    """Return a mock AzureOpenAI client that returns a fixed embedding vector."""
    if vector is None:
        vector = [0.1, 0.2, 0.3]
    mock_embedding = MagicMock()
    mock_embedding.embedding = vector
    mock_response = MagicMock()
    mock_response.data = [mock_embedding]
    client = MagicMock()
    client.embeddings.create.return_value = mock_response
    return client


def _make_search_client(succeeded: bool = True) -> MagicMock:
    """Return a mock Azure AI Search client with a configurable upsert result."""
    mock_result = MagicMock()
    mock_result.succeeded = succeeded
    client = MagicMock()
    client.merge_or_upload_documents.return_value = [mock_result]
    return client


# ---------------------------------------------------------------------------
# Embedding text serialisation tests (build_demand_embedding_text)
# ---------------------------------------------------------------------------


def test_full_demand_embedding_text_contains_all_attributes() -> None:
    """Full demand record should produce embedding text with every key attribute."""
    demand = _make_demand()
    text = build_demand_embedding_text(demand)

    assert "Data Engineer L2" in text       # role_description
    assert "DATA ENGINEER L2" in text       # role_cluster
    assert "Python" in text                 # essential_skill
    assert "GROUP C1" in text               # band
    assert "BANGALORE" in text              # location
    assert "INDIA" in text                  # country
    assert "OFFSHORE" in text               # work_mode
    assert "Data Engineer with Python" in text  # job_description


def test_sparse_demand_embedding_text_handles_none_fields() -> None:
    """Sparse demand with several None fields should still produce non-empty text."""
    demand = _make_demand(
        role_description=None,
        role_cluster=None,
        location=None,
        country=None,
        work_mode=None,
        job_description=None,
        band=None,
    )
    text = build_demand_embedding_text(demand)

    assert "Python" in text   # essential_skill always present
    assert len(text) > 0


def test_embedding_text_is_deterministic() -> None:
    """Same demand record must always produce the same embedding text."""
    demand = _make_demand()
    assert build_demand_embedding_text(demand) == build_demand_embedding_text(demand)


def test_none_fields_not_present_in_embedding_text() -> None:
    """Attributes set to None should be omitted from the embedding text."""
    demand = _make_demand(role_cluster=None, work_mode=None)
    text = build_demand_embedding_text(demand)

    assert "Role Cluster:" not in text
    assert "Work Mode:" not in text


# ---------------------------------------------------------------------------
# vectorize_and_index_jd — happy path tests
# ---------------------------------------------------------------------------


def test_full_demand_indexed_successfully() -> None:
    """A fully populated demand record should return status 'indexed'."""
    demand = _make_demand()
    result = vectorize_and_index_jd(demand, _make_openai_client(), _make_search_client())

    assert isinstance(result, JDVectorizeResult)
    assert result.status == "indexed"
    assert result.demand_id == 101
    assert result.reason is None


def test_sparse_demand_above_threshold_indexed_successfully() -> None:
    """Sparse demand record (above 70% completeness) should be indexed without error.

    10 of 14 schema fields populated = ~71% completeness, which satisfies the
    SP1-007 threshold (≥70%).
    """
    demand = _make_demand(
        # Leave 4 fields as None: job_description, role_cluster, created_on, end_date
        job_description=None,
        role_cluster=None,
        created_on=None,
        end_date=None,
    )
    result = vectorize_and_index_jd(demand, _make_openai_client(), _make_search_client())

    assert result.status == "indexed"


def test_jd_index_document_keyed_by_demand_id() -> None:
    """The JD Index document must use str(demand_id) as the 'id' key."""
    demand = _make_demand(demand_id=42)
    search_client = _make_search_client()

    vectorize_and_index_jd(demand, _make_openai_client(), search_client)

    documents = search_client.merge_or_upload_documents.call_args.kwargs["documents"]
    assert documents[0]["id"] == "42"
    assert documents[0]["demand_id"] == 42


def test_content_vector_stored_in_jd_document() -> None:
    """The embedding vector must be stored as 'content_vector' in the document."""
    expected_vector = [0.5, 0.6, 0.7, 0.8]
    search_client = _make_search_client()

    vectorize_and_index_jd(
        _make_demand(),
        _make_openai_client(vector=expected_vector),
        search_client,
    )

    documents = search_client.merge_or_upload_documents.call_args.kwargs["documents"]
    assert documents[0]["content_vector"] == expected_vector


def test_openai_called_with_configured_deployment() -> None:
    """The embedding API must be called with the AZURE_OPENAI_EMBEDDING_DEPLOYMENT model."""
    os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"] = "text-embedding-3-small"
    openai_client = _make_openai_client()

    vectorize_and_index_jd(_make_demand(), openai_client, _make_search_client())

    call_kwargs = openai_client.embeddings.create.call_args.kwargs
    assert call_kwargs["model"] == "text-embedding-3-small"


def test_revectorizing_same_demand_sends_identical_embedding_text() -> None:
    """Re-vectorizing the same demand must send the same text to the embedding API."""
    demand = _make_demand()

    openai_client_1 = _make_openai_client()
    vectorize_and_index_jd(demand, openai_client_1, _make_search_client())
    first_input = openai_client_1.embeddings.create.call_args.kwargs["input"]

    openai_client_2 = _make_openai_client()
    vectorize_and_index_jd(demand, openai_client_2, _make_search_client())
    second_input = openai_client_2.embeddings.create.call_args.kwargs["input"]

    assert first_input == second_input


# ---------------------------------------------------------------------------
# vectorize_and_index_jd — failure / edge-case tests
# ---------------------------------------------------------------------------


def test_upsert_failure_returns_failed_status() -> None:
    """When the AI Search upsert fails, the result status must be 'failed'."""
    result = vectorize_and_index_jd(
        _make_demand(),
        _make_openai_client(),
        _make_search_client(succeeded=False),
    )

    assert result.status == "failed"
    assert result.reason is not None
    assert "failed" in result.reason.lower()


def test_demand_id_preserved_in_failure_result() -> None:
    """The demand_id must be present on the result even when the upsert fails."""
    result = vectorize_and_index_jd(
        _make_demand(demand_id=99),
        _make_openai_client(),
        _make_search_client(succeeded=False),
    )

    assert result.demand_id == 99
