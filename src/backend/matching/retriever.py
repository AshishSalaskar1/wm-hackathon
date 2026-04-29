"""Dense semantic retrieval against Azure AI Search — SP2-001.

This module implements the :class:`RetrievalStrategy` protocol and a concrete
:class:`DenseRetrievalStrategy` that queries the vectorized supply profile
index using an embedding generated from a demand record.  The same
:class:`RetrievalStrategy` interface is extended by SP2-008 (sparse and hybrid
strategies) so all three can be swapped via the ``RETRIEVAL_STRATEGY``
environment variable without code changes.
"""

from __future__ import annotations

import logging
import math
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from src.backend.api.main import DemandRecord

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Output model
# ---------------------------------------------------------------------------


@dataclass
class RetrievalCandidate:
    """A single supply profile candidate returned from the retrieval layer.

    Attributes:
        employee_id: Anonymized employee identifier (matches AI Search document key).
        similarity_raw: Raw similarity score as returned by the retrieval engine
            (range 0.0–1.0 for Azure AI Search cosine/dot-product; stored for
            auditing per the similarity-and-cache contract).
        similarity: Normalized canonical score in [0.0, 1.0] after applying the
            domain conversion and clamping rules from the similarity contract
            (SP2-002).  This is the value stored in the Search Result DB.
        score_percent: Integer display score in [0, 100] computed as
            ``round(similarity * 100)``.  This is the value shown in the UI.
        document: Full document dict as returned by the search index, containing
            all supply profile attribute fields.
    """

    employee_id: str
    similarity_raw: float
    similarity: float = 0.0
    score_percent: int = 0
    rank: int = 0
    document: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Score normalization — SP2-002
# ---------------------------------------------------------------------------


def normalize_similarity_score(
    raw: float,
    *,
    raw_min: float = 0.0,
    raw_max: float = 1.0,
) -> tuple[float, int]:
    """Normalize a raw retrieval score to a canonical (similarity, score_percent) pair.

    Implements the normalization rules defined in
    ``docs/contracts/similarity-and-cache-contract.md`` (SP0-009).

    The general min-max formula covers all documented retrieval engine domains:

    * Azure AI Search cosine similarity ``[0.0, 1.0]`` — use defaults
      ``raw_min=0.0, raw_max=1.0``.
    * Raw cosine similarity ``[-1.0, 1.0]`` — pass ``raw_min=-1.0,
      raw_max=1.0``; the formula then reduces to ``(raw + 1) / 2``.

    Steps:

    1. Guard against NaN or a degenerate domain (``raw_min == raw_max``); both
       return ``(0.0, 0)``.
    2. Apply min-max normalization:
       ``similarity = (raw - raw_min) / (raw_max - raw_min)``
    3. Clamp ``similarity`` to ``[0.0, 1.0]`` so that out-of-range raw scores
       (including negative values) never produce negative percentages.
    4. Compute ``score_percent = round(similarity * 100)``.

    Args:
        raw: Raw similarity score from the retrieval engine.
        raw_min: Lower bound of the raw score domain (default 0.0).
        raw_max: Upper bound of the raw score domain (default 1.0).

    Returns:
        A tuple ``(similarity, score_percent)`` where ``similarity`` is a float
        in ``[0.0, 1.0]`` and ``score_percent`` is an integer in ``[0, 100]``.
    """
    if math.isnan(raw) or raw_min == raw_max:
        return 0.0, 0

    similarity = (raw - raw_min) / (raw_max - raw_min)
    similarity = max(0.0, min(1.0, similarity))
    score_percent = round(similarity * 100)
    return similarity, score_percent


# ---------------------------------------------------------------------------
# Strategy protocol — shared interface for dense, sparse, and hybrid (SP2-008)
# ---------------------------------------------------------------------------


