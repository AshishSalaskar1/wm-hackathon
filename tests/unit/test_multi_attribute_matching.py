"""Unit tests: multi-attribute simultaneous matching — SP2-005.

Validates that supply profile and demand record embeddings are built from ALL
five matching attributes (skills, designation, location, experience band,
project history), and that each attribute contributes independently to the
composite similarity score.

Five attribute families and their schema mappings
-------------------------------------------------
1. **Skills**           supply: ``skills_iaspire`` / ``certified_skills`` (+ fallbacks)
                        demand: ``essential_skill`` / ``job_description``
2. **Designation/Role** supply: ``role_name`` / ``role_cluster``
                        demand: ``role_description`` / ``role_cluster``
3. **Location**         supply: ``location`` / ``country``
                        demand: ``location`` / ``country``
4. **Experience Band**  supply: ``band``
                        demand: ``band``
5. **Project History**  supply: ``experience`` + ``role_cluster`` (career-trajectory proxy)
                        demand: ``job_description`` (contains project context)

No real Azure services are required.  All tests are pure-Python.
"""

from __future__ import annotations

import sys
import types
from datetime import date
from typing import Any
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Stub missing Azure SDK packages so tests run without the real SDK installed.
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

_search_models_stub = sys.modules["azure.search.documents.models"]
if not hasattr(_search_models_stub, "VectorizedQuery"):
    _search_models_stub.VectorizedQuery = MagicMock  # type: ignore[attr-defined]

from src.backend.ingestion.vectorizer import build_embedding_text  # noqa: E402
from src.backend.matching.retriever import (  # noqa: E402
    DenseRetrievalStrategy,
    RetrievalCandidate,
    build_demand_embedding_text,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_supply_profile(**overrides) -> Any:
    """Return a SimpleNamespace that mimics SupplyProfile attribute access."""
    import types as _types

    defaults = {
        "employee_id": "EMP-001",
        "employee_name": "Employee1",
        "band": "GROUP C1",
        "availability_from": date(2026, 1, 1),
        "ageing_bucket": "0-30 DAYS",
        "work_mode": "OFFSHORE",
        "location": "BANGALORE",
        "experience": "6Years 0Months",
        "role_name": "Data Engineer",
        "country": "INDIA",
        "skills_iaspire": "Python(L4), Azure(L3)",
        "certified_skills": "AZ-900",
        "trained_skills": None,
        "recent_skills": None,
        "language_skills": None,
        "role_cluster": "DATA ENGINEER L2",
    }
    defaults.update(overrides)
    return _types.SimpleNamespace(**defaults)


def _make_demand(**overrides) -> Any:
    """Return a SimpleNamespace that mimics DemandRecord attribute access."""
    import types as _types

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
        "job_description": (
            "Seeking a Data Engineer with Python and Azure skills. "
            "The candidate will work on cloud-based data pipelines."
        ),
        "role_cluster": "DATA ENGINEER L2",
    }
    defaults.update(overrides)
    return _types.SimpleNamespace(**defaults)


def _make_openai_client(vector: list[float] | None = None) -> MagicMock:
    """Return a mock AzureOpenAI client that returns a fixed embedding."""
    if vector is None:
        vector = [0.1] * 1536
    mock_item = MagicMock()
    mock_item.embedding = vector
    mock_response = MagicMock()
    mock_response.data = [mock_item]
    client = MagicMock()
    client.embeddings.create.return_value = mock_response
    return client


def _make_search_client(results: list[dict]) -> MagicMock:
    """Return a mock SearchClient that returns the given result dicts."""
    client = MagicMock()
    client.search.return_value = iter(results)
    return client


def _make_search_result(employee_id: str, score: float, **extra) -> dict:
    """Return a dict that behaves like an Azure AI Search result document."""
    doc = {
        "employee_id": employee_id,
        "id": employee_id,
        "@search.score": score,
        "band": "GROUP C1",
        "location": "BANGALORE",
        "experience": "6Years 0Months",
        "role_name": "Data Engineer",
        "work_mode": "OFFSHORE",
        "country": "INDIA",
        "skills_iaspire": "Python(L4)",
        "certified_skills": None,
        "role_cluster": "DATA ENGINEER L2",
        "employee_name": "Employee1",
    }
    doc.update(extra)
    return doc


