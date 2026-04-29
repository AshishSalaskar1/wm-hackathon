"""Intelligent Demand-Supply Matching — Backend API."""

import logging
import os
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Annotated, Literal

logger = logging.getLogger(__name__)

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from openai import AzureOpenAI
from pydantic import BaseModel, Field

from src.backend.indexing import JDVectorizeResult, vectorize_and_index_jd
from src.backend.ingestion import (
    DemandRecordInput,
    IncompleteDemandError,
    InsufficientDataError,
    validate_demand_completeness,
    vectorize_and_index,
)
from src.backend.matching.retriever import apply_threshold, dense_retrieval, rank_shortlist
from src.backend.matching.result_store import StoredMatchResult, get_result_store

# ---------------------------------------------------------------------------
# Auth configuration
# ---------------------------------------------------------------------------

_AUTH_BYPASS_DEV: bool = os.getenv("AUTH_BYPASS_DEV", "true").lower() == "true"
_bearer = HTTPBearer(auto_error=False)


async def _verify_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str:
    """Validate Azure AD bearer token.

    When AUTH_BYPASS_DEV=true (default in dev), validation is skipped so all
    feature teams can iterate without Azure AD wiring.  Full token validation
    is implemented in SP4-005.
    """
    if _AUTH_BYPASS_DEV:
        return "dev-bypass"
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # TODO SP4-005: validate Azure AD token claims and extract user identity.
    return credentials.credentials


CurrentUser = Annotated[str, Depends(_verify_token)]

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class DemandRecord(BaseModel):
    """Open talent demand (maps to the Demand OIR Data Excel sheet)."""

    demand_id: int = Field(..., description="Unique Service Request identifier (SR_ID)")
    customer_name: str = Field(..., description="Business unit / customer name")
    essential_skill: str = Field(..., description="Primary required skill")
    location: str = Field(..., description="City where resource is required (UPPER case)")
    country: str = Field(..., description="Country where resource is required")
    created_on: date = Field(..., description="Date the service request was raised")
    start_date: date = Field(..., description="Date by which resource is needed")
    end_date: date = Field(..., description="Expected end date of engagement")
    role_description: str = Field(..., description="Short role label")
    work_mode: str = Field(..., description="ONSITE or OFFSHORE")
    band: str = Field(..., description="Required experience band (e.g. GROUP B2)")
    open_positions: int = Field(..., ge=1, description="Number of open headcount positions")
    job_description: str = Field(..., description="Full free-text job description")
    role_cluster: str = Field(..., description="Wipro role cluster name")


class SupplyProfile(BaseModel):
    """Available employee profile (maps to the Employee Data Excel sheet)."""

    employee_id: str = Field(..., description="Anonymized employee identifier")
    employee_name: str = Field(..., description="Anonymized display name")
    band: str = Field(..., description="Experience band (e.g. GROUP D1)")
    availability_from: date = Field(..., description="Date employee became available")
    ageing_bucket: str = Field(..., description="Availability ageing bucket")
    work_mode: str = Field(..., description="ONSITE or OFFSHORE")
    location: str = Field(..., description="City of posting (UPPER case)")
    experience: str = Field(..., description="Total experience string (e.g. '8Years 3Months')")
    role_name: str | None = Field(None, description="Designation / role (nullable)")
    country: str = Field(..., description="Country of posting")
    skills_iaspire: str | None = Field(
        None, description="Skills from iAspire with proficiency levels (primary matching signal)"
    )
    certified_skills: str | None = Field(None, description="Certified skills")
    trained_skills: str | None = Field(None, description="Trained skills")
    recent_skills: str | None = Field(None, description="Recently used skills")
    language_skills: str | None = Field(None, description="Language skills")
    role_cluster: str | None = Field(None, description="Role cluster")


class MatchResult(BaseModel):
    """Single ranked supply profile returned for a demand."""

    rank: int = Field(..., ge=1, le=10, description="Match rank (1 = best fit)")
    employee_id: str = Field(..., description="Anonymized employee identifier")
    employee_name: str = Field(..., description="Anonymized display name")
    similarity_score: int = Field(..., ge=0, le=100, description="Similarity score 0–100")
    band: str = Field(..., description="Experience band")
    location: str = Field(..., description="City of posting")
    experience: str = Field(..., description="Total experience string")
    role_name: str | None = Field(None, description="Designation / role")
    skills_iaspire: str | None = Field(None, description="Primary skills")
    certified_skills: str | None = Field(None, description="Certified skills")
    role_cluster: str | None = Field(None, description="Role cluster")
    work_mode: str = Field(..., description="ONSITE or OFFSHORE")
    below_threshold: bool = Field(
        False, description="True when score is below the 70% threshold (pagination pages 2+)"
    )


