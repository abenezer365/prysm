import { Link } from "react-router-dom";
export default function About() {
  const timeline = [
    [
      "Foundation",
      "Data readiness and a clear separation between operational and analytical concerns.",
    ],
    [
      "Temporal method",
      "Cutoff-aware labels and evaluation to reduce future-information leakage.",
    ],
    [
      "Graph evidence",
      "Bounded relationship context and GNN-oriented analysis.",
    ],
    [
      "Backend boundary",
      "Authentication, authorization, clearance, persistence, and service orchestration.",
    ],
    [
      "Human interface",
      "A research-led public knowledge system and controlled intelligence workspace.",
    ],
  ];
  return (
    <div className="shell py-16">
      <nav className="breadcrumb">
        <Link to="/">Home</Link>
        <span>/</span>
        <span>About</span>
      </nav>
      <header className="max-w-5xl">
        <p className="eyebrow">Institutional profile</p>
        <h1 className="page-title mt-5" tabIndex="-1">
          A project about making complex financial intelligence accountable.
        </h1>
        <p className="muted mt-7 max-w-3xl text-xl leading-8">
          Prysm was conceived around a practical gap: records describe events,
          but investigators need relationships, temporal context, evidence,
          model limits, and responsibility to remain visible together.
        </p>
      </header>
      <section className="mt-20 grid gap-14 border-y border-[var(--border)] py-14 lg:grid-cols-[.8fr_1.2fr]">
        <div>
          <p className="eyebrow">Origin</p>
          <h2 className="section-title mt-5">Why this problem?</h2>
        </div>
        <div className="article-body space-y-5">
          <p>
            Financial fraud and money laundering can involve fragmented
            transactions, changing behavior, indirect relationships, and heavy
            investigative workloads. A single rule or score cannot explain that
            whole environment.
          </p>
          <p>
            Prysm explores how graph context, model signals, evidence, and
            retrieved knowledge can support inquiry while keeping human judgment
            central. Explainability matters because an assessment that cannot be
            inspected cannot be responsibly challenged.
          </p>
          <p>
            The system distinguishes implemented research and software
            capabilities from future ambitions. It does not claim regulatory
            certification, universal detection, or autonomous decision-making.
          </p>
        </div>
      </section>
      <section className="py-20">
        <p className="eyebrow">Project philosophy</p>
        <h2 className="section-title mt-5">Ten principles shape the system.</h2>
        <div className="mt-12 grid border-l border-t border-[var(--border)] sm:grid-cols-2 lg:grid-cols-5">
          {[
            "Human oversight",
            "Evidence",
            "Provenance",
            "Explainability",
            "Privacy",
            "Access control",
            "Security",
            "Transparency",
            "Temporal discipline",
            "Research honesty",
          ].map((x, i) => (
            <div
              className="min-h-32 border-b border-r border-[var(--border)] p-5"
              key={x}
            >
              <span className="mono muted text-xs">
                {String(i + 1).padStart(2, "0")}
              </span>
              <h3 className="mt-8 font-semibold">{x}</h3>
            </div>
          ))}
        </div>
      </section>
      <section className="border-y border-[var(--border)] py-20">
        <p className="eyebrow">Project evolution</p>
        <h2 className="section-title mt-5">
          From data foundations to an intelligence workspace.
        </h2>
        <ol className="mt-12">
          {timeline.map(([t, d], i) => (
            <li
              className="grid gap-4 border-t border-[var(--border)] py-6 md:grid-cols-[90px_220px_1fr]"
              key={t}
            >
              <span className="mono muted">0{i + 1}</span>
              <h3 className="font-semibold">{t}</h3>
              <p className="muted max-w-2xl">{d}</p>
            </li>
          ))}
        </ol>
      </section>
      <section className="py-20">
        <div className="grid gap-12 lg:grid-cols-2">
          <div>
            <p className="eyebrow">Architectural philosophy</p>
            <h2 className="section-title mt-5">
              Separate responsibilities so each boundary can be inspected.
            </h2>
            <p className="muted mt-6 leading-7">
              The frontend presents information. The backend owns policy and
              trusted context. The AI Engine performs analytical work. The graph
              layer represents relationships. RAG retrieves knowledge and
              supports grounded explanation. Data pipelines preserve analytical
              readiness.
            </p>
            <Link className="knowledge-link mt-5" to="/docs/architecture">
              Open the architecture guide
            </Link>
          </div>
          <div className="mono border border-[var(--border)] bg-[var(--surface)] p-6 text-sm leading-10">
            <div>Browser interface</div>
            <div className="pl-5 text-[var(--muted)]">
              ↓ versioned backend boundary
            </div>
            <div>Policy · persistence · context</div>
            <div className="pl-5 text-[var(--muted)]">
              ↙ analysis　↓ graph　↘ retrieval
            </div>
            <div>AI Engine　Data　RAG</div>
          </div>
        </div>
      </section>
      <section className="border-t border-[var(--border)] py-20">
        <p className="eyebrow">Project builders</p>
        <h2 className="section-title mt-5">People and responsibilities</h2>
        <p className="muted mt-4">
          These profiles are intentionally explicit placeholders until the
          owners provide verified details.
        </p>
        <div className="mt-10 grid gap-8 md:grid-cols-2">
          {[1, 2].map((i) => (
            <article
              className="grid grid-cols-[120px_1fr] gap-6 border-t-4 border-[var(--accent)] bg-[var(--surface)] p-6"
              key={i}
            >
              <div className="grid aspect-[4/5] place-items-center bg-[var(--surface-2)] mono text-[var(--muted)]">
                PHOTO {i}
              </div>
              <div>
                <p className="eyebrow">Builder 0{i}</p>
                <h3 className="mt-3 text-xl font-semibold">
                  Verified name required
                </h3>
                <dl className="mt-5 text-sm">
                  <dt className="muted">Role</dt>
                  <dd>Editable project role</dd>
                  <dt className="muted mt-3">Contribution</dt>
                  <dd>Editable responsibilities and interests</dd>
                </dl>
              </div>
            </article>
          ))}
        </div>
      </section>
      <section className="grid gap-12 border-t border-[var(--border)] py-16 md:grid-cols-2">
        <div>
          <p className="eyebrow">Special thanks</p>
          <p className="muted mt-4 leading-7">
            Academic, technical, and community acknowledgements will be
            published only after names and affiliations are confirmed.
          </p>
          <Link className="knowledge-link mt-4" to="/about/acknowledgements">
            Acknowledgements note
          </Link>
        </div>
        <div>
          <p className="eyebrow">Future direction</p>
          <p className="muted mt-4 leading-7">
            Continue improving evaluation, explainability, feedback,
            accessibility, safe collaboration, and the bridge between research
            and responsible operation.
          </p>
          <Link className="knowledge-link mt-4" to="/contribute">
            How to contribute
          </Link>
        </div>
      </section>
    </div>
  );
}
