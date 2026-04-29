import { useNavigate } from "react-router-dom";
import type { DemandRecord } from "../types/api";

interface DemandCardProps {
  demand: DemandRecord;
}

function workModeChip(mode: string) {
  const isOnsite = mode === "ONSITE";
  return (
    <span
      className={`chip ${isOnsite ? "chip-open" : "chip-hold"}`}
      title={`Work mode: ${mode}`}
    >
      {mode}
    </span>
  );
}

export default function DemandCard({ demand }: DemandCardProps) {
  const navigate = useNavigate();

  function handleViewMatches() {
    navigate(`/demands/${demand.demand_id}/matches`);
  }

  return (
    <article
      className="panel"
      style={{
        border: "1px solid #eef2ff",
        cursor: "default",
        display: "flex",
        flexDirection: "column",
        gap: 10,
        background: "linear-gradient(180deg, #fff, #fbfdff)",
        transition: "transform .14s ease, box-shadow .14s ease",
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLElement).style.transform = "translateY(-3px)";
        (e.currentTarget as HTMLElement).style.boxShadow =
          "0 10px 28px rgba(36,52,143,0.07)";
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLElement).style.transform = "";
        (e.currentTarget as HTMLElement).style.boxShadow = "";
      }}
      aria-label={`Demand: ${demand.role_description}`}
    >
      {/* Header row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
        <div>
          <div style={{ fontWeight: 700, fontSize: "1rem" }}>
            {demand.role_description}
          </div>
          <div className="small muted" style={{ marginTop: 2 }}>
            {demand.customer_name} · {demand.role_cluster}
          </div>
        </div>
        {workModeChip(demand.work_mode)}
      </div>

      {/* Attributes */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 6,
          fontSize: "0.82rem",
          color: "var(--muted)",
        }}
      >
        <span title="Required skill">
          <strong style={{ color: "var(--text)" }}>Skill:</strong>{" "}
          {demand.essential_skill}
        </span>
        <span>·</span>
        <span title="Location">
          {demand.location}, {demand.country}
        </span>
        <span>·</span>
        <span title="Band">{demand.band}</span>
        <span>·</span>
        <span title="Open positions">
          {demand.open_positions} position{demand.open_positions !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Job description excerpt */}
      <p
        className="small muted"
        style={{
          margin: 0,
          display: "-webkit-box",
          WebkitBoxOrient: "vertical",
          WebkitLineClamp: 2,
          overflow: "hidden",
        }}
      >
        {demand.job_description}
      </p>

      {/* Footer */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginTop: 4,
        }}
      >
        <div className="small muted">Start: {demand.start_date}</div>
        <button
          className="btn"
          onClick={handleViewMatches}
          aria-label={`View matches for demand ${demand.demand_id}`}
        >
          View Matches
        </button>
      </div>
    </article>
  );
}
