import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getMatches } from "../api/client";
import type { MatchResult, MatchResultsResponse } from "../types/api";
import MatchResultCard from "../components/MatchResultCard";

export default function MatchResultsPage() {
  const { demandId } = useParams<{ demandId: string }>();
  const navigate = useNavigate();
  const id = Number(demandId);

  const [response, setResponse] = useState<MatchResultsResponse | null>(null);
  const [allResults, setAllResults] = useState<MatchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPage = useCallback(
    async (pageNum: number, append: boolean) => {
      try {
        const data = await getMatches(id, pageNum);
        setResponse(data);
        if (append) {
          setAllResults((prev) => [...prev, ...data.results]);
        } else {
          setAllResults(data.results);
        }
        // Use the explicit has_more field from the API response
        setHasMore(data.has_more);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load matches");
      }
    },
    [id]
  );

  useEffect(() => {
    setLoading(true);
    setAllResults([]);
    setPage(1);
    loadPage(1, false).finally(() => setLoading(false));
  }, [id, loadPage]);

  async function handleLoadMore() {
    const nextPage = page + 1;
    setLoadingMore(true);
    await loadPage(nextPage, true);
    setPage(nextPage);
    setLoadingMore(false);
  }

  const aboveThreshold = allResults.filter((r) => !r.below_threshold);
  const belowThreshold = allResults.filter((r) => r.below_threshold);

  return (
    <div>
      {/* Page header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 20,
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontWeight: 800, fontSize: "1.15rem" }}>
            Match Results — Demand SR-{String(id).padStart(3, "0")}
          </h2>
          {response && (
            <div className="small muted" style={{ marginTop: 4 }}>
              Status:{" "}
              <span
                style={{
                  fontWeight: 600,
                  color:
                    response.status === "READY"
                      ? "var(--accent-success)"
                      : response.status === "MATCHING_IN_PROGRESS"
                      ? "var(--accent-pending)"
                      : "var(--muted)",
                }}
              >
                {response.status}
              </span>
            </div>
          )}
        </div>
        <button
          className="btn ghost"
          onClick={() => navigate("/")}
          aria-label="Back to demands list"
        >
          ← Back to Demands
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="panel state-card" aria-busy="true">
          Loading match results…
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div className="panel state-card" role="alert">
          <div style={{ color: "var(--accent-danger)" }}>⚠ {error}</div>
          <div className="small muted">
            Make sure the backend is running at http://localhost:8000
          </div>
        </div>
      )}

      {/* Matching in progress */}
      {!loading && !error && response?.status === "MATCHING_IN_PROGRESS" && (
        <div className="panel state-card">
          <div style={{ color: "var(--accent-pending)", fontWeight: 600 }}>
            ⏳ Matching in progress
          </div>
          <div className="small muted">
            Results will appear once the matching engine completes. Refresh to check.
          </div>
        </div>
      )}

      {/* No results */}
      {!loading && !error && response?.status === "NO_RESULTS" && (
        <div className="panel state-card">
          <div>No candidates met the 70% similarity threshold for this demand.</div>
          <div className="small muted">
            Try broadening the demand requirements or check back after the supply index is
            refreshed.
          </div>
        </div>
      )}

      {/* Results */}
      {!loading && !error && response?.status === "READY" && (
        <div className="panel">
          {aboveThreshold.length === 0 && belowThreshold.length === 0 && (
            <div className="state-card">
              <div>No candidates found for this demand.</div>
            </div>
          )}

          {/* Above-threshold section */}
          {aboveThreshold.length > 0 && (
            <section aria-label="Top matched candidates">
              <h3
                style={{
                  fontWeight: 700,
                  fontSize: "0.95rem",
                  marginBottom: 12,
                  color: "var(--accent-success)",
                }}
              >
                Top Matches ({aboveThreshold.length})
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {aboveThreshold.map((r) => (
                  <MatchResultCard key={r.employee_id} result={r} />
                ))}
              </div>
            </section>
          )}

          {/* Below-threshold section (page 2+) */}
          {belowThreshold.length > 0 && (
            <section
              aria-label="Additional candidates below threshold"
              style={{ marginTop: 24 }}
            >
              <div
                style={{
                  borderTop: "2px dashed #e6e9f2",
                  paddingTop: 16,
                  marginBottom: 12,
                }}
              >
                <h3
                  style={{
                    fontWeight: 700,
                    fontSize: "0.95rem",
                    marginBottom: 4,
                    color: "var(--accent-pending)",
                  }}
                >
                  Additional Candidates — Below 70% Threshold ({belowThreshold.length})
                </h3>
                <p className="small muted" style={{ margin: 0 }}>
                  These profiles scored below the match threshold. Review with caution.
                </p>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {belowThreshold.map((r) => (
                  <MatchResultCard key={r.employee_id} result={r} />
                ))}
              </div>
            </section>
          )}

          {/* Load more */}
          {hasMore && (
            <div style={{ marginTop: 18, display: "flex", alignItems: "center", gap: 12 }}>
              <button
                className="btn ghost"
                onClick={handleLoadMore}
                disabled={loadingMore}
                aria-label="Load next batch of candidates"
              >
                {loadingMore ? "Loading…" : "Load More Candidates"}
              </button>
              <span className="small muted">
                Page {page} · smooth client-side pagination
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