@runtime_checkable
class RetrievalStrategy(Protocol):
    """Common interface for all retrieval strategy implementations.

    Implementations must be callable with these arguments and return a list of
    :class:`RetrievalCandidate` objects sorted by ``similarity_raw`` descending.

    Switching strategies requires only changing the ``RETRIEVAL_STRATEGY``
    environment variable (``dense`` | ``sparse`` | ``hybrid``) per NFR-010.
    """

    def retrieve(
        self,
        demand: "DemandRecord",
        openai_client: object,
        search_client: object,
        *,
        top_n: int = 50,
    ) -> list[RetrievalCandidate]:
        """Execute retrieval and return ranked candidates.

        Args:
            demand: Parsed and validated demand record.
            openai_client: Configured ``AzureOpenAI`` client.
            search_client: Configured Azure AI Search ``SearchClient``.
            top_n: Maximum number of raw candidates to return before
                downstream threshold/ranking steps.

        Returns:
            Candidates sorted by ``similarity_raw`` descending.
        """
        ...


# ---------------------------------------------------------------------------
# Demand embedding text builder
# ---------------------------------------------------------------------------


def build_demand_embedding_text(demand: "DemandRecord") -> str:
    """Construct a structured text representation of a demand record for embedding.

    The format mirrors the supply profile text used in SP1-003 / SP1-001 so
    both sides of the match are embedded in a comparable semantic space.

    Per ``docs/schemas/demand-schema.md``, the ``JD`` field (``job_description``)
    carries the richest semantic signal; structured fields provide explicit
    attribute anchors.

    Args:
        demand: A fully validated demand record (completeness ≥ 70%).

    Returns:
        A non-empty string suitable for passing to the embedding API.
    """
    parts: list[str] = []

    if demand.role_description:
        parts.append(f"Role: {demand.role_description}.")
    if demand.role_cluster:
        parts.append(f"Role Cluster: {demand.role_cluster}.")
    if demand.essential_skill:
        parts.append(f"Essential Skill: {demand.essential_skill}.")
    if demand.band:
        parts.append(f"Band: {demand.band}.")
    if demand.location:
        parts.append(f"Location: {demand.location}.")
    if demand.country:
        parts.append(f"Country: {demand.country}.")
    if demand.work_mode:
        parts.append(f"Work Mode: {demand.work_mode}.")
    if demand.job_description:
        parts.append(f"Job Description: {demand.job_description}.")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Dense retrieval strategy
# ---------------------------------------------------------------------------


