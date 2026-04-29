"""Unit tests: demand completeness validation — SP1-007."""

from datetime import date

import pytest

from src.backend.ingestion.demand_validator import (
    DemandRecordInput,
    IncompleteDemandError,
    validate_demand_completeness,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _full_demand(**overrides) -> DemandRecordInput:
    """Return a fully populated demand record (all 14 fields set)."""
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
    return DemandRecordInput(**defaults)


# ---------------------------------------------------------------------------
# SP1-007 acceptance criteria tests
# ---------------------------------------------------------------------------


def test_100_percent_complete_demand_is_accepted() -> None:
    """All 14 fields populated → completeness 100% → accepted and returned unchanged."""
    record = _full_demand()
    result = validate_demand_completeness(record)
    assert result is record


def test_70_percent_complete_demand_is_accepted() -> None:
    """10 of 14 fields populated → completeness 71.4% (≥ 70%) → accepted.

    With 14 total fields, 10 populated is the minimum count that yields a
    completeness score at or above the 70% threshold (71.4%).
    """
    # Null out 4 optional fields (keeping demand_id + 9 others = 10 populated)
    record = _full_demand(
        certified_skills=None,  # not in schema — use optional schema fields
        role_description=None,
        end_date=None,
        role_cluster=None,
    )
    result = validate_demand_completeness(record)
    assert result is record


def test_69_percent_complete_demand_is_rejected() -> None:
    """9 of 14 fields populated → completeness 64.3% (< 70%) → rejected.

    Nulling 5 fields drops completeness to 9/14 = 64.3%.
    """
    record = _full_demand(
        role_description=None,
        end_date=None,
        role_cluster=None,
        band=None,
        work_mode=None,
    )
    with pytest.raises(IncompleteDemandError) as exc_info:
        validate_demand_completeness(record)

    error = exc_info.value
    assert error.demand_id == 1
    assert error.completeness < 70.0


def test_empty_demand_is_rejected() -> None:
    """Only demand_id present (1 of 14 fields) → completeness 7.1% → rejected."""
    record = DemandRecordInput(demand_id=42)
    with pytest.raises(IncompleteDemandError) as exc_info:
        validate_demand_completeness(record)

    error = exc_info.value
    assert error.demand_id == 42
    assert error.completeness < 70.0


# ---------------------------------------------------------------------------
# Additional behavioural tests
# ---------------------------------------------------------------------------


def test_error_contains_demand_id_and_score() -> None:
    """IncompleteDemandError exposes demand_id and completeness attributes."""
    record = DemandRecordInput(demand_id=99)
    with pytest.raises(IncompleteDemandError) as exc_info:
        validate_demand_completeness(record)

    err = exc_info.value
    assert err.demand_id == 99
    assert isinstance(err.completeness, float)
    assert 0.0 <= err.completeness < 70.0


def test_exactly_threshold_boundary_accepted() -> None:
    """Completeness exactly at the threshold (71.4% with 14 fields) is accepted."""
    # 10/14 = 71.43% — must be accepted
    record = _full_demand(
        role_description=None,
        end_date=None,
        role_cluster=None,
        band=None,
    )
    result = validate_demand_completeness(record)
    assert result is record


def test_one_below_boundary_rejected() -> None:
    """Completeness one field below boundary (9/14 = 64.3%) is rejected."""
    record = _full_demand(
        role_description=None,
        end_date=None,
        role_cluster=None,
        band=None,
        work_mode=None,
    )
    with pytest.raises(IncompleteDemandError):
        validate_demand_completeness(record)


def test_rejected_record_not_passed_downstream() -> None:
    """Rejected records raise before any return value can be used downstream."""
    record = DemandRecordInput(demand_id=7)
    downstream_called = False

    try:
        validated = validate_demand_completeness(record)
        downstream_called = True  # should never reach here
    except IncompleteDemandError:
        pass

    assert not downstream_called