class MatchResultsResponse(BaseModel):
    """Paginated match results for a demand."""

    demand_id: int = Field(..., description="Demand identifier")
    status: str = Field(..., description="READY | MATCHING_IN_PROGRESS | NO_RESULTS")
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    has_more: bool = Field(..., description="True when additional pages are available")
    results: list[MatchResult] = Field(..., description="Ranked match results for this page")


class ProfileEventType(StrEnum):
    """Supply profile change event types."""

    ADDED = "profile.added"
    UPDATED = "profile.updated"
    DELETED = "profile.deleted"


class ProfileEventPayload(BaseModel):
    """Event payload for a supply profile change (add / update / delete)."""

    event_type: ProfileEventType = Field(..., description="Type of profile change event")
    employee_id: str = Field(..., description="Anonymized employee identifier")
    blob_url: str | None = Field(
        None, description="Blob Storage URL of the updated file (null for delete events)"
    )
    correlation_id: str | None = Field(
        None, description="Optional correlation ID for distributed tracing"
    )


class JDEventType(StrEnum):
    """Job description (demand) change event types."""

    ADDED = "jd.added"
    MODIFIED = "jd.modified"
    DELETED = "jd.deleted"


class JDEventPayload(BaseModel):
    """Event payload for a JD (demand) change (add / modify / delete)."""

    event_type: JDEventType = Field(..., description="Type of JD change event")
    demand_id: int = Field(..., description="Demand identifier (SR_ID)")
    blob_url: str | None = Field(
        None, description="Blob Storage URL of the updated file (null for delete events)"
    )
    correlation_id: str | None = Field(
        None, description="Optional correlation ID for distributed tracing"
    )


class EventAck(BaseModel):
    """Acknowledgement returned for accepted event payloads."""

    accepted: bool = Field(True, description="Always true for 202 responses")
    event_type: str = Field(..., description="Echoed event type from the payload")
    message: str = Field(..., description="Human-readable status message")


class VectorizeRequest(BaseModel):
    """Request body for POST /supply/vectorize."""

    profiles: list[SupplyProfile] = Field(
        ..., min_length=1, description="Profiles to vectorize and index"
    )


class ProfileVectorizeResult(BaseModel):
    """Per-profile result from the vectorize endpoint."""

    employee_id: str
    status: Literal["indexed", "skipped", "failed"]
    reason: str | None = None


class VectorizeResponse(BaseModel):
    """Aggregate response from POST /supply/vectorize."""

    total: int = Field(..., ge=0)
    indexed: int = Field(..., ge=0)
    skipped: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)
    results: list[ProfileVectorizeResult]


# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

_MOCK_DEMANDS: list[DemandRecord] = [
    DemandRecord(
        demand_id=1,
        customer_name="Customer2",
        essential_skill=".NET",
        location="HYDERABAD",
        country="INDIA",
        created_on=date(2026, 4, 17),
        start_date=date(2026, 4, 30),
        end_date=date(2026, 5, 25),
        role_description="Developer L3",
        work_mode="OFFSHORE",
        band="GROUP B2",
        open_positions=1,
        job_description=(
            "Looking for a Developer L3 with 4+ years of .NET experience on MSPP projects. "
            "Responsibilities include design, development, and delivery of enterprise .NET applications."
        ),
        role_cluster="DEVELOPER L3",
    ),
    DemandRecord(
        demand_id=2,
        customer_name="Customer5",
        essential_skill="Python",
        location="BANGALORE",
        country="INDIA",
        created_on=date(2026, 4, 18),
        start_date=date(2026, 5, 1),
        end_date=date(2026, 6, 30),
        role_description="Data Engineer L2",
        work_mode="OFFSHORE",
        band="GROUP C1",
        open_positions=2,
        job_description=(
            "Seeking a Data Engineer L2 proficient in Python, Azure Data Factory, and SQL. "
            "Experience with Spark, Databricks, and cloud-native data pipelines preferred."
        ),
        role_cluster="DATA ENGINEER L2",
    ),
    DemandRecord(
        demand_id=3,
        customer_name="Customer1",
        essential_skill="Java",
        location="PUNE",
        country="INDIA",
        created_on=date(2026, 4, 20),
        start_date=date(2026, 5, 5),
        end_date=date(2026, 7, 4),
        role_description="Project Manager L2",
        work_mode="ONSITE",
        band="GROUP B1",
        open_positions=1,
        job_description=(
            "Project Manager L2 for a Java-based enterprise delivery project. "
            "PMP certified preferred; experience managing cross-functional delivery teams."
        ),
        role_cluster="PROJECT MANAGER L2",
    ),
]

