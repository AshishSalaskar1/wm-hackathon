"""Unit tests: similarity score threshold enforcement — SP2-003.

Validates ``apply_threshold`` from ``src.matching.retriever`` against the
acceptance criteria defined in the sprint plan for SP2-003.

No real Azure services are required.  All tests are pure-Python.
"""

from __future__ import annotations

import pytest

from src.backend.matching.retriever import RetrievalCandidate, apply_threshold


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
# Core filtering behaviour
# ---------------------------------------------------------------------------


class TestApplyThreshold:
    def test_candidates_above_threshold_are_returned(self) -> None:
        """Candidates with score_percent > threshold pass through."""
        candidates = [
            _candidate("EMP-A", 95),
            _candidate("EMP-B", 80),
            _candidate("EMP-C", 71),
        ]
        result = apply_threshold(candidates, threshold=70)
        assert len(result) == 3
        ids = {c.employee_id for c in result}
        assert ids == {"EMP-A", "EMP-B", "EMP-C"}

    def test_candidate_at_threshold_is_included(self) -> None:
        """score_percent == threshold is accepted (inclusive lower bound)."""
        candidates = [_candidate("EMP-AT", 70)]
        result = apply_threshold(candidates, threshold=70)
        assert len(result) == 1
        assert result[0].employee_id == "EMP-AT"

    def test_candidate_below_threshold_is_excluded(self) -> None:
        """score_percent < threshold is filtered out."""
        candidates = [_candidate("EMP-LOW", 69)]
        result = apply_threshold(candidates, threshold=70)
        assert result == []

    def test_mixed_list_returns_only_passing_candidates(self) -> None:
        """Only candidates meeting or exceeding the threshold are returned."""
        candidates = [
            _candidate("EMP-PASS-95", 95),
            _candidate("EMP-PASS-70", 70),
            _candidate("EMP-FAIL-69", 69),
            _candidate("EMP-FAIL-0", 0),
        ]
        result = apply_threshold(candidates, threshold=70)
        assert len(result) == 2
        ids = {c.employee_id for c in result}
        assert ids == {"EMP-PASS-95", "EMP-PASS-70"}

    def test_empty_input_returns_empty_list(self) -> None:
        """Empty candidate list always returns an empty list (not an error)."""
        result = apply_threshold([], threshold=70)
        assert result == []

    def test_all_candidates_fail_threshold_returns_empty_list(self) -> None:
        """Zero passing candidates is a valid (non-error) outcome."""
        candidates = [
            _candidate("EMP-A", 65),
            _candidate("EMP-B", 50),
            _candidate("EMP-C", 10),
        ]
        result = apply_threshold(candidates, threshold=70)
        assert result == []

    def test_all_candidates_pass_threshold_returns_all(self) -> None:
        """All candidates above threshold are returned without truncation."""
        candidates = [_candidate(f"EMP-{i}", 70 + i) for i in range(5)]
        result = apply_threshold(candidates, threshold=70)
        assert len(result) == 5


# ---------------------------------------------------------------------------
# Configurable threshold via explicit argument
# ---------------------------------------------------------------------------


class TestExplicitThreshold:
    def test_threshold_80_excludes_scores_below_80(self) -> None:
        candidates = [
            _candidate("EMP-A", 85),
            _candidate("EMP-B", 80),
            _candidate("EMP-C", 79),
        ]
        result = apply_threshold(candidates, threshold=80)
        assert len(result) == 2
        ids = {c.employee_id for c in result}
        assert ids == {"EMP-A", "EMP-B"}

    def test_threshold_75_accepts_75_and_above(self) -> None:
        candidates = [
            _candidate("EMP-ABOVE", 76),
            _candidate("EMP-AT", 75),
            _candidate("EMP-BELOW", 74),
        ]
        result = apply_threshold(candidates, threshold=75)
        assert len(result) == 2
        assert {c.employee_id for c in result} == {"EMP-ABOVE", "EMP-AT"}


# ---------------------------------------------------------------------------
# Environment variable — MATCH_SCORE_THRESHOLD
# ---------------------------------------------------------------------------


class TestEnvironmentVariable:
    def test_env_var_default_is_70(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When MATCH_SCORE_THRESHOLD is absent the default is 70."""
        monkeypatch.delenv("MATCH_SCORE_THRESHOLD", raising=False)
        candidates = [
            _candidate("EMP-PASS", 70),
            _candidate("EMP-FAIL", 69),
        ]
        result = apply_threshold(candidates)
        assert len(result) == 1
        assert result[0].employee_id == "EMP-PASS"

    def test_env_var_70_accepted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MATCH_SCORE_THRESHOLD", "70")
        candidates = [_candidate("EMP-AT", 70), _candidate("EMP-BELOW", 69)]
        result = apply_threshold(candidates)
        assert len(result) == 1
        assert result[0].employee_id == "EMP-AT"

    def test_env_var_80_accepted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MATCH_SCORE_THRESHOLD", "80")
        candidates = [_candidate("EMP-AT", 80), _candidate("EMP-BELOW", 79)]
        result = apply_threshold(candidates)
        assert len(result) == 1
        assert result[0].employee_id == "EMP-AT"

    def test_env_var_below_70_raises_value_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MATCH_SCORE_THRESHOLD", "69")
        with pytest.raises(ValueError, match="between 70 and 80"):
            apply_threshold([])

    def test_env_var_above_80_raises_value_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MATCH_SCORE_THRESHOLD", "81")
        with pytest.raises(ValueError, match="between 70 and 80"):
            apply_threshold([])

    def test_env_var_non_integer_raises_value_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MATCH_SCORE_THRESHOLD", "seventy")
        with pytest.raises(ValueError, match="must be an integer"):
            apply_threshold([])

    def test_env_var_float_string_raises_value_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Float strings like '70.5' are not accepted; threshold must be an integer."""
        monkeypatch.setenv("MATCH_SCORE_THRESHOLD", "70.5")
        with pytest.raises(ValueError, match="must be an integer"):
            apply_threshold([])
