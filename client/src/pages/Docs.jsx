import { Link } from "react-router-dom";
import { docPages } from "../config/publicRegistry";
const endpoints = [
  ["GET", "/health", "Public", "Process liveness"],
  ["POST", "/applications", "Public", "Request controlled access"],
  ["POST", "/auth/login", "Public", "Start a session"],
  ["POST", "/chat/public", "Public", "Knowledge-only answer"],
  ["GET", "/auth/me", "Authenticated", "Safe current identity"],
  ["POST", "/search", "subject:read", "Authorized subject discovery"],
  ["GET", "/subjects/:id", "subject:read", "Redacted subject summary"],
  ["GET", "/investigations", "investigation:read", "Owned or shared cases"],
  [
    "POST",
    "/investigations/:id/analyze",
    "investigation:analyze",
    "Run bounded analysis",
  ],
  [
    "GET",
    "/graph/subjects/:id/subgraph",
    "graph:read",
    "Bounded relationship graph",
  ],
  [
    "POST",
    "/chat/authorized",
    "chat:authorized",
    "Investigation-grounded answer",
  ],
  ["GET", "/models", "model:read", "Safe registry metadata"],
];
export default function Docs() {
  return (
    <div className="shell py-16">
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <span>/</span>
        <span>Documentation</span>
      </nav>
      <header className="max-w-4xl">
        <p className="eyebrow">Technical documentation / v1</p>
        <h1 className="page-title mt-5" tabIndex="-1">
          Understand Prysm from browser to evidence.
        </h1>
        <p className="muted mt-7 text-xl leading-8">
          A public technical guide to architecture, application flow, data,
          authorization, graph intelligence, retrieval, models, and failure
          handling.
        </p>
      </header>
      <div className="mt-14 grid gap-px border border-[var(--border)] bg-[var(--border)] sm:grid-cols-2 lg:grid-cols-4">
        {Object.entries(docPages).map(([path, [title, description]]) => (
          <Link
            className="bg-[var(--surface)] p-5 hover:bg-[var(--surface-2)]"
            to={path}
            key={path}
          >
            <h2 className="font-semibold">{title}</h2>
            <p className="muted mt-3 line-clamp-3 text-sm leading-6">
              {description}
            </p>
            <span className="mt-5 block text-sm text-[var(--link)] underline">
              Open guide
            </span>
          </Link>
        ))}
      </div>
      <section className="mt-20 grid gap-12 lg:grid-cols-[260px_1fr]">
        <div>
          <p className="eyebrow">System overview</p>
          <h2 className="mt-4 text-2xl font-semibold">
            Responsibility by layer
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="institutional-table">
            <thead>
              <tr>
                <th>Layer</th>
                <th>Responsibility</th>
                <th>Boundary</th>
              </tr>
            </thead>
            <tbody>
              {[
                [
                  "Frontend",
                  "Navigation, presentation, local interaction",
                  "Never authoritative for access",
                ],
                [
                  "Backend",
                  "Identity, policy, ownership, persistence, trusted context",
                  "Only browser service boundary",
                ],
                [
                  "AI Engine",
                  "Risk and graph analysis",
                  "Receives backend-built context",
                ],
                [
                  "RAG",
                  "Knowledge retrieval and grounded explanation",
                  "No direct browser access",
                ],
                [
                  "PostgreSQL",
                  "Operational records and audit state",
                  "Backend mediated",
                ],
                [
                  "Analytical data",
                  "Prepared model and graph inputs",
                  "Versioned and cutoff-aware",
                ],
              ].map((r) => (
                <tr key={r[0]}>
                  {r.map((x) => (
                    <td key={x}>{x}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="mt-20 border-y border-[var(--border)] py-16">
        <p className="eyebrow">Application flow</p>
        <div className="mono mt-8 overflow-x-auto bg-[var(--surface-2)] p-6 text-sm leading-10 text-[var(--text)]">
          Visitor → public knowledge → access request → review
          <br />→ authentication → live authorization → intelligence workspace
          <br />→ investigation → bounded analysis → evidence → grounded
          explanation
        </div>
        <p className="muted mt-5">
          Application review is enforced by the backend. Authorized reviewers
          can approve or reject a pending request, record a decision note, and
          provision controlled access without exposing bootstrap operations.
        </p>
      </section>
      <section className="mt-20">
        <p className="eyebrow">Frontend API contract</p>
        <h2 className="section-title mt-5">Representative endpoints</h2>
        <p className="muted mt-5">
          Exact schemas and all clearance requirements remain in BACKEND_API.md
          and the OpenAPI document.
        </p>
        <div className="mt-8 overflow-x-auto">
          <table className="institutional-table">
            <thead>
              <tr>
                <th>Method</th>
                <th>Route</th>
                <th>Access</th>
                <th>Purpose</th>
              </tr>
            </thead>
            <tbody>
              {endpoints.map((r) => (
                <tr key={r[1]}>
                  {r.map((x, i) => (
                    <td className={i < 2 ? "mono" : ""} key={x}>
                      {x}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="mt-20 grid gap-12 border-t border-[var(--border)] pt-16 lg:grid-cols-2">
        <div>
          <p className="eyebrow">Data flow</p>
          <h2 className="mt-4 text-2xl font-semibold">
            From records to explanation
          </h2>
          <ol className="mt-6 space-y-3 text-sm">
            {[
              "Raw source records",
              "Validation and temporal processing",
              "Operational and analytical storage",
              "Graph context and model output",
              "Investigation findings and evidence",
              "RAG context and source-grounded answer",
            ].map((x, i) => (
              <li
                className="flex gap-4 border-b border-[var(--border)] pb-3"
                key={x}
              >
                <span className="mono muted">{i + 1}</span>
                {x}
              </li>
            ))}
          </ol>
        </div>
        <div>
          <p className="eyebrow">Start reading</p>
          <div className="related-links mt-5">
            <Link to="/docs/architecture">Architecture</Link>
            <Link to="/docs/authentication">Authentication and sessions</Link>
            <Link to="/docs/security">Authorization and security</Link>
            <Link to="/docs/chat">Public and authorized chat</Link>
            <Link to="/docs/investigations">Investigation system</Link>
            <Link to="/docs/errors">Errors and request IDs</Link>
            <Link to="/docs/glossary">Glossary</Link>
            <Link to="/faq">Frequently asked questions</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
