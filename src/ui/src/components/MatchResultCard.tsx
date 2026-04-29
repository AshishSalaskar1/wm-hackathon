import type { MatchResult } from "../types/api";

interface MatchResultCardProps {
  result: MatchResult;
}

function initials(name: string): string {
  return name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

function scoreClass(score: number, belowThreshold: boolean): string {
  if (belowThreshold) return "below";
  if (score >= 80) return "high";
  return "";
}

export default function MatchResultCard({ result }: MatchResultCardProps) {
  const badgeClass = scoreClass(result.similarity_score, result.below_threshold);

  return (
    <article
      style={{
        display: "flex",
        gap: 14,
        alignItems: "flex-start",
        padding: "12px 14px",
        borderRadius: 10,
        background: "linear-gradient(180deg, #fff, #fbfdff)",
        border: result.below_threshold ? "1px solid #fef3c7" : "1px solid #eef2ff",
        transition: "transform .12s ease",
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLElement).style.transform = "translateY(-3px)";
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLElement).style.transform = "";
      }}
      aria-label={`Rank ${result.rank}: ${result.employee_name}`}
    >
      {/* Rank badge */}
      <div
        style={{
          minWidth: 28,
          height: 28,
          borderRadius: 6,
          background: "var(--bg)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontWeight: 700,
          fontSize: "0.85rem",
          color: "var(--primary)",
          flexShrink: 0,
        }}
        aria-label={`Rank ${result.rank}`}
      >
        #{result.rank}
      </div>

      {/* Avatar */}
      <div
        style={{
          width: 48,
          height: 48,
          borderRadius: 10,
          background: "#eef2ff",
          color: "var(--primary)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontWeight: 700,
          fontSize: "0.95rem",
          flexShrink: 0,
        }}
        aria-hidden="true"
      >
        {initials(result.employee_name)}
      </div>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Name row */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 8,
            flexWrap: "wrap",
          }}
        >
          <span style={{ fontWeight: 600 }}>{result.employee_name}</span>
          <span
            className={`score-badge ${badgeClass}`}
            title={`Similarity score: ${result.similarity_score}%`}
            aria-label={`${result.similarity_score}% similarity`}
          >
            {result.similarity_score}%
          </span>
        </div>

        {/* Subtitle */}
        <div className="small muted" style={{ marginTop: 2 }}>
          {result.role_name ?? "No role"} · {result.band} · {result.location} ·{" "}
          {result.work_mode}
        </div>

        {/* Score bar */}
        <div style={{ margin: "8px 0 4px" }}>
          <div
            className="score-bar-track"
            role="progressbar"
            aria-valuenow={result.similarity_score}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Match score: ${result.similarity_score}%`}
          >
            <div
              className="score-bar-fill"
              style={{ width: `${result.similarity_score}%` }}
            />
          </div>
        </div>

        {/* Skills */}
        {result.skills_iaspire && (
          <div className="small muted">
            <strong style={{ color: "var(--text)" }}>Skills:</strong>{" "}
            {result.skills_iaspire}
          </div>
        )}

        {/* Experience + below-threshold flag */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: 6,
            flexWrap: "wrap",
            gap: 4,
          }}
        >
          <span className="small muted">Exp: {result.experience}</span>
          {result.below_threshold && (
            <span
              style={{
                fontSize: "0.75rem",
                fontWeight: 600,
                color: "var(--accent-pending)",
                background: "#fff7ed",
                padding: "2px 8px",
                borderRadius: 999,
              }}
            >
              Below 70% threshold
            </span>
          )}
        </div>
      </div>
    </article>
  );
}