class DenseRetrievalStrategy:
    """Retrieve supply profile candidates using dense (ANN/HNSW) vector search.

    The demand record is embedded with the same model used for supply profiles
    (``text-embedding-3-small`` per the ADR).  The resulting vector is submitted
    to Azure AI Search as a ``VectorizedQuery`` which uses approximate nearest-
    neighbour search over the ``content_vector`` field in the supply index.

    Raw similarity scores returned by Azure AI Search for cosine-similarity
    searches are in the range [0.0, 1.0].  They are stored as ``similarity_raw``
    on each :class:`RetrievalCandidate` and passed unchanged to the downstream
    normalisation step (SP2-002).
    """

    def retrieve(
        self,
        demand: "DemandRecord",
        openai_client: object,
        search_client: object,
        *,
        top_n: int = 50,
    ) -> list[RetrievalCandidate]:
        """Execute dense vector retrieval against the AI Search supply index.

        Args:
            demand: Validated demand record.
            openai_client: Configured ``AzureOpenAI`` client.
            search_client: Configured ``SearchClient`` pointing at the supply
                profile index.
            top_n: Number of candidates to request from the index (default 50,
                configurable via ``RETRIEVAL_TOP_N`` env var).

        Returns:
            Candidates sorted by ``similarity_raw`` descending.
        """
        # Lazy import: avoids circular imports with src.api.main at module load time.
        from azure.search.documents.models import VectorizedQuery  # noqa: PLC0415

        deployment = os.getenv(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"
        )
        vector_field = os.getenv("AZURE_SEARCH_VECTOR_FIELD", "content_vector")
        index_top_n = int(os.getenv("RETRIEVAL_TOP_N", str(top_n)))

        # Step 1: embed the demand record using the same model as supply profiles
        embedding_text = build_demand_embedding_text(demand)
        logger.debug(
            "dense_retrieval demand_id=%s embedding_text_len=%d",
            demand.demand_id,
            len(embedding_text),
        )

        response = openai_client.embeddings.create(
            input=[embedding_text],
            model=deployment,
        )
        query_vector: list[float] = response.data[0].embedding

        # Step 2: submit vector query to Azure AI Search
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=index_top_n,
            fields=vector_field,
        )

        search_results = search_client.search(
            search_text=None,  # pure vector query — no keyword text
            vector_queries=[vector_query],
            top=index_top_n,
        )

        # Step 3: collect and sort candidates
        candidates: list[RetrievalCandidate] = []
        for result in search_results:
            raw_score: float = result.get("@search.score", 0.0)
            employee_id: str = result.get("employee_id", result.get("id", ""))
            similarity, score_percent = normalize_similarity_score(raw_score)
            candidates.append(
                RetrievalCandidate(
                    employee_id=employee_id,
                    similarity_raw=raw_score,
                    similarity=similarity,
                    score_percent=score_percent,
                    document=dict(result),
                )
            )
            logger.debug(
                "dense_retrieval candidate employee_id=%s similarity_raw=%.4f score_percent=%d",
                employee_id,
                raw_score,
                score_percent,
            )

        candidates.sort(key=lambda c: c.similarity_raw, reverse=True)

        logger.info(
            "dense_retrieval demand_id=%s candidates_returned=%d top_n=%d",
            demand.demand_id,
            len(candidates),
            index_top_n,
        )
        return candidates


# ---------------------------------------------------------------------------
# Threshold enforcement — SP2-003
# ---------------------------------------------------------------------------

#: Minimum configurable threshold (inclusive) per FR-005.
_THRESHOLD_MIN = 70
#: Maximum configurable threshold (inclusive) per FR-005.
_THRESHOLD_MAX = 80


def _read_threshold() -> int:
    """Read and validate ``MATCH_SCORE_THRESHOLD`` from the environment.

    Returns:
        An integer threshold in [70, 80] (inclusive).  Defaults to 70 when the
        variable is absent or empty.

    Raises:
        ValueError: If the configured value cannot be parsed as an integer or
            lies outside the allowed [70, 80] range.
    """
    raw = os.getenv("MATCH_SCORE_THRESHOLD", "70").strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(
            f"MATCH_SCORE_THRESHOLD must be an integer, got '{raw}'"
        ) from exc

    if value < _THRESHOLD_MIN or value > _THRESHOLD_MAX:
        raise ValueError(
            f"MATCH_SCORE_THRESHOLD must be between {_THRESHOLD_MIN} and "
            f"{_THRESHOLD_MAX} (inclusive), got {value}"
        )
    return value


