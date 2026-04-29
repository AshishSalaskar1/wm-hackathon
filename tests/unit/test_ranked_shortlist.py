"""Unit tests: ranked top-10 shortlist generation — SP2-004.

Validates ``rank_shortlist`` from ``src.matching.retriever`` against the
acceptance criteria defined in the sprint plan for SP2-004.

No real Azure services are required.  All tests are pure-Python.
"""

from __future__ import annotations

import pytest

from src.backend.matching.retriever import RetrievalCandidate, TOP_SHORTLIST_SIZE, rank_shortlist


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _candidate(employee_id: str, score_percent: int) -> RetrievalCandidate:
    """Return a minimal RetrievalCandidate with the given score_percent."""
    similarity = score_percent / 100.0
    return RetrievalCandidate(
        employee_id=employee_id,
        similarity_raw=similarity,
        similarity=similarity,
        score_percent=score_percent,
    )


# ---------------------------------------------------------------------------
# Core shortlist behaviour (AC from sprint plan)
# ---------------------------------------------------------------------------


class TestRankShortlistCoreAcceptanceCriteria:
    def test_fifteen_candidates_returns_top_ten(self) -> None:
        """15 candidates above threshold → returns top 10 in correct order."""
        # Scores 71–85 (15 unique values)
        candidates = [_candidate(f"EMP-{i:02d}", 71 + i) for i in range(15)]
        result = rank_shortlist(candidates)

        assert len(result) == TOP_SHORTLIST_SIZE
        # Highest score (85) must be rank 1; lowest in shortlist (76) must be rank 10.
        assert result[0].score_percent == 85
        assert result[9].score_percent == 76

    def test_fifteen_candidates_ranks_one_through_ten(self) -> None:
        """Ranks are assigned 1 through 10 for a 15-candidate input."""
        candidates = [_candidate(f"EMP-{i:02d}", 71 + i) for i in range(15)]
        result = rank_shortlist(candidates)

        for expected_rank, candidate in enumerate(result, start=1):
            assert candidate.rank == expected_rank

    def test_five_candidates_returns_all_five(self) -> None:
        """5 candidates → returns all 5 (fewer than top_n)."""
        candidates = [_candidate(f"EMP-{i}", 75 + i) for i in range(5)]
        result = rank_shortlist(candidates)

        assert len(result) == 5

    def test_five_candidates_ranks_one_through_five(self) -> None:
        """Ranks 1–5 assigned when shortlist has fewer than 10 entries."""
        candidates = [_candidate(f"EMP-{i}", 75 + i) for i in range(5)]
        result = rank_shortlist(candidates)

        for expected_rank, candidate in enumerate(result, start=1):
            assert candidate.rank == expected_rank

    def test_zero_candidates_returns_empty_list(self) -> None:
        """0 above threshold → returns empty list (not an error)."""
        result = rank_shortlist([])
        assert result == []


# ---------------------------------------------------------------------------
# Ordering and determinism
# ---------------------------------------------------------------------------


class TestOrdering:
    def test_sorted_descending_by_score_percent(self) -> None:
        """Results are ordered highest score_percent first."""
        candidates = [
            _candidate("EMP-C", 72),
            _candidate("EMP-A", 90),
            _candidate("EMP-B", 81),
        ]
        result = rank_shortlist(candidates)

        scores = [c.score_percent for c in result]
        assert scores == sorted(scores, reverse=True)

    def test_tie_breaking_by_employee_id_ascending(self) -> None:
        """Equal score_percent → employee_id ascending determines order."""
        candidates = [
            _candidate("EMP-C", 85),
            _candidate("EMP-A", 85),
            _candidate("EMP-B", 85),
        ]
        result = rank_shortlist(candidates)

        ids = [c.employee_id for c in result]
        assert ids == ["EMP-A", "EMP-B", "EMP-C"]

    def test_deterministic_for_same_input(self) -> None:
        """Calling rank_shortlist twice on the same data produces the same order."""
        candidates = [
            _candidate("EMP-Z", 80),
            _candidate("EMP-A", 80),
            _candidate("EMP-M", 90),
        ]
        result_a = rank_shortlist(candidates)
        result_b = rank_shortlist(candidates)

        assert [c.employee_id for c in result_a] == [c.employee_id for c in result_b]

    def test_rank_one_is_highest_score(self) -> None:
        """The candidate with the highest score_percent receives rank 1."""
        candidates = [
            _candidate("EMP-LOW", 75),
            _candidate("EMP-HIGH", 95),
            _candidate("EMP-MID", 82),
        ]
        result = rank_shortlist(candidates)

        assert result[0].employee_id == "EMP-HIGH"
        assert result[0].rank == 1


# ---------------------------------------------------------------------------
# Boundary: exactly 10 candidates
# ---------------------------------------------------------------------------


class TestExactlyTenCandidates:
    def test_exactly_ten_returns_all_ten(self) -> None:
        """10 candidates → all 10 returned."""
        candidates = [_candidate(f"EMP-{i:02d}", 80 + i) for i in range(10)]
        result = rank_shortlist(candidates)

        assert len(result) == 10

    def test_exactly_ten_ranks_one_through_ten(self) -> None:
        """10 candidates → ranks 1–10 assigned."""
        candidates = [_candidate(f"EMP-{i:02d}", 80 + i) for i in range(10)]
        result = rank_shortlist(candidates)

        for expected_rank, candidate in enumerate(result, start=1):
            assert candidate.rank == expected_rank


# ---------------------------------------------------------------------------
# Result item completeness
# ---------------------------------------------------------------------------


class TestResultItemContents:
    def test_result_items_include_all_supply_profile_attributes(self) -> None:
        """Result items carry the full document dict from the supply profile."""
        doc = {"skills": "Python", "designation": "Engineer", "location": "London"}
        candidate = RetrievalCandidate(
            employee_id="EMP-DOC",
            similarity_raw=0.9,
            similarity=0.9,
            score_percent=90,
            document=doc,
        )
        result = rank_shortlist([candidate])

        assert result[0].document == doc

    def test_result_item_contains_employee_id_score_and_rank(self) -> None:
        """Each result item exposes employee_id, score_percent, and rank."""
        candidate = _candidate("EMP-X", 88)
        result = rank_shortlist([candidate])

        item = result[0]
        assert item.employee_id == "EMP-X"
        assert item.score_percent == 88
        assert item.rank == 1


# ---------------------------------------------------------------------------
# Custom top_n override
# ---------------------------------------------------------------------------


class TestTopNOverride:
    def test_custom_top_n_limits_shortlist_size(self) -> None:
        """Passing top_n=5 caps the shortlist at 5 even with 15 input candidates."""
        candidates = [_candidate(f"EMP-{i:02d}", 71 + i) for i in range(15)]
        result = rank_shortlist(candidates, top_n=5)

        assert len(result) == 5

    def test_custom_top_n_assigns_ranks_from_one(self) -> None:
        """Ranks start at 1 regardless of the top_n value."""
        candidates = [_candidate(f"EMP-{i:02d}", 71 + i) for i in range(15)]
        result = rank_shortlist(candidates, top_n=5)

        assert result[0].rank == 1
        assert result[4].rank == 5
