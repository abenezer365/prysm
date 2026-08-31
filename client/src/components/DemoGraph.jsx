import { useState } from "react";
const nodes = [
  {
    id: "selam",
    x: 47,
    y: 43,
    name: "Selam Tesfaye",
    type: "Person",
    role: "Finance manager",
    institution: "Blue Nile Imports PLC",
    risk: "Example behavioral variance under review",
  },
  {
    id: "dawit",
    x: 18,
    y: 21,
    name: "Dawit Bekele",
    type: "Person",
    role: "Director",
    institution: "Abay Logistics PLC",
    risk: "No standalone risk conclusion",
  },
  {
    id: "blue-nile",
    x: 77,
    y: 18,
    name: "Blue Nile Imports PLC",
    type: "Company",
    role: "Importer",
    institution: "Addis Ababa",
    risk: "Example transaction concentration",
  },
  {
    id: "abay-bank",
    x: 84,
    y: 58,
    name: "Abay Horizon Bank",
    type: "Bank",
    role: "Financial institution",
    institution: "Fictional institution",
    risk: "Institution shown for network context",
  },
  {
    id: "acct-2048",
    x: 59,
    y: 76,
    name: "Account ET-2048",
    type: "Account",
    role: "Business account",
    institution: "Abay Horizon Bank",
    risk: "Example rapid movement indicator",
  },
  {
    id: "meron",
    x: 22,
    y: 72,
    name: "Meron Alemu",
    type: "Person",
    role: "Authorized signatory",
    institution: "Blue Nile Imports PLC",
    risk: "Shared-account relationship",
  },
  {
    id: "sheba",
    x: 8,
    y: 48,
    name: "Sheba Trade Services",
    type: "Company",
    role: "Supplier",
    institution: "Dire Dawa",
    risk: "Example repeated counterparty",
  },
];
const edges = [
  [
    "selam",
    "dawit",
    "Professional contact",
    64,
    "Repeated business correspondence in this fictional dataset.",
  ],
  [
    "selam",
    "blue-nile",
    "Employed by",
    92,
    "Declared employment and signing authority.",
  ],
  [
    "blue-nile",
    "abay-bank",
    "Banks with",
    78,
    "Recurring institutional relationship.",
  ],
  [
    "abay-bank",
    "acct-2048",
    "Holds account",
    96,
    "The bank maintains this fictional account.",
  ],
  [
    "selam",
    "acct-2048",
    "Authorized user",
    88,
    "Example signing authority over the account.",
  ],
  [
    "meron",
    "acct-2048",
    "Authorized user",
    81,
    "A second fictional signatory shares account access.",
  ],
  ["meron", "sheba", "Director of", 86, "Declared director relationship."],
  [
    "sheba",
    "dawit",
    "Counterparty",
    57,
    "Moderate recurring transaction relationship.",
  ],
  [
    "blue-nile",
    "sheba",
    "Supplier",
    71,
    "Repeated invoice and payment pathway.",
  ],
].map((e, i) => ({
  id: `e${i}`,
  source: e[0],
  target: e[1],
  type: e[2],
  score: e[3],
  explanation: e[4],
}));
const colors = {
  Person: "var(--graph-person)",
  Company: "var(--graph-company)",
  Bank: "var(--graph-bank)",
  Account: "var(--graph-account)",
};
export default function DemoGraph() {
  const [selected, setSelected] = useState(nodes[0]),
    [hover, setHover] = useState();
  const map = new Map(nodes.map((n) => [n.id, n])),
    detail = hover || selected;
  return (
    <section
      className="demo-graph"
      aria-label="Interactive fictional relationship demonstration"
    >
      <header>
        <div>
          <p className="eyebrow">Safe demonstration dataset</p>
          <h3>Fictional relationship network</h3>
        </div>
        <span className="mono">
          Fictional ETB flows · {nodes.length} entities · {edges.length} links
        </span>
      </header>
      <div className="demo-graph-layout">
        <div className="demo-canvas">
          <svg
            viewBox="0 0 100 90"
            role="img"
            aria-label="Fictional network of Ethiopian people, companies, a bank, and an account"
          >
            {edges.map((e) => {
              const a = map.get(e.source),
                b = map.get(e.target);
              return (
                <g
                  key={e.id}
                  tabIndex="0"
                  role="button"
                  aria-label={`${e.type}, score ${e.score} out of 100`}
                  onFocus={() => setHover({ ...e, kind: "Relationship" })}
                  onBlur={() => setHover()}
                  onMouseEnter={() => setHover({ ...e, kind: "Relationship" })}
                  onMouseLeave={() => setHover()}
                  onClick={() => setSelected({ ...e, kind: "Relationship" })}
                >
                  <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} />
                  <text x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 1}>
                    {e.score}
                  </text>
                </g>
              );
            })}
            {nodes.map((n) => (
              <g
                key={n.id}
                tabIndex="0"
                role="button"
                aria-label={`${n.name}, ${n.type}`}
                className={detail?.id === n.id ? "selected" : ""}
                onFocus={() => setHover(n)}
                onBlur={() => setHover()}
                onMouseEnter={() => setHover(n)}
                onMouseLeave={() => setHover()}
                onClick={() => setSelected(n)}
              >
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={n.id === "selam" ? 5.3 : 4.2}
                  fill={colors[n.type]}
                />
                <text x={n.x} y={n.y + 8}>
                  {n.name}
                </text>
              </g>
            ))}
          </svg>
        </div>
        <aside aria-live="polite">
          {detail?.kind === "Relationship" ? (
            <>
              <p className="eyebrow">Relationship</p>
              <h4>{detail.type}</h4>
              <p className="score">
                {detail.score}
                <small>/100</small>
              </p>
              <p>{detail.explanation}</p>
              <dl>
                <dt>From</dt>
                <dd>{map.get(detail.source).name}</dd>
                <dt>To</dt>
                <dd>{map.get(detail.target).name}</dd>
              </dl>
            </>
          ) : (
            <>
              <p className="eyebrow">{detail.type}</p>
              <h4>{detail.name}</h4>
              <dl>
                <dt>Role or category</dt>
                <dd>{detail.role}</dd>
                <dt>Connected institution</dt>
                <dd>{detail.institution}</dd>
                <dt>Example context</dt>
                <dd>{detail.risk}</dd>
              </dl>
            </>
          )}
        </aside>
      </div>
      <footer>
        <div className="demo-legend">
          {Object.keys(colors).map((x) => (
            <span key={x}>
              <i style={{ background: colors[x] }} />
              {x}
            </span>
          ))}
        </div>
        <p>
          Scores describe example relationship strength, not guilt or legal
          risk.
        </p>
      </footer>
    </section>
  );
}
