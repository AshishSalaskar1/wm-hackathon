"""Search Result DB interface — SP2-007.

Stores ranked match results produced by the JD event handler pipeline.
Backed by a thread-safe in-memory dict in dev mode.  The interface is
designed to be swapped for Azure Cosmos DB in production (SP0-002)
without changing calling code.

Schema follows ``docs/contracts/similarity-and-cache-contract.md`` (SP0-009):
  * ``similarity_raw``  — float as returned by the retrieval engine.
  * ``similarity``      — canonical float in [0.0, 1.0] after normalization.
  * ``score_percent``   — integer in [0, 100] for UI display.
  * Cache key           — ``{demand_id}:{supply_index_version}`` (SP3-003).
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result document model
# ---------------------------------------------------------------------------


@dataclass
class StoredMatchResult:
    """One ranked result document written to the Search Result DB.

    Schema per ``docs/contracts/similarity-and-cache-contract.md`` (SP0-009).
    Supply profile attributes are denormalized so the API read path does not
    require a second look-up into the supply index.

    Attributes:
        demand_id: Demand identifier (SR_ID).
        employee_id: Anonymized employee identifier.
        similarity_raw: Raw score from the retrieval engine (auditing).
        similarity: Canonical score in [0.0, 1.0] after normalization.
        score_percent: Integer display score in [0, 100].
        rank: 1-based rank position within this demand's shortlist.
        retrieval_strategy: ``"dense"`` | ``"sparse"`` | ``"hybrid"``.
        timestamp: ISO-8601 UTC timestamp when the result was stored.
        employee_name: Denormalized from supply index.
        band: Experience band, denormalized from supply index.
        location: City of posting, denormalized from supply index.
        experience: Experience string, denormalized from supply index.
        work_mode: ``"ONSITE"`` or ``"OFFSHORE"``, denormalized.
        role_name: Designation / role (nullable).
        skills_iaspire: Primary skills (nullable).
        certified_skills: Certified skills (nullable).
        role_cluster: Role cluster (nullable).
        below_threshold: ``True`` for pagination-page-2+ results below 70%.
    """

    demand_id: int
    employee_id: str
    similarity_raw: float
    similarity: float
    score_percent: int
    rank: int
    retrieval_strategy: str
    timestamp: str
    # Denormalized supply profile fields (populated from RetrievalCandidate.document)
    employee_name: str = ""
    band: str = ""
    location: str = ""
    experience: str = ""
    work_mode: str = ""
    role_name: str | None = None
    skills_iaspire: str | None = None
    certified_skills: str | None = None
    role_cluster: str | None = None
    below_threshold: bool = False


# ---------------------------------------------------------------------------
# In-memory result store
# ---------------------------------------------------------------------------


class InMemoryResultStore:
    """Thread-safe in-memory implementation of the Search Result DB.

    Provides upsert, get, clear, and delete operations.  All mutations are
    idempotent: calling :meth:`upsert_results` twice with the same
    ``demand_id`` replaces the previous results rather than duplicating them.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # demand_id → list of StoredMatchResult ordered by rank ascending
        self._results: dict[int, list[StoredMatchResult]] = {}

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def upsert_results(
        self,
        demand_id: int,
        results: list[StoredMatchResult],
    ) -> None:
        """Replace all stored results for *demand_id* with *results* (idempotent).

        Args:
            demand_id: Demand identifier (SR_ID).
            results: Ranked list of :class:`StoredMatchResult` items, ordered
                by rank ascending.  An empty list is valid and signals that
                matching completed but no candidates met the threshold.
        """
        with self._lock:
            self._results[demand_id] = list(results)
        logger.info(
            "result_store upsert demand_id=%s result_count=%d",
            demand_id,
            len(results),
        )

    def clear_results(self, demand_id: int) -> None:
        """Remove stored results for *demand_id* without deleting the demand key.

        Used by the JD Modify handler (SP3-001) to signal that matching is
        in-progress while new results are being computed.  After clearing,
        :meth:`demand_exists` returns ``False``.
        """
        with self._lock:
            self._results.pop(demand_id, None)
        logger.info("result_store clear demand_id=%s", demand_id)

    def delete_demand(self, demand_id: int) -> None:
        """Permanently remove all data for *demand_id* (used by JD Delete, SP3-002).

        Idempotent: calling on an absent ``demand_id`` is a no-op.
        """
        with self._lock:
            self._results.pop(demand_id, None)
        logger.info("result_store delete demand_id=%s", demand_id)

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_results(self, demand_id: int) -> list[StoredMatchResult] | None:
        """Return stored results for *demand_id* or ``None`` when not found.

        Returns an empty list when the demand has been processed but produced
        zero results above the threshold (distinct from ``None``, which means
        the demand has never been processed).

        Args:
            demand_id: Demand identifier to look up.

        Returns:
            List of :class:`StoredMatchResult` ordered by rank, or ``None``
            when no results have been stored for the demand.
        """
        with self._lock:
            return self._results.get(demand_id)

    def demand_exists(self, demand_id: int) -> bool:
        """Return ``True`` when *demand_id* has been processed and results stored."""
        with self._lock:
            return demand_id in self._results


# ---------------------------------------------------------------------------
# Module-level singleton (one store per process)
# ---------------------------------------------------------------------------

_store: InMemoryResultStore | None = None
_store_lock = threading.Lock()


def get_result_store() -> InMemoryResultStore:
    """Return the module-level :class:`InMemoryResultStore` singleton.

    Thread-safe double-checked locking ensures a single store is created
    even under concurrent initialisation.
    """
    global _store  # noqa: PLW0603
    if _store is None:
        with _store_lock:
            if _store is None:
                _store = InMemoryResultStore()
    return _store
