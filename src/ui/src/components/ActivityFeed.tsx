import { useEffect, useRef, useState } from "react";

/**
 * Safely renders feed text that may contain `<strong>token</strong>` segments.
 * Avoids dangerouslySetInnerHTML by splitting on the known pattern.
 */
function FeedText({ text }: { text: string }) {
  const parts = text.split(/(<strong>[^<]*<\/strong>)/g);
  return (
    <>
      {parts.map((part, i) => {
        const match = part.match(/^<strong>([^<]*)<\/strong>$/);
        return match ? <strong key={i}>{match[1]}</strong> : part;
      })}
    </>
  );
}

interface FeedItem {
  id: number;
  text: string;
  ts: string;
}

/** Simulated activity feed — replaced by real WebSocket/SSE in Sprint 3. */
export default function ActivityFeed() {
  const [items, setItems] = useState<FeedItem[]>([]);
  const counterRef = useRef(0);

  useEffect(() => {
    const TEMPLATES = [
      "Demand <strong>SR-001</strong> matched — 2 candidates above threshold",
      "Employee <strong>EMP-00001</strong> profile updated in supply index",
      "New demand <strong>SR-004</strong> published — matching queued",
      "Employee <strong>EMP-00003</strong> profile added to AI Search index",
      "Demand <strong>SR-002</strong> re-indexed after JD modification",
    ];

    function push() {
      const id = ++counterRef.current;
      const text = TEMPLATES[id % TEMPLATES.length];
      const ts = new Date().toLocaleTimeString();
      setItems((prev) => [{ id, text, ts }, ...prev].slice(0, 50));
    }

    // Seed with one item immediately
    push();
    const timer = setInterval(push, 4000);
    return () => clearInterval(timer);
  }, []);

  return (
    <aside className="panel" aria-label="Activity feed">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <div style={{ fontWeight: 700 }}>Activity Feed</div>
        <div className="small muted">Simulated · Real-time in Sprint 3</div>
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 8,
          maxHeight: 540,
          overflowY: "auto",
        }}
        role="log"
        aria-live="polite"
        aria-atomic="false"
      >
        {items.map((item) => (
          <div
            key={item.id}
            style={{
              padding: "10px 12px",
              borderRadius: 8,
              background: "linear-gradient(180deg, #fff, #fbfdff)",
              border: "1px solid #eef2ff",
              fontSize: "0.88rem",
            }}
          >
            <div style={{ lineHeight: 1.45 }}>
              <FeedText text={item.text} />
            </div>
            <div className="small muted" style={{ marginTop: 4 }}>
              {item.ts}
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}