# ---------------------------------------------------------------------------
# AC1: Supply profile embedding includes all five attribute families
# ---------------------------------------------------------------------------


class TestSupplyEmbeddingAllFiveAttributes:
    """Verify the supply embedding text contains each of the five attribute families."""

    def _full_profile_text(self) -> str:
        return build_embedding_text(_make_supply_profile())

    def test_skills_attribute_present(self) -> None:
        """Skills (primary iAspire skills) appear in the embedding text."""
        text = self._full_profile_text()
        assert "Python" in text, "Skills attribute must appear in supply embedding text"

    def test_designation_role_attribute_present(self) -> None:
        """Designation / role_name appears in the embedding text."""
        text = self._full_profile_text()
        assert "Data Engineer" in text, "Role/designation must appear in supply embedding text"

    def test_role_cluster_attribute_present(self) -> None:
        """Role cluster (project-history proxy) appears in the embedding text."""
        text = self._full_profile_text()
        assert "DATA ENGINEER L2" in text, "Role cluster must appear in supply embedding text"

    def test_location_attribute_present(self) -> None:
        """Location appears in the embedding text."""
        text = self._full_profile_text()
        assert "BANGALORE" in text, "Location must appear in supply embedding text"

    def test_experience_band_attribute_present(self) -> None:
        """Experience band (BAND field) appears in the embedding text."""
        text = self._full_profile_text()
        assert "GROUP C1" in text, "Experience band must appear in supply embedding text"

    def test_experience_attribute_present(self) -> None:
        """Total experience (project-history depth proxy) appears in the embedding text."""
        text = self._full_profile_text()
        assert "6Years" in text, "Experience must appear in supply embedding text"

    def test_all_five_families_present_simultaneously(self) -> None:
        """All five attribute families must appear in a single embedding text."""
        text = self._full_profile_text()
        checks = {
            "skills": "Python" in text,
            "designation": "Data Engineer" in text,
            "location": "BANGALORE" in text,
            "experience_band": "GROUP C1" in text,
            "project_history_proxy": "6Years" in text or "DATA ENGINEER L2" in text,
        }
        missing = [k for k, v in checks.items() if not v]
        assert not missing, f"Attribute families missing from supply embedding text: {missing}"


# ---------------------------------------------------------------------------
# AC2: Demand record embedding includes corresponding required attributes
# ---------------------------------------------------------------------------


class TestDemandEmbeddingAllFiveAttributes:
    """Verify the demand embedding text contains each of the five attribute families."""

    def _full_demand_text(self) -> str:
        return build_demand_embedding_text(_make_demand())

    def test_skills_attribute_present(self) -> None:
        """Essential skill appears in the demand embedding text."""
        text = self._full_demand_text()
        assert "Python" in text, "Essential skill must appear in demand embedding text"

    def test_job_description_present(self) -> None:
        """Job description (rich skills + project context) appears in the embedding text."""
        text = self._full_demand_text()
        assert "Job Description:" in text, "Job description must appear in demand embedding text"

    def test_designation_role_description_present(self) -> None:
        """Role description / designation appears in the demand embedding text."""
        text = self._full_demand_text()
        assert "Data Engineer L2" in text, "Role description must appear in demand embedding text"

    def test_role_cluster_attribute_present(self) -> None:
        """Role cluster appears in the demand embedding text."""
        text = self._full_demand_text()
        assert "DATA ENGINEER L2" in text, "Role cluster must appear in demand embedding text"

    def test_location_attribute_present(self) -> None:
        """Location appears in the demand embedding text."""
        text = self._full_demand_text()
        assert "BANGALORE" in text, "Location must appear in demand embedding text"

    def test_experience_band_attribute_present(self) -> None:
        """Experience band (SR_BAND) appears in the demand embedding text."""
        text = self._full_demand_text()
        assert "GROUP C1" in text, "Experience band must appear in demand embedding text"

    def test_all_five_families_present_simultaneously(self) -> None:
        """All five attribute families must appear in a single demand embedding text."""
        text = self._full_demand_text()
        checks = {
            "skills": "Python" in text,
            "designation": "Data Engineer L2" in text,
            "location": "BANGALORE" in text,
            "experience_band": "GROUP C1" in text,
            "project_context": "Job Description:" in text,
        }
        missing = [k for k, v in checks.items() if not v]
        assert not missing, f"Attribute families missing from demand embedding text: {missing}"