_MOCK_SUPPLY: list[SupplyProfile] = [
    SupplyProfile(
        employee_id="EMP-00001",
        employee_name="Employee1",
        band="GROUP B2",
        availability_from=date(2026, 1, 2),
        ageing_bucket="31-60 DAYS",
        work_mode="OFFSHORE",
        location="HYDERABAD",
        experience="8Years 3Months",
        role_name="Senior .NET Developer",
        country="INDIA",
        skills_iaspire=".NET(L4), C#(L4), Azure(L3), SQL(L3)",
        certified_skills="Microsoft Certified: Azure Developer Associate(L3)",
        trained_skills=None,
        recent_skills=".NET, Azure",
        language_skills="English, Telugu",
        role_cluster="DEVELOPER L3",
    ),
    SupplyProfile(
        employee_id="EMP-00002",
        employee_name="Employee2",
        band="GROUP C1",
        availability_from=date(2026, 2, 15),
        ageing_bucket="31-60 DAYS",
        work_mode="OFFSHORE",
        location="BANGALORE",
        experience="5Years 6Months",
        role_name="Data Engineer",
        country="INDIA",
        skills_iaspire="Python(L4), Azure Data Factory(L3), SQL(L4), Spark(L3)",
        certified_skills=None,
        trained_skills="Databricks(L2)",
        recent_skills="Python, SQL",
        language_skills="English, Hindi",
        role_cluster="DATA ENGINEER L2",
    ),
    SupplyProfile(
        employee_id="EMP-00003",
        employee_name="Employee3",
        band="GROUP B2",
        availability_from=date(2026, 3, 1),
        ageing_bucket="61-90 DAYS",
        work_mode="OFFSHORE",
        location="MUMBAI",
        experience="9Years 0Months",
        role_name="Java Developer",
        country="INDIA",
        skills_iaspire="Java(L4), Spring Boot(L4), Microservices(L3), AWS(L2)",
        certified_skills="AWS Certified Developer(L3)",
        trained_skills=None,
        recent_skills="Java, Spring Boot",
        language_skills="English, Hindi, Marathi",
        role_cluster="DEVELOPER L3",
    ),
]

# Page 1 results: candidates at or above the 70% similarity threshold.
_MOCK_MATCHES: dict[int, list[MatchResult]] = {
    1: [
        MatchResult(
            rank=1,
            employee_id="EMP-00001",
            employee_name="Employee1",
            similarity_score=92,
            band="GROUP B2",
            location="HYDERABAD",
            experience="8Years 3Months",
            role_name="Senior .NET Developer",
            skills_iaspire=".NET(L4), C#(L4), Azure(L3), SQL(L3)",
            certified_skills="Microsoft Certified: Azure Developer Associate(L3)",
            role_cluster="DEVELOPER L3",
            work_mode="OFFSHORE",
        ),
        MatchResult(
            rank=2,
            employee_id="EMP-00003",
            employee_name="Employee3",
            similarity_score=75,
            band="GROUP B2",
            location="MUMBAI",
            experience="9Years 0Months",
            role_name="Java Developer",
            skills_iaspire="Java(L4), Spring Boot(L4), Microservices(L3), AWS(L2)",
            certified_skills="AWS Certified Developer(L3)",
            role_cluster="DEVELOPER L3",
            work_mode="OFFSHORE",
        ),
    ],
    2: [
        MatchResult(
            rank=1,
            employee_id="EMP-00002",
            employee_name="Employee2",
            similarity_score=88,
            band="GROUP C1",
            location="BANGALORE",
            experience="5Years 6Months",
            role_name="Data Engineer",
            skills_iaspire="Python(L4), Azure Data Factory(L3), SQL(L4), Spark(L3)",
            certified_skills=None,
            role_cluster="DATA ENGINEER L2",
            work_mode="OFFSHORE",
        ),
    ],
    3: [],
}

