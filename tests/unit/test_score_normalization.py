"""Unit tests: similarity score normalization — SP2-002.

Validates ``normalize_similarity_score`` from ``src.matching.retriever`` against
the normalization rules defined in ``docs/contracts/similarity-and-cache-contract.md``.

No real Azure services are required.  All tests are pure-Python.
"""

from __future__ import annotations

import math

import pytest

from src.backend.matching.retriever import normalize_similarity_score


# ---------------------------------------------------------------------------
# Boundary values — Azure AI Search [0.0, 1.0] domain (default)
# ---------------------------------------------------------------------------


class TestBoundaryValues:
    def test_raw_1_0_maps_to_100(self) -> None:
        similarity, score_percent = normalize_similarity_score(1.0)
        assert score_percent == 100
        assert similarity == pytest.approx(1.0)

    def test_raw_0_0_maps_to_0(self) -> None:
        similarity, score_percent = normalize_similarity_score(0.0)
        assert score_percent == 0
        assert similarity == pytest.approx(0.0)

    def test_negative_raw_maps_to_0(self) -> None:
        """Negative raw scores are clamped to similarity=0, score_percent=0."""
        similarity, score_percent = normalize_similarity_score(-0.5)
        assert score_percent == 0
        assert similarity == pytest.approx(0.0)

    def test_raw_above_max_clamped_to_100(self) -> None:
        """Raw scores above raw_max are clamped to similarity=1.0, score_percent=100."""
        similarity, score_percent = normalize_similarity_score(1.5)
        assert score_percent == 100
        assert similarity == pytest.approx(1.0)

    def test_raw_exactly_at_threshold_70_pct(self) -> None:
        """Raw 0.70 → score_percent 70 (threshold boundary used in SP2-003)."""
        _, score_percent = normalize_similarity_score(0.70)
        assert score_percent == 70

    def test_raw_just_below_threshold_69_pct(self) -> None:
        """Raw 0.69 → score_percent 69."""
        _, score_percent = normalize_similarity_score(0.69)
        assert score_percent == 69


# ---------------------------------------------------------------------------
# Mid-range values
# ---------------------------------------------------------------------------


class TestMidRangeValues:
    def test_raw_0_5_maps_to_50(self) -> None:
        _, score_percent = normalize_similarity_score(0.5)
        assert score_percent == 50

    def test_raw_0_871234_maps_to_87(self) -> None:
        """Contract example: similarity_raw=0.871234 → score_percent=87."""
        similarity, score_percent = normalize_similarity_score(0.871234)
        assert score_percent == 87
        assert similarity == pytest.approx(0.871234, abs=1e-6)

    def test_raw_0_875_rounds_to_88(self) -> None:
        """0.875 * 100 = 87.5 → rounds to 88 (Python banker's rounding: round(87.5) == 88)."""
        _, score_percent = normalize_similarity_score(0.875)
        assert score_percent == round(0.875 * 100)

    def test_raw_0_25_maps_to_25(self) -> None:
        _, score_percent = normalize_similarity_score(0.25)
        assert score_percent == 25

    def test_similarity_float_precision(self) -> None:
        """similarity field retains full float precision, not truncated."""
        raw = 0.123456789
        similarity, _ = normalize_similarity_score(raw)
        assert abs(similarity - raw) < 1e-9


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------


class TestReproducibility:
    def test_same_input_produces_same_output(self) -> None:
        raw = 0.8531
        result_a = normalize_similarity_score(raw)
        result_b = normalize_similarity_score(raw)
        assert result_a == result_b

    def test_deterministic_across_calls(self) -> None:
        for raw in [0.0, 0.3, 0.7, 0.9999, 1.0]:
            a = normalize_similarity_score(raw)
            b = normalize_similarity_score(raw)
            assert a == b, f"Non-deterministic output for raw={raw}"


# ---------------------------------------------------------------------------
# NaN and degenerate domain handling
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_nan_raw_maps_to_0(self) -> None:
        similarity, score_percent = normalize_similarity_score(math.nan)
        assert score_percent == 0
        assert similarity == pytest.approx(0.0)

    def test_degenerate_domain_maps_to_0(self) -> None:
        """raw_min == raw_max is undefined; must not raise and returns 0."""
        similarity, score_percent = normalize_similarity_score(
            0.5, raw_min=0.5, raw_max=0.5
        )
        assert score_percent == 0
        assert similarity == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Cosine similarity [-1, 1] domain
# ---------------------------------------------------------------------------


class TestCosineNegativeOneDomain:
    """When the retrieval engine returns raw cosine scores in [-1, 1]."""

    def test_raw_1_0_in_neg1_pos1_domain_maps_to_100(self) -> None:
        _, score_percent = normalize_similarity_score(1.0, raw_min=-1.0, raw_max=1.0)
        assert score_percent == 100

    def test_raw_minus_1_in_neg1_pos1_domain_maps_to_0(self) -> None:
        similarity, score_percent = normalize_similarity_score(
            -1.0, raw_min=-1.0, raw_max=1.0
        )
        assert score_percent == 0
        assert similarity == pytest.approx(0.0)

    def test_raw_0_in_neg1_pos1_domain_maps_to_50(self) -> None:
        """Orthogonal vectors (raw=0) are neutral; should map to 50%."""
        _, score_percent = normalize_similarity_score(0.0, raw_min=-1.0, raw_max=1.0)
        assert score_percent == 50

    def test_formula_equivalent_to_contract(self) -> None:
        """Verify: similarity = (raw + 1.0) / 2.0 per the contract formula."""
        raw = 0.6
        expected_similarity = (raw + 1.0) / 2.0
        similarity, _ = normalize_similarity_score(raw, raw_min=-1.0, raw_max=1.0)
        assert similarity == pytest.approx(expected_similarity, abs=1e-9)

    def test_negative_raw_below_domain_still_clamped_to_0(self) -> None:
        """Score below -1.0 is clamped; does not produce negative score_percent."""
        similarity, score_percent = normalize_similarity_score(
            -1.5, raw_min=-1.0, raw_max=1.0
        )
        assert score_percent == 0
        assert similarity == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Return type contract
