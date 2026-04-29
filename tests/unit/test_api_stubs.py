"""Unit tests: stub API endpoints return correct status codes and payload shapes."""

from fastapi.testclient import TestClient

from src.backend.api.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body


def test_list_demands_returns_200_with_list() -> None:
    response = client.get("/demands")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) > 0
    first = body[0]
    assert "demand_id" in first
    assert "essential_skill" in first
    assert "job_description" in first


def test_create_demand_returns_201() -> None:
    payload = {
        "demand_id": 99,
        "customer_name": "CustomerTest",
        "essential_skill": "Go",
        "location": "CHENNAI",
        "country": "INDIA",
        "created_on": "2026-04-28",
        "start_date": "2026-05-10",
        "end_date": "2026-06-30",
        "role_description": "Backend Engineer L2",
        "work_mode": "OFFSHORE",
        "band": "GROUP C1",
        "open_positions": 1,
        "job_description": "Backend engineer with Go and Kubernetes experience.",
        "role_cluster": "DEVELOPER L2",
    }
    response = client.post("/demands", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["demand_id"] == 99
    assert body["essential_skill"] == "Go"


def test_get_demand_matches_known_id_returns_200() -> None:
    response = client.get("/demands/1/matches")
    assert response.status_code == 200
    body = response.json()
    assert body["demand_id"] == 1
    assert body["status"] in {"READY", "NO_RESULTS", "MATCHING_IN_PROGRESS"}
    assert isinstance(body["results"], list)


def test_get_demand_matches_with_results_has_required_fields() -> None:
    response = client.get("/demands/1/matches")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "READY"
    result = body["results"][0]
    assert result["rank"] == 1
    assert 0 <= result["similarity_score"] <= 100
    assert "employee_id" in result
    assert "below_threshold" in result


def test_get_demand_matches_no_results_returns_no_results_status() -> None:
    response = client.get("/demands/3/matches")
    assert response.status_code == 200
    body = response.json()
    assert body["demand_id"] == 3
    assert body["status"] == "NO_RESULTS"
    assert body["results"] == []


def test_get_demand_matches_unknown_id_returns_404() -> None:
    response = client.get("/demands/9999/matches")
    assert response.status_code == 404


def test_list_supply_returns_200_with_list() -> None:
    response = client.get("/supply")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) > 0
    first = body[0]
    assert "employee_id" in first
    assert "band" in first
    assert "location" in first


def test_get_demand_matches_page2_returns_below_threshold_candidates() -> None:
    response = client.get("/demands/1/matches?page=2")
    assert response.status_code == 200
    body = response.json()
    assert body["demand_id"] == 1
    assert body["page"] == 2
    assert isinstance(body["results"], list)
    assert len(body["results"]) > 0
    for result in body["results"]:
        assert result["below_threshold"] is True
        assert result["similarity_score"] < 70


def test_post_events_profile_added_returns_202() -> None:
    payload = {
        "event_type": "profile.added",
        "employee_id": "EMP-00099",
        "blob_url": "https://sa.blob.core.windows.net/supply-uploads/EMP-00099.xlsx",
        "correlation_id": "corr-abc-123",
    }
    response = client.post("/events/profile", json=payload)
    assert response.status_code == 202
    body = response.json()
    assert body["accepted"] is True
    assert body["event_type"] == "profile.added"
    assert "EMP-00099" in body["message"]


def test_post_events_profile_deleted_returns_202() -> None:
    payload = {
        "event_type": "profile.deleted",
        "employee_id": "EMP-00001",
        "blob_url": None,
    }
    response = client.post("/events/profile", json=payload)
    assert response.status_code == 202
    body = response.json()
    assert body["accepted"] is True
    assert body["event_type"] == "profile.deleted"


def test_post_events_profile_invalid_type_returns_422() -> None:
    payload = {"event_type": "unknown.event", "employee_id": "EMP-00001"}
    response = client.post("/events/profile", json=payload)
    assert response.status_code == 422


def test_post_events_jd_added_returns_202() -> None:
    payload = {
        "event_type": "jd.added",
        "demand_id": 1,
        "blob_url": "https://sa.blob.core.windows.net/demand-uploads/demand-1.xlsx",
        "correlation_id": "corr-xyz-456",
    }
    response = client.post("/events/jd", json=payload)
    assert response.status_code == 202
    body = response.json()
    assert body["accepted"] is True
    assert body["event_type"] == "jd.added"
    assert "1" in body["message"]


def test_post_events_jd_deleted_returns_202() -> None:
    payload = {
        "event_type": "jd.deleted",
        "demand_id": 2,
        "blob_url": None,
    }
    response = client.post("/events/jd", json=payload)
    assert response.status_code == 202
    body = response.json()
    assert body["accepted"] is True
    assert body["event_type"] == "jd.deleted"


def test_post_events_jd_invalid_type_returns_422() -> None:
    payload = {"event_type": "unknown.event", "demand_id": 1}
    response = client.post("/events/jd", json=payload)
    assert response.status_code == 422
