"""Unit tests: supply profile vectorization — build_embedding_text logic and HTTP contract."""

import os
from datetime import date
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.backend.api.main import ProfileVectorizeResult, SupplyProfile, app
from src.backend.ingestion import InsufficientDataError, build_embedding_text

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helper fixture
# ---------------------------------------------------------------------------


def _make_profile(**overrides) -> SupplyProfile:
    defaults = {
        "employee_id": "EMP-TEST",
        "employee_name": "Test Employee",
        "band": "GROUP B2",
        "availability_from": date(2026, 1, 1),
        "ageing_bucket": "0-30 DAYS",
        "work_mode": "OFFSHORE",
        "location": "HYDERABAD",
        "experience": "5Years 0Months",
        "country": "INDIA",
        "skills_iaspire": "Python(L4)",
        "certified_skills": None,
        "trained_skills": None,
        "recent_skills": None,
        "language_skills": None,
        "role_name": "Developer",
        "role_cluster": "DEVELOPER L2",
    }
    defaults.update(overrides)
    return SupplyProfile(**defaults)


# ---------------------------------------------------------------------------
# build_embedding_text tests
# ---------------------------------------------------------------------------


def test_primary_skills_in_text() -> None:
    profile = _make_profile(skills_iaspire="Python(L4)")
    text = build_embedding_text(profile)
    assert text.startswith("Skills: Python(L4).")


def test_certified_skills_appended() -> None:
    profile = _make_profile(skills_iaspire="Python", certified_skills="AZ-900")
    text = build_embedding_text(profile)
    assert "Skills: Python." in text
    assert "Certified: AZ-900." in text


def test_fallback_trained_skills() -> None:
    profile = _make_profile(skills_iaspire=None, certified_skills=None, trained_skills="Docker")
    text = build_embedding_text(profile)
    assert text.startswith("Trained Skills: Docker.")


def test_fallback_recent_skills() -> None:
    profile = _make_profile(
        skills_iaspire=None, certified_skills=None, trained_skills=None, recent_skills="K8s"
    )
    text = build_embedding_text(profile)
    assert text.startswith("Recent Skills: K8s.")


def test_all_null_raises_error() -> None:
    profile = _make_profile(
        skills_iaspire=None,
        certified_skills=None,
        trained_skills=None,
        recent_skills=None,
    )
    try:
        build_embedding_text(profile)
        assert False, "Expected InsufficientDataError"
    except InsufficientDataError as exc:
        assert exc.employee_id == "EMP-TEST"


def test_null_role_omitted() -> None:
    profile = _make_profile(role_name=None)
    text = build_embedding_text(profile)
    assert "Role:" not in text


def test_null_role_cluster_omitted() -> None:
    profile = _make_profile(role_cluster=None)
    text = build_embedding_text(profile)
    assert "Role Cluster:" not in text


def test_band_always_present() -> None:
    profile = _make_profile()
    text = build_embedding_text(profile)
    assert "Band:" in text


# ---------------------------------------------------------------------------
# HTTP endpoint contract tests
# ---------------------------------------------------------------------------

_VALID_PROFILE_PAYLOAD = {
    "employee_id": "EMP-TEST",
    "employee_name": "Test Employee",
    "band": "GROUP B2",
    "availability_from": "2026-01-01",
    "ageing_bucket": "0-30 DAYS",
    "work_mode": "OFFSHORE",
    "location": "HYDERABAD",
    "experience": "5Years 0Months",
    "country": "INDIA",
    "skills_iaspire": "Python(L4)",
    "certified_skills": None,
    "trained_skills": None,
    "recent_skills": None,
    "language_skills": None,
    "role_name": "Developer",
    "role_cluster": "DEVELOPER L2",
}


def test_vectorize_returns_200_when_all_indexed() -> None:
    mock_result = [ProfileVectorizeResult(employee_id="EMP-TEST", status="indexed")]
    with (
        patch("src.api.main.vectorize_and_index", return_value=mock_result),
        patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
                "AZURE_SEARCH_ENDPOINT": "https://test.search.windows.net",
            },
        ),
        patch("src.api.main.DefaultAzureCredential"),
        patch("src.api.main.AzureOpenAI"),
        patch("src.api.main.SearchClient"),
    ):
        response = client.post("/supply/vectorize", json={"profiles": [_VALID_PROFILE_PAYLOAD]})
    assert response.status_code == 200
    body = response.json()
    assert body["indexed"] == 1
    assert body["total"] == 1


def test_vectorize_returns_503_when_endpoint_not_set() -> None:
    env_without_endpoint = {k: v for k, v in os.environ.items() if k not in ("AZURE_OPENAI_ENDPOINT", "AZURE_SEARCH_ENDPOINT")}
    with patch.dict(os.environ, env_without_endpoint, clear=True):
        response = client.post("/supply/vectorize", json={"profiles": [_VALID_PROFILE_PAYLOAD]})
    assert response.status_code == 503


def test_vectorize_empty_profiles_returns_422() -> None:
    response = client.post("/supply/vectorize", json={"profiles": []})
    assert response.status_code == 422


def test_vectorize_skipped_profile_counted() -> None:
    mock_result = [
        ProfileVectorizeResult(
            employee_id="EMP-TEST", status="skipped", reason="All skill fields are null"
        )
    ]
    with (
        patch("src.api.main.vectorize_and_index", return_value=mock_result),
        patch.dict(
            os.environ,
            {
                "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
                "AZURE_SEARCH_ENDPOINT": "https://test.search.windows.net",
            },
        ),
        patch("src.api.main.DefaultAzureCredential"),
        patch("src.api.main.AzureOpenAI"),
        patch("src.api.main.SearchClient"),
    ):
        response = client.post("/supply/vectorize", json={"profiles": [_VALID_PROFILE_PAYLOAD]})
    assert response.status_code == 200
    body = response.json()
    assert body["skipped"] == 1
    assert body["indexed"] == 0


def test_batch_chunking_250_profiles_three_calls() -> None:
    """Verify that 250 profiles result in exactly 3 embeddings.create calls (100+100+50)."""
    from src.backend.ingestion.vectorizer import vectorize_and_index as real_vectorize_and_index

    profiles = [
        _make_profile(employee_id=f"EMP-{i:03d}") for i in range(250)
    ]

    # Mock openai_client with embeddings.create returning fake vectors
    mock_openai = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1, 0.2]) for _ in range(100)]
    mock_openai.embeddings.create.return_value = mock_response

    # Mock search_client — merge_or_upload_documents returns a list of succeeded results
    mock_search = MagicMock()
    mock_index_result = MagicMock()
    mock_index_result.succeeded = True
    mock_search.merge_or_upload_documents.return_value = [mock_index_result] * 250

    # Override the response.data length per batch call
    def embeddings_side_effect(input, model):  # noqa: A002
        batch_mock = MagicMock()
        batch_mock.data = [MagicMock(embedding=[0.1, 0.2]) for _ in range(len(input))]
        return batch_mock

    mock_openai.embeddings.create.side_effect = embeddings_side_effect

    real_vectorize_and_index(profiles, mock_openai, mock_search)

    assert mock_openai.embeddings.create.call_count == 3