# ---------------------------------------------------------------------------


class TestReturnTypes:
    def test_returns_tuple_of_two_elements(self) -> None:
        result = normalize_similarity_score(0.75)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_similarity_is_float(self) -> None:
        similarity, _ = normalize_similarity_score(0.75)
        assert isinstance(similarity, float)

    def test_score_percent_is_int(self) -> None:
        _, score_percent = normalize_similarity_score(0.75)
        assert isinstance(score_percent, int)

    def test_similarity_always_in_0_to_1_range(self) -> None:
        for raw in [-10.0, -1.0, -0.001, 0.0, 0.5, 1.0, 1.001, 10.0]:
            similarity, _ = normalize_similarity_score(raw)
            assert 0.0 <= similarity <= 1.0, f"similarity out of range for raw={raw}"

    def test_score_percent_always_in_0_to_100_range(self) -> None:
        for raw in [-10.0, -1.0, -0.001, 0.0, 0.5, 1.0, 1.001, 10.0]:
            _, score_percent = normalize_similarity_score(raw)
            assert 0 <= score_percent <= 100, f"score_percent out of range for raw={raw}"


# ---------------------------------------------------------------------------
# Integration with RetrievalCandidate — normalized fields populated by DenseRetrievalStrategy
# ---------------------------------------------------------------------------


class TestRetrievalCandidateNormalizedFields:
    """Verify that DenseRetrievalStrategy populates similarity and score_percent."""

    def _make_mock_infrastructure(self) -> tuple:
        import sys
        import types
        from unittest.mock import MagicMock

        for _mod in [
            "azure",
            "azure.identity",
            "azure.core",
            "azure.core.credentials",
            "azure.search",
            "azure.search.documents",
            "azure.search.documents.models",
        ]:
            if _mod not in sys.modules:
                sys.modules[_mod] = types.ModuleType(_mod)

        _stub = sys.modules["azure.search.documents.models"]
        if not hasattr(_stub, "VectorizedQuery"):
            _stub.VectorizedQuery = MagicMock()

        mock_item = MagicMock()
        mock_item.embedding = [0.1] * 1536
        mock_response = MagicMock()
        mock_response.data = [mock_item]
        openai_client = MagicMock()
        openai_client.embeddings.create.return_value = mock_response

        search_client = MagicMock()
        return openai_client, search_client

    def _make_demand(self):
        import types as _types
        from datetime import date

        return _types.SimpleNamespace(
            demand_id=1,
            customer_name="CustomerA",
            essential_skill="Python",
            location="BANGALORE",
            country="INDIA",
            created_on=date(2026, 4, 1),
            start_date=date(2026, 5, 1),
            end_date=date(2026, 6, 30),
            role_description="Data Engineer L2",
            work_mode="OFFSHORE",
            band="GROUP C1",
            open_positions=2,
            job_description="Seeking a Data Engineer with Python and Azure skills.",
            role_cluster="DATA ENGINEER L2",
        )

    def test_candidate_has_similarity_field(self) -> None:
        from src.backend.matching.retriever import DenseRetrievalStrategy

        openai_client, search_client = self._make_mock_infrastructure()
        result_doc = {
            "employee_id": "EMP-001",
            "id": "EMP-001",
            "@search.score": 0.87,
            "band": "GROUP B2",
        }
        search_client.search.return_value = iter([result_doc])

        candidates = DenseRetrievalStrategy().retrieve(
            self._make_demand(), openai_client, search_client
        )

        assert len(candidates) == 1
        assert candidates[0].similarity == pytest.approx(0.87, abs=1e-6)

    def test_candidate_has_score_percent_field(self) -> None:
        from src.backend.matching.retriever import DenseRetrievalStrategy

        openai_client, search_client = self._make_mock_infrastructure()
        result_doc = {
            "employee_id": "EMP-001",
            "id": "EMP-001",
            "@search.score": 0.871234,
            "band": "GROUP B2",
        }
        search_client.search.return_value = iter([result_doc])

        candidates = DenseRetrievalStrategy().retrieve(
            self._make_demand(), openai_client, search_client
        )

        assert candidates[0].score_percent == 87

    def test_score_percent_consistent_with_normalize_function(self) -> None:
        """score_percent on the candidate must equal normalize_similarity_score output."""
        from src.backend.matching.retriever import DenseRetrievalStrategy

        openai_client, search_client = self._make_mock_infrastructure()
        raw = 0.763
        result_doc = {
            "employee_id": "EMP-002",
            "id": "EMP-002",
            "@search.score": raw,
        }
        search_client.search.return_value = iter([result_doc])

        candidates = DenseRetrievalStrategy().retrieve(
            self._make_demand(), openai_client, search_client
        )

        expected_similarity, expected_score_percent = normalize_similarity_score(raw)
        assert candidates[0].similarity == pytest.approx(expected_similarity, abs=1e-9)
        assert candidates[0].score_percent == expected_score_percent