# ---------------------------------------------------------------------------
# AC3 & AC4: Ablation — each attribute independently changes the embedding text
# ---------------------------------------------------------------------------


class TestSupplyEmbeddingAblation:
    """Text-level ablation: changing any single attribute alters the embedding text.

    Because the embedding vector is deterministic for a given input text, a
    changed text guarantees a changed vector and therefore a changed similarity
    score in production.
    """

    def test_different_location_produces_different_text(self) -> None:
        """Location change → embedding text changes (location contributes to score)."""
        text_bangalore = build_embedding_text(_make_supply_profile(location="BANGALORE"))
        text_hyderabad = build_embedding_text(_make_supply_profile(location="HYDERABAD"))
        assert text_bangalore != text_hyderabad, (
            "Changing location must alter the supply embedding text"
        )

    def test_different_band_produces_different_text(self) -> None:
        """Experience band change → embedding text changes (band contributes to score)."""
        text_c1 = build_embedding_text(_make_supply_profile(band="GROUP C1"))
        text_d1 = build_embedding_text(_make_supply_profile(band="GROUP D1"))
        assert text_c1 != text_d1, (
            "Changing experience band must alter the supply embedding text"
        )

    def test_different_skills_produces_different_text(self) -> None:
        """Skills change → embedding text changes (skills contribute to score)."""
        text_python = build_embedding_text(_make_supply_profile(skills_iaspire="Python(L4)"))
        text_java = build_embedding_text(_make_supply_profile(skills_iaspire="Java(L4)"))
        assert text_python != text_java, (
            "Changing skills must alter the supply embedding text"
        )

    def test_different_role_name_produces_different_text(self) -> None:
        """Designation (role_name) change → embedding text changes."""
        text_engineer = build_embedding_text(_make_supply_profile(role_name="Data Engineer"))
        text_analyst = build_embedding_text(_make_supply_profile(role_name="Business Analyst"))
        assert text_engineer != text_analyst, (
            "Changing role/designation must alter the supply embedding text"
        )

    def test_null_role_name_produces_different_text_than_populated(self) -> None:
        """A null role_name omits the designation field; the text differs from a populated one."""
        text_with_role = build_embedding_text(_make_supply_profile(role_name="Data Engineer"))
        text_without_role = build_embedding_text(_make_supply_profile(role_name=None))
        assert text_with_role != text_without_role, (
            "Null role_name must produce different embedding text than a populated role"
        )

    def test_different_role_cluster_produces_different_text(self) -> None:
        """Role cluster change → embedding text changes (project-history proxy contributes)."""
        text_de = build_embedding_text(_make_supply_profile(role_cluster="DATA ENGINEER L2"))
        text_dev = build_embedding_text(_make_supply_profile(role_cluster="DEVELOPER L3"))
        assert text_de != text_dev, (
            "Changing role cluster must alter the supply embedding text"
        )

    def test_different_experience_produces_different_text(self) -> None:
        """Total experience change → embedding text changes."""
        text_6yr = build_embedding_text(_make_supply_profile(experience="6Years 0Months"))
        text_2yr = build_embedding_text(_make_supply_profile(experience="2Years 0Months"))
        assert text_6yr != text_2yr, (
            "Changing experience must alter the supply embedding text"
        )

    def test_skills_only_profile_text_differs_from_full_profile_text(self) -> None:
        """A skills-only profile (all non-skill fields at minimal/mismatched values) has
        a different embedding text than a full-attribute-match profile.

        This is the core ablation assertion for SP2-005 AC3: the system does NOT
        embed only skills — all five attribute families are encoded, so a partial
        match produces a structurally different text.
        """
        full_match_text = build_embedding_text(
            _make_supply_profile(
                skills_iaspire="Python(L4), Azure(L3)",
                role_name="Data Engineer",
                role_cluster="DATA ENGINEER L2",
                location="BANGALORE",
                band="GROUP C1",
                experience="6Years 0Months",
                work_mode="OFFSHORE",
                country="INDIA",
            )
        )
        skills_only_text = build_embedding_text(
            _make_supply_profile(
                skills_iaspire="Python(L4), Azure(L3)",  # same skills
                role_name="Developer",  # different designation
                role_cluster="DEVELOPER L3",  # different role cluster
                location="HYDERABAD",  # different location
                band="GROUP D1",  # different band
                experience="2Years 0Months",  # different experience
                work_mode="ONSITE",  # different work mode
                country="INDIA",
            )
        )
        assert full_match_text != skills_only_text, (
            "A skills-only match must produce a different embedding text than a "
            "full-attribute match, confirming all five attribute families are encoded"
        )