# Page 2+ results: candidates below the 70% threshold, flagged accordingly.
_MOCK_MATCHES_PAGE2: dict[int, list[MatchResult]] = {
    1: [
        MatchResult(
            rank=3,
            employee_id="EMP-00004",
            employee_name="Employee4",
            similarity_score=62,
            band="GROUP C1",
            location="CHENNAI",
            experience="4Years 2Months",
            role_name="Associate .NET Developer",
            skills_iaspire=".NET(L2), C#(L2), SQL(L2)",
            certified_skills=None,
            role_cluster="DEVELOPER L2",
            work_mode="OFFSHORE",
            below_threshold=True,
        ),
        MatchResult(
            rank=4,
            employee_id="EMP-00005",
            employee_name="Employee5",
            similarity_score=55,
            band="GROUP D1",
            location="HYDERABAD",
            experience="2Years 0Months",
            role_name=None,
            skills_iaspire="C#(L1), SQL(L1)",
            certified_skills=None,
            role_cluster=None,
            work_mode="OFFSHORE",
            below_threshold=True,
        ),
    ],
    2: [
        MatchResult(
            rank=2,
            employee_id="EMP-00006",
            employee_name="Employee6",
            similarity_score=60,
            band="GROUP C2",
            location="PUNE",
            experience="3Years 5Months",
            role_name="Junior Data Engineer",
            skills_iaspire="Python(L2), SQL(L3)",
            certified_skills=None,
            role_cluster="DATA ENGINEER L1",
            work_mode="OFFSHORE",
            below_threshold=True,
        ),
    ],
    3: [],
}

# ---------------------------------------------------------------------------
# Demand lookup index (O(1) by demand_id)
# ---------------------------------------------------------------------------

_MOCK_DEMANDS_BY_ID: dict[int, DemandRecord] = {d.demand_id: d for d in _MOCK_DEMANDS}


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _demand_record_to_input(record: DemandRecord) -> DemandRecordInput:
    """Convert an API ``DemandRecord`` to a ``DemandRecordInput`` for completeness validation."""
    return DemandRecordInput(**record.model_dump())


def _create_matching_clients() -> tuple[object, object, object] | None:
    """Create Azure OpenAI, supply search, and JD search clients.

    Returns ``None`` when ``AZURE_OPENAI_ENDPOINT`` or ``AZURE_SEARCH_ENDPOINT``
    environment variables are not set (dev mode with no Azure services).
    """
    openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    if not openai_endpoint or not search_endpoint:
        return None

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    openai_client = AzureOpenAI(
        azure_endpoint=openai_endpoint,
        azure_ad_token_provider=token_provider,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    )
    supply_search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=os.getenv("AZURE_SEARCH_SUPPLY_INDEX", "supply-profiles"),
        credential=DefaultAzureCredential(),
    )
    jd_search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=os.getenv("AZURE_JD_SEARCH_INDEX_NAME", "jd-index"),
        credential=DefaultAzureCredential(),
    )
    return openai_client, supply_search_client, jd_search_client


def _stored_to_match_result(stored: StoredMatchResult) -> MatchResult:
    """Convert a :class:`StoredMatchResult` to the API-layer :class:`MatchResult` model."""
    return MatchResult(
        rank=stored.rank,
        employee_id=stored.employee_id,
        employee_name=stored.employee_name,
        similarity_score=stored.score_percent,
        band=stored.band,
        location=stored.location,
        experience=stored.experience,
        role_name=stored.role_name,
        skills_iaspire=stored.skills_iaspire,
        certified_skills=stored.certified_skills,
        role_cluster=stored.role_cluster,
        work_mode=stored.work_mode,
        below_threshold=stored.below_threshold,
    )


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Intelligent Demand-Supply Matching API",
    description="Matches open talent demands against available supply profiles using Azure AI Search.",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/demands", response_model=list[DemandRecord], tags=["demands"])
async def list_demands(_user: CurrentUser) -> list[DemandRecord]:
    """Return all open demand records."""
    return _MOCK_DEMANDS


@app.post(
    "/demands",
    response_model=DemandRecord,
    status_code=status.HTTP_201_CREATED,
    tags=["demands"],
)
async def create_demand(demand: DemandRecord, _user: CurrentUser) -> DemandRecord:
    """Accept a new demand record (stub — echoes the submitted record back)."""
    return demand


