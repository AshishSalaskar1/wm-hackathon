"""Demand record completeness validation for the ingestion pipeline.

SP1-007: Demand records with fewer than 70% of defined fields populated are
rejected before reaching the matching engine.  The ``validate_demand_completeness``
function is the single entry-point for this check.
"""

from __future__ import annotations

import logging
import os
from datetime import date

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: All field names that contribute to the completeness score (14 total).
_DEMAND_FIELDS: tuple[str, ...] = (
    "demand_id",
    "customer_name",
    "essential_skill",
    "location",
    "country",
    "created_on",
    "start_date",
    "end_date",
    "role_description",
    "work_mode",
    "band",
    "open_positions",
    "job_description",
    "role_cluster",
)

_TOTAL_FIELDS: int = len(_DEMAND_FIELDS)  # 14


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class IncompleteDemandError(ValueError):
    """Raised when a demand record fails the 70% completeness threshold.

    Attributes:
        demand_id: Identifier of the rejected demand record.
        completeness: Computed completeness percentage (0.0–100.0).
    """

    def __init__(self, demand_id: int | str | None, completeness: float) -> None:
        self.demand_id = demand_id
        self.completeness = completeness
        super().__init__(
            f"Demand {demand_id!r} completeness {completeness:.1f}% is below the 70% threshold"
        )


# ---------------------------------------------------------------------------
# Ingestion input model
# ---------------------------------------------------------------------------


class DemandRecordInput(BaseModel):
    """Parsed demand record from an Excel ingestion source.

    All fields except ``demand_id`` are optional so that rows with missing
    columns can be constructed and subjected to completeness validation before
    the matching pipeline receives them.  This model is distinct from the API-
    layer ``DemandRecord`` model, which enforces all fields as required.
    """

    demand_id: int = Field(..., description="Unique Service Request identifier (SR_ID)")
    customer_name: str | None = Field(None, description="Business unit / customer name")
    essential_skill: str | None = Field(None, description="Primary required skill")
    location: str | None = Field(None, description="City where resource is required")
    country: str | None = Field(None, description="Country where resource is required")
    created_on: date | None = Field(None, description="Date the service request was raised")
    start_date: date | None = Field(None, description="Date by which resource is needed")
    end_date: date | None = Field(None, description="Expected end date of engagement")
    role_description: str | None = Field(None, description="Short role label")
    work_mode: str | None = Field(None, description="ONSITE or OFFSHORE")
    band: str | None = Field(None, description="Required experience band")
    open_positions: int | None = Field(None, description="Number of open headcount positions")
    job_description: str | None = Field(None, description="Full free-text job description")
    role_cluster: str | None = Field(None, description="Wipro role cluster name")


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


def validate_demand_completeness(record: DemandRecordInput) -> DemandRecordInput:
    """Validate that a demand record meets the minimum completeness threshold.

    Completeness is defined as::

        completeness = (count of non-null fields / 14 total fields) × 100

    Records with completeness < 70 are rejected with an
    :class:`IncompleteDemandError` that includes the demand ID and computed
    score.  Valid records are returned unchanged.

    The threshold is read from the ``MATCH_DEMAND_THRESHOLD`` environment
    variable (default ``70.0``).

    Args:
        record: Parsed demand record to validate.

    Returns:
        The original ``record`` when completeness >= threshold.

    Raises:
        IncompleteDemandError: When completeness < threshold.
    """
    threshold: float = float(os.getenv("MATCH_DEMAND_THRESHOLD", "70.0"))

    data = record.model_dump()
    populated = sum(1 for field in _DEMAND_FIELDS if data.get(field) is not None)
    completeness = populated / _TOTAL_FIELDS * 100

    if completeness < threshold:
        logger.warning(
            "Demand %r rejected: completeness %.1f%% < %.1f%% threshold",
            record.demand_id,
            completeness,
            threshold,
        )
        raise IncompleteDemandError(demand_id=record.demand_id, completeness=completeness)

    return record