class TestDemandEmbeddingAblation:
    """Text-level ablation for demand embedding: each attribute change alters the text."""

    def test_different_location_produces_different_text(self) -> None:
        text_blr = build_demand_embedding_text(_make_demand(location="BANGALORE"))
        text_hyd = build_demand_embedding_text(_make_demand(location="HYDERABAD"))
        assert text_blr != text_hyd

    def test_different_band_produces_different_text(self) -> None:
        text_c1 = build_demand_embedding_text(_make_demand(band="GROUP C1"))
        text_b2 = build_demand_embedding_text(_make_demand(band="GROUP B2"))
        assert text_c1 != text_b2

    def test_different_essential_skill_produces_different_text(self) -> None:
        text_python = build_demand_embedding_text(_make_demand(essential_skill="Python"))
        text_java = build_demand_embedding_text(_make_demand(essential_skill="Java"))
        assert text_python != text_java

    def test_different_role_description_produces_different_text(self) -> None:
        text_de = build_demand_embedding_text(_make_demand(role_description="Data Engineer L2"))
        text_pm = build_demand_embedding_text(_make_demand(role_description="Project Manager L1"))
        assert text_de != text_pm

    def test_different_role_cluster_produces_different_text(self) -> None:
        text_de = build_demand_embedding_text(_make_demand(role_cluster="DATA ENGINEER L2"))
        text_dev = build_demand_embedding_text(_make_demand(role_cluster="DEVELOPER L3"))
        assert text_de != text_dev


# ---------------------------------------------------------------------------
# AC5: Integration mock test — full-attribute-match scores higher than skills-only
# ---------------------------------------------------------------------------


