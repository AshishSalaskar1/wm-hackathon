"""JD (demand record) vectorization and indexing for the JD Index — SP2-006.

Serialises a demand record into a structured text representation using the same
embedding model as supply profiles (text-embedding-3-small per the ADR), then
upserts the resulting document into a dedicated Azure AI Search JD Index keyed
by demand_id.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------


@dataclass
class JDVectorizeResult:
    """Result of vectorizing and indexing a single JD (demand record).

    Attributes:
        demand_id: Demand identifier used as the JD Index document key.
        status: ``"indexed"`` when the document was upserted successfully,
            ``"failed"`` when the upsert failed.
        reason: Human-readable explanation when status is ``"failed"``.
    """

    demand_id: int | str
    status: Literal["indexed", "failed"]
    reason: str | None = None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def vectorize_and_index_jd(
    demand,
    openai_client,
    jd_search_client,
) -> JDVectorizeResult:
    """Vectorize a demand record and upsert it to the JD Index.

    Uses the same embedding model as supply profiles (``text-embedding-3-small``
    per ``docs/adr/2026-04-28-embedding-jd-index-retrieval-v01.md``).

    The JD Index document is keyed by ``str(demand_id)`` (Azure AI Search
    requires string document keys).  Re-vectorizing the same demand record
    with identical field values produces the same embedding text input and
    therefore the same vector from the embedding model (deterministic given a
    fixed model and input per SP2-006 AC).

    Args:
        demand: A demand record object with attribute access matching
            ``DemandRecord`` or ``DemandRecordInput``.  Optional fields may
            be ``None``; the embedding text builder omits null attributes.
        openai_client: Configured ``AzureOpenAI`` client.
        jd_search_client: Configured Azure AI Search ``SearchClient`` pointing
            at the JD Index (typically named via ``AZURE_JD_SEARCH_INDEX_NAME``).

    Returns:
        A :class:`JDVectorizeResult` with status ``"indexed"`` on success or
        ``"failed"`` on upsert failure.
    """
    # Lazy import: avoids potential circular-import issues; mirrors the pattern
    # used in src/ingestion/vectorizer.py and src/matching/retriever.py.
    from src.backend.matching.retriever import build_demand_embedding_text  # noqa: PLC0415

    deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

    # Step 1: build the embedding text — same format used at retrieval time so
    # demand and supply embeddings occupy the same semantic space (SP2-005).
    embedding_text = build_demand_embedding_text(demand)
    logger.debug(
        "jd_vectorize demand_id=%s embedding_text_len=%d",
        demand.demand_id,
        len(embedding_text),
    )

    # Step 2: call Azure OpenAI Embeddings API to produce the content vector.
    response = openai_client.embeddings.create(
        input=[embedding_text],
        model=deployment,
    )
    vector: list[float] = response.data[0].embedding

    # Step 3: build the JD Index document keyed by str(demand_id).
    document = _build_jd_document(demand, vector)

    # Step 4: upsert to the JD Index (merge_or_upload is idempotent — a second
    # call with the same key updates the existing document rather than
    # duplicating it, satisfying the re-vectorization idempotency requirement).
    index_results = jd_search_client.merge_or_upload_documents(documents=[document])
    upsert_result = index_results[0]

    if not upsert_result.succeeded:
        logger.warning(
            "jd_vectorize upsert_failed demand_id=%s",
            demand.demand_id,
        )
        return JDVectorizeResult(
            demand_id=demand.demand_id,
            status="failed",
            reason="JD Index upsert failed",
        )

    logger.info("jd_vectorize indexed demand_id=%s", demand.demand_id)
    return JDVectorizeResult(demand_id=demand.demand_id, status="indexed")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_jd_document(demand, vector: list[float]) -> dict:
    """Build the JD Index document dict from a demand record and its embedding.

    All optional demand fields are stored as ``None`` when absent so the
    document schema remains consistent across sparse and fully populated
    records.

    Args:
        demand: Demand record object with attribute access.
        vector: Embedding vector produced by Azure OpenAI.

    Returns:
        Dict suitable for ``SearchClient.merge_or_upload_documents``.
    """
    return {
        # Azure AI Search requires the document key to be a string.
        "id": str(demand.demand_id),
        "demand_id": demand.demand_id,
        "customer_name": _str_or_none(demand, "customer_name"),
        "essential_skill": _str_or_none(demand, "essential_skill"),
        "location": _str_or_none(demand, "location"),
        "country": _str_or_none(demand, "country"),
        "created_on": _date_iso_or_none(demand, "created_on"),
        "start_date": _date_iso_or_none(demand, "start_date"),
        "end_date": _date_iso_or_none(demand, "end_date"),
        "role_description": _str_or_none(demand, "role_description"),
        "work_mode": _str_or_none(demand, "work_mode"),
        "band": _str_or_none(demand, "band"),
        "open_positions": getattr(demand, "open_positions", None),
        "job_description": _str_or_none(demand, "job_description"),
        "role_cluster": _str_or_none(demand, "role_cluster"),
        "content_vector": vector,
    }


def _str_or_none(obj, attr: str) -> str | None:
    """Return ``str(getattr(obj, attr))`` or ``None`` when the attribute is absent or None."""
    val = getattr(obj, attr, None)
    return str(val) if val is not None else None


def _date_iso_or_none(obj, attr: str) -> str | None:
    """Return the ISO-8601 string of a date attribute or ``None`` when absent."""
    val = getattr(obj, attr, None)
    return val.isoformat() if val is not None else None
