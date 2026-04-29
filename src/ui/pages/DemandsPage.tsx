import { useEffect, useMemo, useState } from "react";
import { getDemands } from "../api/client";
import type { DemandRecord } from "../types/api";
import DemandCard from "../components/DemandCard";
import KpiCards from "../components/KpiCards";

export default function DemandsPage() {
  const [demands, setDemands] = useState<DemandRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [search, setSearch] = useState("");
  const [filterSkill, setFilterSkill] = useState("all");
  const [filterLocation, setFilterLocation] = useState("all");
  const [filterWorkMode, setFilterWorkMode] = useState("all");
  const [sortBy, setSortBy] = useState<"role" | "location" | "start_date">("start_date");

  useEffect(() => {
    getDemands()
      .then(setDemands)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to load demands")
      )
      .finally(() => setLoading(false));
  }, []);

  // Derive filter options from loaded data
  const skills = useMemo(
    () => ["all", ...Array.from(new Set(demands.map((d) => d.essential_skill))).sort()],
    [demands]
  );
  const locations = useMemo(
    () => ["all", ...Array.from(new Set(demands.map((d) => d.location))).sort()],
    [demands]
  );

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return demands
      .filter((d) => {
        if (filterSkill !== "all" && d.essential_skill !== filterSkill) return false;
        if (filterLocation !== "all" && d.location !== filterLocation) return false;
        if (filterWorkMode !== "all" && d.work_mode !== filterWorkMode) return false;
        if (
          q &&
          !`${d.role_description} ${d.essential_skill} ${d.job_description} ${d.customer_name}`
            .toLowerCase()
            .includes(q)
        )
          return false;
        return true;
      })
      .slice()
      .sort((a, b) => {
        if (sortBy === "role") return a.role_description.localeCompare(b.role_description);
        if (sortBy === "location") return a.location.localeCompare(b.location);
        return a.start_date.localeCompare(b.start_date);
      });
  }, [demands, search, filterSkill, filterLocation, filterWorkMode, sortBy]);

  const kpis = [
    { label: "Total Demands", value: demands.length },
    { label: "Open Positions", value: demands.reduce((s, d) => s + d.open_positions, 0) },
    { label: "Showing", value: filtered.length },
    {
      label: "Onsite / Offshore",
      value: `${demands.filter((d) => d.work_mode === "ONSITE").length} / ${demands.filter((d) => d.work_mode === "OFFSHORE").length}`,
    },
  ];

  return (
    <div>
      <KpiCards items={kpis} />

      <div className="page-layout">
        <main>
          <div className="panel">
            {/* Filter bar */}
            <div
              style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 16 }}
              role="search"
              aria-label="Filter demands"
            >
              <input
                className="input"
                style={{ flex: 1, minWidth: 200 }}
                placeholder="Search demands…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                aria-label="Search demands"
              />

              <select
                className="select"
                value={filterSkill}
                onChange={(e) => setFilterSkill(e.target.value)}
                aria-label="Filter by skill"
              >
                {skills.map((s) => (
                  <option key={s} value={s}>
                    {s === "all" ? "All Skills" : s}
                  </option>
                ))}
              </select>

              <select
                className="select"
                value={filterLocation}
                onChange={(e) => setFilterLocation(e.target.value)}
                aria-label="Filter by location"
              >
                {locations.map((l) => (
                  <option key={l} value={l}>
                    {l === "all" ? "All Locations" : l}
                  </option>
                ))}
              </select>

              <select
                className="select"
                value={filterWorkMode}
                onChange={(e) => setFilterWorkMode(e.target.value)}
                aria-label="Filter by work mode"
              >
                <option value="all">All Modes</option>
                <option value="ONSITE">Onsite</option>
                <option value="OFFSHORE">Offshore</option>
              </select>

              <select
                className="select"
                value={sortBy}
                onChange={(e) =>
                  setSortBy(e.target.value as typeof sortBy)
                }
                aria-label="Sort demands"
              >
                <option value="start_date">Sort: Start Date</option>
                <option value="role">Sort: Role</option>
                <option value="location">Sort: Location</option>
              </select>
            </div>

            {/* Content */}
            {loading && (
              <div className="state-card" aria-busy="true">
                <div>Loading demands…</div>
              </div>
            )}

            {!loading && error && (
              <div className="state-card" role="alert">
                <div style={{ color: "var(--accent-danger)" }}>⚠ {error}</div>
                <div className="small muted">
                  Make sure the backend is running at http://localhost:8000
                </div>
              </div>
            )}

            {!loading && !error && filtered.length === 0 && (
              <div className="state-card">
                <div>No demands match the current filters.</div>
              </div>
            )}

            {!loading && !error && filtered.length > 0 && (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
                  gap: 12,
                }}
                role="list"
                aria-label="Demand records"
              >
                {filtered.map((d) => (
                  <div key={d.demand_id} role="listitem">
                    <DemandCard demand={d} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>

      </div>
    </div>
  );
}
