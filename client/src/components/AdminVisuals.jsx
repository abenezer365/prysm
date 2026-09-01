import { useEffect, useMemo, useRef, useState } from "react";
import { Minus, Plus, RotateCcw } from "lucide-react";

const palette = ["#00614c", "#175a91", "#9a650d", "#7a4ea3", "#a83b36"];
const number = new Intl.NumberFormat();

export function BarChart({
  data = [],
  labelKey = "name",
  valueKey = "count",
  empty = "No chart data is available yet.",
}) {
  const max = Math.max(1, ...data.map((x) => Number(x[valueKey]) || 0));
  if (!data.length)
    return <p className="muted p-8 text-center text-sm">{empty}</p>;
  return (
    <div
      className="space-y-4 p-5"
      role="img"
      aria-label={data.map((x) => `${x[labelKey]} ${x[valueKey]}`).join(", ")}
    >
      {data.map((x, i) => (
        <div key={x.code || x[labelKey]}>
          <div className="mb-1.5 flex justify-between gap-4 text-xs">
            <span>{x[labelKey]}</span>
            <strong className="mono">{number.format(x[valueKey])}</strong>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-[var(--surface-2)]">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${Math.max(3, ((Number(x[valueKey]) || 0) / max) * 100)}%`,
                background: palette[i % palette.length],
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export function DonutChart({
  data = [],
  labelKey = "label",
  valueKey = "value",
}) {
  const total = data.reduce((sum, x) => sum + (Number(x[valueKey]) || 0), 0);
  let offset = 0;
  const slices = data.map((x, i) => {
    const value = Number(x[valueKey]) || 0,
      start = offset;
    offset += total ? (value / total) * 100 : 0;
    return { ...x, start, end: offset, color: palette[i % palette.length] };
  });
  const gradient = slices.length
    ? `conic-gradient(${slices.map((x) => `${x.color} ${x.start}% ${x.end}%`).join(",")})`
    : "var(--surface-2)";
  return (
    <div className="grid items-center gap-6 p-5 sm:grid-cols-[150px_1fr]">
      <div
        className="relative mx-auto h-36 w-36 rounded-full"
        style={{ background: gradient }}
        role="img"
        aria-label={`${number.format(total)} total`}
      >
        <div className="absolute inset-6 grid place-items-center rounded-full bg-[var(--surface)] text-center">
          <span>
            <strong className="block text-xl">{number.format(total)}</strong>
            <small className="muted">total</small>
          </span>
        </div>
      </div>
      <div className="space-y-2">
        {slices.map((x) => (
          <div
            className="flex items-center justify-between gap-4 text-xs"
            key={x[labelKey]}
          >
            <span className="flex items-center gap-2">
              <i
                className="h-2.5 w-2.5 rounded-full"
                style={{ background: x.color }}
              />
              {x[labelKey]}
            </span>
            <strong className="mono">{number.format(x[valueKey])}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

function hash(text) {
  let h = 0;
  for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) | 0;
  return Math.abs(h);
}
export function NetworkGraph({ nodes = [], edges = [], onSelect }) {
  const [selected, setSelected] = useState(null),
    [hovered, setHovered] = useState(null),
    [view, setView] = useState({ x: 0, y: 0, scale: 1 });
  const drag = useRef(null),
    graphRef = useRef(null);
  const positioned = useMemo(
    () =>
      [...nodes].sort((a,b)=>Number(Boolean(b.isSubject))-Number(Boolean(a.isSubject))).map((n, i) => {
        const ring = i ? 1 + Math.floor((i - 1) / 10) : 0,
          index = i ? (i - 1) % 10 : 0,
          count = Math.min(10, Math.max(1, nodes.length - 1 - (ring - 1) * 10));
        const angle = (index / count) * Math.PI * 2 - (hash(n.id) % 20) / 100;
        return {
          ...n,
          x: i === 0 ? 400 : 400 + Math.cos(angle) * (120 + ring * 75),
          y: i === 0 ? 245 : 245 + Math.sin(angle) * (90 + ring * 55),
        };
      }),
    [nodes],
  );
  const map = new Map(positioned.map((n) => [n.id, n]));
  useEffect(() => {
    const graph = graphRef.current;
    if (!graph) return undefined;
    const handleWheel = (event) => {
      event.preventDefault();
      const amount = event.deltaY < 0 ? 0.12 : -0.12;
      setView((current) => ({
        ...current,
        scale: Math.min(2.5, Math.max(0.45, current.scale + amount)),
      }));
    };
    graph.addEventListener("wheel", handleWheel, { passive: false });
    return () => graph.removeEventListener("wheel", handleWheel);
  }, []);
  function choose(item, type) {
    const value = { ...item, kind: type };
    setSelected(value);
    onSelect?.(value);
  }
  if (!nodes.length) return null;
  const zoom = (amount) => setView((current) => ({ ...current, scale: Math.min(2.5, Math.max(.45, current.scale + amount)) }));
  const startDrag = (event) => {
    if (event.button !== 0) return;
    drag.current = { clientX: event.clientX, clientY: event.clientY, x: view.x, y: view.y };
    event.currentTarget.setPointerCapture(event.pointerId);
  };
  const moveDrag = (event) => {
    const origin = drag.current;
    if (!origin) return;
    const x = origin.x + event.clientX - origin.clientX,
      y = origin.y + event.clientY - origin.clientY;
    setView((current) => ({ ...current, x, y }));
  };
  const stopDrag = () => {
    drag.current = null;
  };
  return (
    <div className="relative overflow-hidden rounded-md border border-[var(--border)] bg-[var(--surface-2)]">
      <div className="absolute right-3 top-3 z-10 flex overflow-hidden rounded-md border border-[var(--border)] bg-[var(--surface)] shadow" aria-label="Graph zoom controls">
        <button className="p-2 hover:bg-[var(--surface-2)]" onClick={() => zoom(.2)} aria-label="Zoom in"><Plus size={17}/></button>
        <button className="border-x border-[var(--border)] p-2 hover:bg-[var(--surface-2)]" onClick={() => zoom(-.2)} aria-label="Zoom out"><Minus size={17}/></button>
        <button className="p-2 hover:bg-[var(--surface-2)]" onClick={() => setView({x:0,y:0,scale:1})} aria-label="Reset graph view"><RotateCcw size={16}/></button>
      </div>
      <svg
        ref={graphRef}
        className="h-[620px] w-full cursor-grab touch-none select-none active:cursor-grabbing"
        viewBox="0 0 800 490"
        onPointerDown={startDrag}
        onPointerMove={moveDrag}
        onPointerUp={stopDrag}
        onPointerCancel={stopDrag}
        onLostPointerCapture={stopDrag}
        role="img"
        aria-label={`Relationship graph with ${nodes.length} nodes and ${edges.length} edges`}
      >
        <defs>
          <pattern
            id="grid"
            width="28"
            height="28"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 28 0 L 0 0 0 28"
              fill="none"
              stroke="var(--border)"
              strokeWidth=".6"
            />
          </pattern>
        </defs>
        <rect width="800" height="490" fill="url(#grid)" />
        <g transform={`translate(${view.x} ${view.y}) scale(${view.scale})`} style={{transformOrigin:"400px 245px"}}>
        {edges.map((e, i) => {
          const a = map.get(e.sourceNodeId || e.source),
            b = map.get(e.targetNodeId || e.target);
          if (!a || !b) return null;
          const score = e.confidence ?? e.normalizedScore ?? e.score ?? e.weight;
          return (
            <g
              key={e.id || i}
              onMouseEnter={() => setHovered({ ...e, kind: "edge" })}
              onMouseLeave={() => setHovered(null)}
              onClick={(event) => { event.stopPropagation(); choose(e, "edge"); }}
              className="cursor-pointer"
            >
              <line
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke={
                  selected?.id === (e.id || i)
                    ? "var(--accent)"
                    : "var(--border-strong)"
                }
                strokeWidth={1.5 + (Number(score) || 0) * 2}
              />
              <text x={(a.x+b.x)/2} y={(a.y+b.y)/2-4} textAnchor="middle" fill="var(--muted)" fontSize="8">{String(e.label||e.type||e.edgeType||"related").slice(0,24)}</text>
              <title>
                {e.relationshipType || e.edgeType || "RELATED"}
                {score != null
                  ? ` · ${Math.round(Number(score) * (Number(score) <= 1 ? 100 : 1))}%`
                  : ""}
              </title>
            </g>
          );
        })}
        {positioned.map((n, i) => {
          const active = selected?.id === n.id || hovered?.id === n.id;
          return (
            <g
              key={n.id}
              transform={`translate(${n.x} ${n.y})`}
              onMouseEnter={() => setHovered({ ...n, kind: "node" })}
              onMouseLeave={() => setHovered(null)}
              onClick={(event) => { event.stopPropagation(); choose(n, "node"); }}
              className="cursor-pointer"
            >
              <circle
                r={n.isSubject ? 27 : active ? 19 : 16}
                fill={
                  ({Person:"var(--graph-person)",Company:"var(--graph-company)",Bank:"var(--graph-bank)",Account:"var(--graph-account)",Device:"var(--warning)",Invoice:"var(--accent)"})[n.nodeType||n.type] || palette[hash(n.nodeType || n.type || "entity") % palette.length]
                }
                stroke={n.isSubject?"var(--accent)":"var(--surface)"}
                strokeWidth={n.isSubject?"6":"4"}
              />
              <text y="3" textAnchor="middle" fill="white" fontSize="9" fontWeight="700">{({Person:"P",Company:"ORG",Bank:"BANK",Account:"AC",Device:"DEV",Invoice:"INV"})[n.nodeType||n.type]||"?"}</text>
              <text
                y={i === 0 ? 40 : 31}
                textAnchor="middle"
                fill="var(--text)"
                fontSize="10"
                fontFamily="var(--font-ui)"
              >
                {(n.displayLabel || n.label || n.externalKey || n.id).slice(
                  0,
                  22,
                )}
              </text>
              {(n.nodeType || n.type) === "Person" && (
                <text
                  y={i === 0 ? 52 : 42}
                  textAnchor="middle"
                  fill="var(--muted)"
                  fontSize="8"
                  fontFamily="var(--font-mono)"
                >
                  {n.sourceId || String(n.externalRef || n.id).replace("Person:", "")}
                </text>
              )}
              <title>
                {n.displayLabel || n.label || n.externalKey || n.id}
              </title>
            </g>
          );
        })}
        </g>
      </svg>
      {hovered && (
        <div className="pointer-events-none absolute left-3 top-3 max-w-xs rounded border border-[var(--border)] bg-[var(--surface)] p-3 text-xs shadow">
          <strong>
            {hovered.displayLabel ||
              hovered.label ||
              hovered.relationshipType ||
              hovered.edgeType ||
              hovered.id}
          </strong>
          <p className="muted mt-1">
            {hovered.kind === "node"
              ? hovered.nodeType || hovered.type || "ENTITY"
              : `${hovered.sourceNodeId || hovered.source} → ${hovered.targetNodeId || hovered.target}`}
          </p>
          {hovered.kind === "node" && <p className="mono mt-1 break-all">{hovered.sourceId || hovered.externalRef || hovered.id}</p>}
        </div>
      )}
      <p className="pointer-events-none absolute bottom-3 left-3 rounded bg-[var(--surface)]/90 px-2 py-1 text-[10px] text-[var(--muted)]">Drag to pan · scroll or use + / − to zoom · {Math.round(view.scale * 100)}%</p>
    </div>
  );
}