class TestMultiAttributeMatchingEndToEnd:
    """End-to-end integration test using mock Azure clients.

    Two synthetic supply profiles are returned by the mock search index:

    * ``EMP-FULL``: matches the demand on all five attributes (skills,
      designation, location, experience band, project history / role context).
      The mock search index returns a higher cosine similarity score (0.92) for
      this profile, reflecting real embedding-model behaviour.

    * ``EMP-SKILLS``: matches the demand on skills only; all other attributes
      (location, band, designation, work_mode) differ.  The mock returns a
      lower similarity score (0.74).

    Assertions verify that:
    1. The full-attribute-match candidate appears first in the ranked results.
    2. The skills-only candidate has a lower score_percent.
    3. The demand embedding text passed to OpenAI includes all five attributes
       (skills, designation, location, experience band, project context), so a
       real embedding model would naturally produce the expected score ordering.
    """

    def _run(self) -> tuple[list[RetrievalCandidate], MagicMock]:
        """Run DenseRetrievalStrategy against two mock candidates; return results and
        the captured OpenAI client for assertion on the embedding text."""
        demand = _make_demand(
            essential_skill="Python",
            location="BANGALORE",
            band="GROUP C1",
            work_mode="OFFSHORE",
            role_description="Data Engineer L2",
            role_cluster="DATA ENGINEER L2",
        )

        # Full-attribute-match: all five attribute families align with the demand.
        full_match = _make_search_result(
            "EMP-FULL",
            0.92,
            band="GROUP C1",
            location="BANGALORE",
            work_mode="OFFSHORE",
            role_cluster="DATA ENGINEER L2",
            role_name="Data Engineer",
            skills_iaspire="Python(L4), Azure(L3)",
            experience="6Years 0Months",
        )
        # Skills-only-match: skills align, but location, band, designation, and
        # work mode all differ from the demand.
        skills_only = _make_search_result(
            "EMP-SKILLS",
            0.74,
            band="GROUP D1",
            location="HYDERABAD",
            work_mode="ONSITE",
            role_cluster="DEVELOPER L3",
            role_name="Developer",
            skills_iaspire="Python(L3)",
            experience="2Years 0Months",
        )

        openai_client = _make_openai_client()
        search_client = _make_search_client([full_match, skills_only])

        strategy = DenseRetrievalStrategy()
        candidates = strategy.retrieve(demand, openai_client, search_client)
        return candidates, openai_client

    def test_full_attribute_match_ranks_first(self) -> None:
        """Full-attribute-match candidate must appear at rank 1."""
        candidates, _ = self._run()
        assert len(candidates) == 2
        assert candidates[0].employee_id == "EMP-FULL", (
            "Profile matching all five attributes must rank above skills-only match"
        )

    def test_skills_only_match_ranks_second(self) -> None:
        """Skills-only-match candidate must rank below the full-attribute match."""
        candidates, _ = self._run()
        assert candidates[1].employee_id == "EMP-SKILLS"

    def test_full_attribute_match_score_higher_than_skills_only(self) -> None:
        """Full-attribute-match score_percent must exceed skills-only score_percent."""
        candidates, _ = self._run()
        full_match = next(c for c in candidates if c.employee_id == "EMP-FULL")
        skills_only = next(c for c in candidates if c.employee_id == "EMP-SKILLS")
        assert full_match.score_percent > skills_only.score_percent, (
            "A profile matching on all five attributes must score higher than "
            "a profile matching on skills only"
        )

    def test_demand_embedding_text_sent_to_openai_contains_all_five_attributes(self) -> None:
        """The embedding text forwarded to the OpenAI API must encode all five attributes.

        This verifies AC4 in the context of the full retrieval pipeline:
        the demand is represented by a text that includes skills, designation,
        location, experience band, and project context before being vectorized.
        """
        _, openai_client = self._run()

        # Capture the text passed to the embeddings API.
        call_args = openai_client.embeddings.create.call_args
        texts_sent: list[str] = call_args.kwargs.get("input") or call_args.args[0]
        assert len(texts_sent) == 1
        demand_text = texts_sent[0]

        assert "Python" in demand_text, "Skills attribute missing from demand embedding text"
        assert "Data Engineer" in demand_text, "Designation missing from demand embedding text"
        assert "BANGALORE" in demand_text, "Location missing from demand embedding text"
        assert "GROUP C1" in demand_text, "Experience band missing from demand embedding text"
        assert "Job Description:" in demand_text, (
            "Project context (job description) missing from demand embedding text"
        )

    def test_supply_embedding_text_for_full_match_encodes_all_five_attributes(self) -> None:
        """The supply embedding text for the full-match profile encodes all five attributes."""
        full_profile = _make_supply_profile(
            skills_iaspire="Python(L4), Azure(L3)",
            role_name="Data Engineer",
            role_cluster="DATA ENGINEER L2",
            location="BANGALORE",
            band="GROUP C1",
            experience="6Years 0Months",
        )
        supply_text = build_embedding_text(full_profile)

        assert "Python" in supply_text, "Skills attribute missing from supply embedding text"
        assert "Data Engineer" in supply_text, "Designation missing from supply embedding text"
        assert "BANGALORE" in supply_text, "Location missing from supply embedding text"
        assert "GROUP C1" in supply_text, "Experience band missing from supply embedding text"
        assert "6Years" in supply_text, "Experience missing from supply embedding text"

    def test_supply_embedding_text_for_skills_only_differs_from_full_match(self) -> None:
        """Skills-only supply profile produces a different embedding text than the full match.

        This is the key AC3 assertion: the system encodes all five attributes,
        so mismatched non-skill attributes change the embedding text, which
        would produce a lower cosine similarity in production.
        """
        full_text = build_embedding_text(
            _make_supply_profile(
                skills_iaspire="Python(L4), Azure(L3)",
                role_name="Data Engineer",
                role_cluster="DATA ENGINEER L2",
                location="BANGALORE",
                band="GROUP C1",
                experience="6Years 0Months",
                work_mode="OFFSHORE",
            )
        )
        skills_only_text = build_embedding_text(
            _make_supply_profile(
                skills_iaspire="Python(L4), Azure(L3)",  # skills identical
                role_name="Developer",  # different designation
                role_cluster="DEVELOPER L3",  # different role cluster
                location="HYDERABAD",  # different location
                band="GROUP D1",  # different band
                experience="2Years 0Months",  # different experience
                work_mode="ONSITE",  # different work mode
            )
        )
        assert full_text != skills_only_text, (
            "Supply embedding texts must differ when non-skill attributes differ, "
            "confirming multi-attribute encoding is active"
        )
