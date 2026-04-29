interface KpiItem {
  label: string;
  value: string | number;
  color?: string;
}

interface KpiCardsProps {
  items: KpiItem[];
}

export default function KpiCards({ items }: KpiCardsProps) {
  return (
    <section
      style={{ display: "flex", gap: 16, flexWrap: "wrap", margin: "18px 0 22px" }}
      aria-label="Key performance indicators"
    >
      {items.map((item) => (
        <div
          key={item.label}
          className="panel"
          style={{ minWidth: 170, flex: "1 1 170px" }}
        >
          <div className="small muted">{item.label}</div>
          <div
            style={{
              fontWeight: 700,
              fontSize: "1.6rem",
              marginTop: 6,
              color: item.color ?? "var(--text)",
            }}
          >
            {item.value}
          </div>
        </div>
      ))}
    </section>
  );
}