@app.get(
    "/demands/{demand_id}/matches",
    response_model=MatchResultsResponse,
    tags=["demands"],
)
async def get_demand_matches(
    demand_id: int,
    _user: CurrentUser,
    page: int = 1,
) -> MatchResultsResponse:
    """Return ranked match results for the given demand.

    Serves from the Search Result DB when results have been pre-computed by
    the JD event pipeline (SP2-007).  Falls back to mock data when the result
    store has no entry for the demand ID.

    Returns 404 when the demand ID is not found in either source.
    Returns NO_RESULTS status when the demand exists but no candidates met
    the 70% similarity threshold.
    """
    result_store = get_result_store()

    # Prefer real matching results from the Search Result DB.
    if result_store.demand_exists(demand_id):
        stored = result_store.get_results(demand_id)
        if page == 1:
            real_results = [_stored_to_match_result(r) for r in (stored or [])]
            match_status = "READY" if real_results else "NO_RESULTS"
            # Pagination (SP3-006) deferred — page 2 not supported here yet.
            has_more = False
        else:
            real_results = []
            match_status = "NO_RESULTS"
            has_more = False
        return MatchResultsResponse(
            demand_id=demand_id,
            status=match_status,
            page=page,
            has_more=has_more,
            results=real_results,
        )

    # Fall back to mock data for demands not yet processed by the pipeline.
    if demand_id not in _MOCK_MATCHES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demand {demand_id} not found",
        )
    if page == 1:
        results = _MOCK_MATCHES[demand_id]
        match_status = "READY" if results else "NO_RESULTS"
        has_more = bool(_MOCK_MATCHES_PAGE2.get(demand_id, []))
    else:
        results = _MOCK_MATCHES_PAGE2.get(demand_id, [])
        match_status = "READY" if results else "NO_RESULTS"
        has_more = False  # Mock data only has two pages
    return MatchResultsResponse(
        demand_id=demand_id,
        status=match_status,
        page=page,
        has_more=has_more,
        results=results,
    )


@app.get("/supply", response_model=list[SupplyProfile], tags=["supply"])
async def list_supply(_user: CurrentUser) -> list[SupplyProfile]:
    """Return available supply profiles (mock data)."""
    return _MOCK_SUPPLY


@app.post(
    "/events/profile",
    response_model=EventAck,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["events"],
)
async def receive_profile_event(
    payload: ProfileEventPayload,
    _user: CurrentUser,
) -> EventAck:
    """Accept a supply profile change event (add / update / delete).

    Logs the event and returns 202 Accepted.  Real indexing logic is wired
    in SP1-004, SP1-005, and SP1-006.
    """
    logger.info(
        "profile_event received event_type=%s employee_id=%s correlation_id=%s",
        payload.event_type,
        payload.employee_id,
        payload.correlation_id,
    )
    return EventAck(
        event_type=payload.event_type,
        message=f"Profile event '{payload.event_type}' for '{payload.employee_id}' accepted.",
    )


