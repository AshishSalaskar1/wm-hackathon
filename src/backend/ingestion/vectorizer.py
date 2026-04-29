"""Supply profile vectorization utilities for Azure OpenAI and Azure AI Search."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.backend.api.main import SupplyProfile


class InsufficientDataError(ValueError):
    """Raised when a supply profile has no usable skill fields for embedding."""

    def __init__(self, employee_id: str, message: str) -> None:
        self.employee_id = employee_id
        super().__init__(message)


def build_embedding_text(profile: "SupplyProfile") -> str:
    """Construct a skill-priority embedding text string from a supply profile.

    Primary fields: skills_iaspire, certified_skills.
    Fallback fields: trained_skills, recent_skills.
    Raises InsufficientDataError when all four skill fields are null.
    """
    parts: list[str] = []

    # Primary skill fields
    if profile.skills_iaspire:
        parts.append(f"Skills: {profile.skills_iaspire}.")
    if profile.certified_skills:
        parts.append(f"Certified: {profile.certified_skills}.")

    # Fallback when both primary skill fields are null
    if not profile.skills_iaspire and not profile.certified_skills:
        if profile.trained_skills:
            parts.append(f"Trained Skills: {profile.trained_skills}.")
        elif profile.recent_skills:
            parts.append(f"Recent Skills: {profile.recent_skills}.")
        else:
            raise InsufficientDataError(
                employee_id=profile.employee_id,
                message="All skill fields are null; profile cannot be embedded.",
            )

    # Non-skill fields — omit when null or empty
    if profile.role_name:
        parts.append(f"Role: {profile.role_name}.")
    if profile.role_cluster:
        parts.append(f"Role Cluster: {profile.role_cluster}.")
    parts.append(f"Band: {profile.band}.")
    parts.append(f"Location: {profile.location}.")
    parts.append(f"Country: {profile.country}.")
    parts.append(f"Experience: {profile.experience}.")
    parts.append(f"Work Mode: {profile.work_mode}.")

    return " ".join(parts)


def vectorize_and_index(
    profiles: list,
    openai_client,
    search_client,
) -> list:
    """Vectorize supply profiles via Azure OpenAI and upsert them to Azure AI Search.

    Returns a list of ProfileVectorizeResult in the same order as the input profiles.
    """
    # Lazy import: deferred until first call to avoid circular import with src.api.main
    from src.backend.api.main import ProfileVectorizeResult  # noqa: PLC0415

    _BATCH_SIZE = 100
    deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")

    # Step 1: build embedding texts; mark skipped profiles
    results: list[ProfileVectorizeResult] = []
    eligible_profiles = []
    eligible_texts = []

    for profile in profiles:
        try:
            text = build_embedding_text(profile)
            eligible_profiles.append(profile)
            eligible_texts.append(text)
            results.append(ProfileVectorizeResult(employee_id=profile.employee_id, status="indexed"))
        except InsufficientDataError as exc:
            results.append(
                ProfileVectorizeResult(
                    employee_id=profile.employee_id,
                    status="skipped",
                    reason=str(exc),
                )
            )

    # Step 2: batch call Azure OpenAI embeddings
    vectors: dict[str, list[float]] = {}
    for i in range(0, len(eligible_texts), _BATCH_SIZE):
        batch_texts = eligible_texts[i : i + _BATCH_SIZE]
        batch_profiles = eligible_profiles[i : i + _BATCH_SIZE]
        response = openai_client.embeddings.create(input=batch_texts, model=deployment)
        for j, item in enumerate(response.data):
            vectors[batch_profiles[j].employee_id] = item.embedding

    # Step 3: upsert to AI Search
    if eligible_profiles:
        documents = [
            {
                "id": p.employee_id,
                "employee_id": p.employee_id,
                "employee_name": p.employee_name,
                "band": p.band,
                "availability_from": p.availability_from.isoformat(),
                "ageing_bucket": p.ageing_bucket,
                "work_mode": p.work_mode,
                "location": p.location,
                "experience": p.experience,
                "role_name": p.role_name,
                "country": p.country,
                "skills_iaspire": p.skills_iaspire,
                "certified_skills": p.certified_skills,
                "trained_skills": p.trained_skills,
                "recent_skills": p.recent_skills,
                "language_skills": p.language_skills,
                "role_cluster": p.role_cluster,
                "content_vector": vectors[p.employee_id],
            }
            for p in eligible_profiles
        ]
        index_results = search_client.merge_or_upload_documents(documents=documents)

        # Step 4: check per-document AI Search result
        failed_ids = {r.key for r in index_results if not r.succeeded}
        for r in results:
            if r.employee_id in failed_ids:
                r.status = "failed"
                r.reason = "AI Search upsert failed"

    return results
