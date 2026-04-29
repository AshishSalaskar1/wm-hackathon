import { NavLink } from "react-router-dom";

const LOGO_STYLE: React.CSSProperties = {
  width: 44,
  height: 44,
  background: "linear-gradient(180deg, var(--primary), var(--primary-600))",
  color: "#fff",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontWeight: 700,
  borderRadius: 8,
  fontSize: "1.1rem",
  flexShrink: 0,
};

const HEADER_STYLE: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 16,
  justifyContent: "space-between",
  marginBottom: 20,
};

const BRAND_STYLE: React.CSSProperties = {
  display: "flex",
  gap: 12,
  alignItems: "center",
};

const NAV_STYLE: React.CSSProperties = {
  display: "flex",
  gap: 8,
  alignItems: "center",
};

export default function AppHeader() {
  return (
    <header style={HEADER_STYLE} aria-label="Application header">
      <div style={BRAND_STYLE}>
        <div style={LOGO_STYLE} aria-hidden="true">
          R
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: "1.05rem" }}>
            Recruitment Management System
          </div>
          <div className="small muted">Enterprise HR · Demand-Supply Matching</div>
        </div>
      </div>

      <nav style={NAV_STYLE} aria-label="Primary navigation">
        <NavLink
          to="/"
          end
          style={({ isActive }) => navLinkStyle(isActive)}
        >
          Demands
        </NavLink>
        {/* Supply Profiles — planned for a future sprint */}
        <span
          style={{
            ...navLinkStyle(false),
            opacity: 0.4,
            cursor: "not-allowed",
            pointerEvents: "none",
          }}
          aria-disabled="true"
          title="Coming soon"
        >
          Supply Profiles
        </span>
      </nav>
    </header>
  );
}

function navLinkStyle(isActive: boolean): React.CSSProperties {
  return {
    color: isActive ? "var(--primary)" : "var(--muted)",
    textDecoration: "none",
    padding: "6px 12px",
    borderRadius: 8,
    fontWeight: 600,
    fontSize: "0.9rem",
    background: isActive ? "rgba(36,52,143,0.06)" : "transparent",
  };
}