@app.post(
    "/events/jd",
    response_model=EventAck,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["events"],
)
async def receive_jd_event(
    payload: JDEventPayload,
    _user: CurrentUser,
) -> EventAck:
    """Accept a JD (demand) change event (add / modify / delete).

    For ``jd.added`` events: runs the full JD pipeline synchronously —
    completeness validation → JD vectorization → dense retrieval →
    threshold → top-10 ranking → result persistence — and returns 202
    only after results are stored in the Search Result DB (SP2-007).

    For ``jd.modified`` and ``jd.deleted`` events: logged and accepted
    (pipeline wiring in SP3-001 and SP3-002).

    Returns:
        202 Accepted with an :class:`EventAck` payload.

    Raises:
        HTTPException 404: Demand ID not found.
        HTTPException 422: Demand fails the 70% completeness check.
        HTTPException 503: Azure services are not configured.
        HTTPException 500: JD vectorization or retrieval failed.
    """
    logger.info(
        "jd_event received event_type=%s demand_id=%s correlation_id=%s",
        payload.event_type,
        payload.demand_id,
        payload.correlation_id,
    )

    if payload.event_type == JDEventType.ADDED:
        # Step 1: look up the demand record.
        demand = _MOCK_DEMANDS_BY_ID.get(payload.demand_id)
        if demand is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Demand {payload.demand_id} not found",
            )

        # Step 2: validate completeness ≥ 70% (FR-003 / SP1-007).
        demand_input = _demand_record_to_input(demand)
        try:
            validate_demand_completeness(demand_input)
        except IncompleteDemandError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        # Require Azure services for the matching pipeline.
        clients = _create_matching_clients()
        if clients is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Azure OpenAI and Azure AI Search endpoints must be configured. "
                    "Set AZURE_OPENAI_ENDPOINT and AZURE_SEARCH_ENDPOINT environment variables."
                ),
            )
        openai_client, supply_search_client, jd_search_client = clients

        # Step 3: vectorize JD and upsert to the JD Index (SP2-006).
        jd_result = vectorize_and_index_jd(demand, openai_client, jd_search_client)
        if jd_result.status == "failed":
            logger.error(
                "jd_added vectorize_failed demand_id=%s reason=%s",
                demand.demand_id,
                jd_result.reason,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"JD vectorization failed: {jd_result.reason}",
            )

        # Step 4: dense retrieval against the full supply index (SP2-001).
        candidates = dense_retrieval(demand, openai_client, supply_search_client)

        # Step 5: apply 70% similarity threshold (SP2-003).
        passing = apply_threshold(candidates)

        # Step 6: rank and truncate to top-10 shortlist (SP2-004).
        shortlist = rank_shortlist(passing)

        # Step 7: persist results to the Search Result DB (SP0-009).
        now = datetime.now(timezone.utc).isoformat()
        strategy = os.getenv("RETRIEVAL_STRATEGY", "dense")
        stored_results = [
            StoredMatchResult(
                demand_id=demand.demand_id,
                employee_id=c.employee_id,
                similarity_raw=c.similarity_raw,
                similarity=c.similarity,
                score_percent=c.score_percent,
                rank=c.rank,
                retrieval_strategy=strategy,
                timestamp=now,
                employee_name=c.document.get("employee_name", ""),
                band=c.document.get("band", ""),
                location=c.document.get("location", ""),
                experience=c.document.get("experience", ""),
                work_mode=c.document.get("work_mode", ""),
                role_name=c.document.get("role_name"),
                skills_iaspire=c.document.get("skills_iaspire"),
                certified_skills=c.document.get("certified_skills"),
                role_cluster=c.document.get("role_cluster"),
            )
            for c in shortlist
        ]
        get_result_store().upsert_results(demand.demand_id, stored_results)

        logger.info(
            "jd_added pipeline_complete demand_id=%s results_stored=%d",
            demand.demand_id,
            len(stored_results),
        )
        return EventAck(
            event_type=payload.event_type,
            message=(
                f"JD event 'jd.added' for demand '{payload.demand_id}' processed. "
                f"{len(stored_results)} match result(s) stored."
            ),
        )

    # jd.modified → SP3-001; jd.deleted → SP3-002.
    return EventAck(
        event_type=payload.event_type,
        message=f"JD event '{payload.event_type}' for demand '{payload.demand_id}' accepted.",
    )


@app.post(
    "/supply/vectorize",
    response_model=VectorizeResponse,
    tags=["supply"],
)
async def vectorize_supply_profiles(
    request: VectorizeRequest,
    _user: CurrentUser,
) -> VectorizeResponse:
    """Vectorize a batch of supply profiles and upsert them into Azure AI Search.

    Returns per-profile indexed/skipped/failed status.
    Returns 503 when Azure OpenAI or AI Search endpoints are not configured.
    """
    openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")

    if not openai_endpoint or not search_endpoint:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Azure OpenAI and Azure AI Search endpoints must be configured. "
                "Set AZURE_OPENAI_ENDPOINT and AZURE_SEARCH_ENDPOINT environment variables."
            ),
        )

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )
    openai_client = AzureOpenAI(
        azure_endpoint=openai_endpoint,
        azure_ad_token_provider=token_provider,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    )
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=os.getenv("AZURE_SEARCH_SUPPLY_INDEX", "supply-profiles"),
        credential=DefaultAzureCredential(),
    )

    results = vectorize_and_index(request.profiles, openai_client, search_client)

    return VectorizeResponse(
        total=len(results),
        indexed=sum(1 for r in results if r.status == "indexed"),
        skipped=sum(1 for r in results if r.status == "skipped"),
        failed=sum(1 for r in results if r.status == "failed"),
        results=results,
    )