def apply_threshold(
    candidates: list[RetrievalCandidate],
    *,
    threshold: int | None = None,
) -> list[RetrievalCandidate]:
    """Filter out candidates whose ``score_percent`` falls below the threshold.

    Implements the 70% similarity floor defined in FR-005 and SP2-003.

    The threshold defaults to the value of the ``MATCH_SCORE_THRESHOLD``
    environment variable (default ``70``) which must be in the range [70, 80]
    inclusive.  Callers may pass an explicit *threshold* value to override the
    environment variable (useful in tests).

    Args:
        candidates: List of :class:`RetrievalCandidate` objects, typically the
            output of a retrieval strategy (may be unsorted).
        threshold: Optional explicit threshold in [0, 100].  When *None* the
            value is read from the ``MATCH_SCORE_THRESHOLD`` environment
            variable.

    Returns:
        A list containing only candidates whose ``score_percent`` is greater
        than or equal to *threshold*.  Returns an empty list when no candidates
        meet the threshold — this is not an error condition.

    Examples:
        >>> from src.matching.retriever import RetrievalCandidate, apply_threshold
        >>> c_high = RetrievalCandidate("EMP-A", 0.95, 0.95, 95)
        >>> c_low  = RetrievalCandidate("EMP-B", 0.60, 0.60, 60)
        >>> apply_threshold([c_high, c_low], threshold=70)
        [RetrievalCandidate(employee_id='EMP-A', ...)]
    """
    effective_threshold: int = threshold if threshold is not None else _read_threshold()

    passing = [c for c in candidates if c.score_percent >= effective_threshold]

    logger.debug(
        "apply_threshold threshold=%d candidates_in=%d candidates_out=%d",
        effective_threshold,
        len(candidates),
        len(passing),
    )
    return passing


# ---------------------------------------------------------------------------
# Ranked top-10 shortlist — SP2-004
# ---------------------------------------------------------------------------

#: Maximum shortlist size returned by :func:`rank_shortlist`.
TOP_SHORTLIST_SIZE: int = 10


def rank_shortlist(
    candidates: list[RetrievalCandidate],
    *,
    top_n: int = TOP_SHORTLIST_SIZE,
) -> list[RetrievalCandidate]:
    """Sort candidates by descending score and return a ranked top-N shortlist.

    Implements SP2-004.  The candidates passed in are typically the output of
    :func:`apply_threshold` (SP2-003) — i.e., all candidates already meet the
    similarity floor — but the function is safe to call on any list.

    Sorting is stable and deterministic:

    1. Primary key: ``score_percent`` descending (highest score = rank 1).
    2. Tie-break key: ``employee_id`` ascending (alphabetical).

    The returned list contains at most *top_n* items (default
    :data:`TOP_SHORTLIST_SIZE` = 10).  When fewer candidates are supplied all
    are returned.  An empty input produces an empty output — not an error.

    Each returned :class:`RetrievalCandidate` has its ``rank`` attribute set to
    its 1-based position in the shortlist (rank 1 = best match).

    Args:
        candidates: Candidate list to rank.  The list is not mutated; a new
            sorted slice is returned.
        top_n: Maximum number of results to return.  Defaults to
            :data:`TOP_SHORTLIST_SIZE` (10).

    Returns:
        A list of at most *top_n* :class:`RetrievalCandidate` objects sorted by
        ``score_percent`` descending and with ``rank`` set to 1-based position.
    """
    # Sort: score_percent descending; employee_id ascending for tie-breaking.
    sorted_candidates = sorted(
        candidates,
        key=lambda c: (-c.score_percent, c.employee_id),
    )

    shortlist = sorted_candidates[:top_n]

    for position, candidate in enumerate(shortlist, start=1):
        candidate.rank = position

    logger.debug(
        "rank_shortlist candidates_in=%d top_n=%d shortlist_size=%d",
        len(candidates),
        top_n,
        len(shortlist),
    )
    return shortlist


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------


def dense_retrieval(
    demand: "DemandRecord",
    openai_client: object,
    search_client: object,
    *,
    top_n: int = 50,
) -> list[RetrievalCandidate]:
    """Thin wrapper around :class:`DenseRetrievalStrategy` for convenience.

    Reads ``RETRIEVAL_TOP_N`` from the environment when ``top_n`` is not
    provided explicitly.

    Args:
        demand: Validated demand record.
        openai_client: Configured ``AzureOpenAI`` client.
        search_client: Configured ``SearchClient`` for the supply index.
        top_n: Maximum raw candidates to return (default 50).

    Returns:
        Candidates sorted by ``similarity_raw`` descending.
    """
    return DenseRetrievalStrategy().retrieve(
        demand,
        openai_client,
        search_client,
        top_n=top_n,
    )
