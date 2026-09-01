import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  BookOpen,
  Check,
  Database,
  FileSearch,
  LockKeyhole,
  Network,
  Scale,
  Search,
} from "lucide-react";
import DemoGraph from "../components/DemoGraph";
import NewsFeed from "../components/NewsFeed";
const steps = [
  ["01", "Find", "Search authorized, redacted subject summaries."],
  ["02", "Frame", "Create a purpose-bound investigation and temporal cutoff."],
  ["03", "Analyze", "Review bounded model and relationship context."],
  ["04", "Verify", "Trace findings to evidence and source provenance."],
  ["05", "Assess", "Record a human interpretation with limitations."],
];

function HeroGraph() {
  const definitions = [
    ["Institution", -Math.PI / 2, 138, 0.82],
    ["Persons", -Math.PI / 2 + Math.PI * .4, 140, 1.08],
    ["Accounts", -Math.PI / 2 + Math.PI * .8, 136, .92],
    ["Organization", -Math.PI / 2 + Math.PI * 1.2, 139, 1.15],
    ["Business", -Math.PI / 2 + Math.PI * 1.6, 137, .98],
  ];
  const calculate = (time = 0) => {
    const center = { x: 260 + Math.sin(time * .19) * 2.2, y: 190 + Math.cos(time * .16) * 1.8 };
    const nodes = definitions.map(([label, baseAngle, radius, weight], index) => {
      const phase = index * 1.37;
      const angle = baseAngle + Math.sin(time * .13 * weight + phase) * .025;
      const weightedRadius = radius + Math.sin(time * .21 * weight + phase) * (2.4 + weight);
      return { label, x: center.x + Math.cos(angle) * weightedRadius, y: center.y + Math.sin(angle) * weightedRadius };
    });
    return { center, nodes };
  };
  const [network, setNetwork] = useState(() => calculate());
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return undefined;
    let frame, last = 0;
    const move = (now) => {
      if (now - last > 32) { setNetwork(calculate(now / 1000)); last = now; }
      frame = requestAnimationFrame(move);
    };
    frame = requestAnimationFrame(move);
    return () => cancelAnimationFrame(frame);
  }, []);
  const ringEdges = network.nodes.map((node, index) => [node, network.nodes[(index + 1) % network.nodes.length]]);
  const edgePath = (a, b) => `M ${a.x} ${a.y} L ${b.x} ${b.y}`;
  return (
    <figure className="hero-graph" aria-labelledby="hero-graph-caption">
      <svg
        viewBox="0 0 520 380"
        role="img"
        aria-label="A person connected to an institution, persons, accounts, organization, and business"
      >
        <g className="hero-graph-edges">
          {network.nodes.map((node, index) => <path key={`spoke-${node.label}`} d={edgePath(network.center,node)}><title>Person to {node.label}</title></path>)}
          {ringEdges.map(([from,to]) => <path className="relationship-ring" key={`${from.label}-${to.label}`} d={edgePath(from,to)}><title>{from.label} to {to.label}</title></path>)}
        </g>
        <g className="hero-graph-flow" aria-hidden="true">
          {network.nodes.map((node,index)=><circle r="2.5" key={`flow-${node.label}`}><animateMotion path={edgePath(network.center,node)} dur={`${3.2+index*.37}s`} begin={`${index*-.61}s`} repeatCount="indefinite"/></circle>)}
          {ringEdges.map(([from,to],index)=><circle r="2.1" key={`ring-flow-${from.label}`}><animateMotion path={edgePath(from,to)} dur={`${4.4+index*.31}s`} begin={`${index*-.73}s`} repeatCount="indefinite"/></circle>)}
        </g>
        <g className="hero-graph-nodes">
          <g className="node-person" transform={`translate(${network.center.x} ${network.center.y})`}><circle r="40"/><text className="node-core-label" y="5">Person</text></g>
          {network.nodes.map((node,index)=><g className={`node-related node-related-${index+1}`} transform={`translate(${node.x} ${node.y})`} key={node.label}><circle r="30"/><text y="50">{node.label}</text></g>)}
        </g>
      </svg>
      <figcaption id="hero-graph-caption">
        A living view of financial relationships.
      </figcaption>
    </figure>
  );
}
export default function Home() {
  return (
    <>
      <section className="home-hero">
        <div className="shell home-hero-layout">
          <div className="home-hero-copy">
            <p className="home-hero-quote">
              “Follow the evidence. See the whole.”
            </p>
            <h1 tabIndex="-1">Understand risk through what connects.</h1>
            <p className="home-hero-brand">Prysm Intelligence</p>
            <Link
              to="/request-access"
              className="button button-primary home-hero-cta"
            >
              Start using Prysm <ArrowRight size={17} />
            </Link>
          </div>
          <HeroGraph />
        </div>
      </section>
      <section className="border-y border-[var(--border)] bg-[var(--surface)]">
        <div className="shell grid gap-0 lg:grid-cols-[.85fr_1.15fr]">
          <div className="border-b border-[var(--border)] py-16 pr-10 lg:border-b-0 lg:border-r">
            <p className="eyebrow">What Prysm is</p>
            <h2 className="section-title mt-5">
              An information system for accountable inquiry.
            </h2>
          </div>
          <div className="grid gap-8 py-16 lg:pl-14">
            <p className="article-body !text-xl">
              Financial records often arrive as isolated rows, alerts, and
              reports. Investigators need a coherent view of time, behavior,
              relationships, evidence, and analytical limits.
            </p>
            <p className="muted leading-7">
              Prysm connects those views around an authorized case. It is not an
              autonomous authority and does not claim to determine criminal
              behavior.
            </p>
            <div className="flex flex-wrap gap-x-8 gap-y-3 text-sm">
              {[
                "Evidence-aware",
                "Graph-capable",
                "Permission-controlled",
                "Source-grounded",
              ].map((x) => (
                <span className="flex items-center gap-2" key={x}>
                  <Check size={15} className="text-[var(--accent)]" />
                  {x}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>
      <section className="shell py-[var(--space-section)]">
        <div className="grid gap-14 lg:grid-cols-2">
          <div>
            <p className="eyebrow">The problem</p>
            <h2 className="section-title mt-5">
              Rules see events. Investigations need context.
            </h2>
            <p className="article-body muted mt-7">
              Conventional rules are valuable for explicit conditions, but
              complex activity can involve changing behavior, indirect
              relationships, repeated pathways, and temporal patterns. More
              context can improve prioritization, yet it also increases the risk
              of over-interpretation.
            </p>
            <Link
              className="knowledge-link mt-6"
              to="/research/fraud-detection"
            >
              Read the fraud detection research note
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="institutional-table">
              <thead>
                <tr>
                  <th>View</th>
                  <th>Useful for</th>
                  <th>Important limitation</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Rule</td>
                  <td>Known conditions</td>
                  <td>Can be rigid</td>
                </tr>
                <tr>
                  <td>Behavior</td>
                  <td>Change over time</td>
                  <td>Difference needs context</td>
                </tr>
                <tr>
                  <td>Graph</td>
                  <td>Connected structure</td>
                  <td>Proximity is not guilt</td>
                </tr>
                <tr>
                  <td>Model</td>
                  <td>Pattern prioritization</td>
                  <td>Errors and drift remain</td>
                </tr>
                <tr>
                  <td>Human review</td>
                  <td>Purpose and judgment</td>
                  <td>Requires time and evidence</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
      <section className="bg-[#e7eee5] py-[var(--space-section)] text-[#18221d]">
        <div className="shell">
          <p className="eyebrow">Investigation workflow</p>
          <h2 className="section-title mt-5 max-w-3xl">
            A repeatable line from question to assessment.
          </h2>
          <ol className="mt-14 grid border-y border-[#bdcabc] md:grid-cols-5">
            {steps.map(([n, t, d]) => (
              <li
                className="border-b border-[#bdcabc] p-5 last:border-b-0 md:border-b-0 md:border-r md:last:border-r-0"
                key={n}
              >
                <span className="font-mono text-xs text-[#55705d]">{n}</span>
                <h3 className="mt-8 font-semibold">{t}</h3>
                <p className="mt-3 text-sm leading-6 text-[#556159]">{d}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>
      <section className="shell grid gap-16 py-[var(--space-section)] lg:grid-cols-[1fr_1.2fr]">
        <div>
          <p className="eyebrow">Three analytical lenses</p>
          <h2 className="section-title mt-5">
            Different views answer different questions.
          </h2>
        </div>
        <div className="divide-y divide-[var(--border)] border-y border-[var(--border)]">
          {[
            [
              Database,
              "Transaction intelligence",
              "What happened, when, between which parties, and with what provenance?",
              "/research/transaction-intelligence",
            ],
            [
              Search,
              "Behavioral intelligence",
              "How does activity differ from a meaningful historical expectation?",
              "/research/behavioral-intelligence",
            ],
            [
              Network,
              "Graph intelligence",
              "Which typed relationships and structures surround an entity?",
              "/research/network-intelligence",
            ],
          ].map(([I, t, d, p]) => (
            <article className="grid grid-cols-[40px_1fr] gap-4 py-7" key={t}>
              <I className="text-[var(--accent)]" size={21} />
              <div>
                <h3 className="font-semibold">{t}</h3>
                <p className="muted mt-2 leading-7">{d}</p>
                <Link className="knowledge-link mt-3 text-sm" to={p}>
                  Read the research note
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>
      <section className="border-y border-[var(--border)] bg-[var(--surface)] py-[var(--space-section)]">
        <div className="shell grid gap-12 lg:grid-cols-3">
          <article>
            <Scale className="text-[var(--accent)]" />
            <h2 className="mt-5 text-2xl font-semibold">Ethics</h2>
            <p className="muted mt-4 leading-7">
              Signals are not verdicts. False positives and false negatives
              require explicit review.
            </p>
            <Link className="knowledge-link mt-4" to="/research/ethical-ai">
              Ethical AI framework
            </Link>
          </article>
          <article>
            <Database className="text-[var(--accent)]" />
            <h2 className="mt-5 text-2xl font-semibold">Provenance</h2>
            <p className="muted mt-4 leading-7">
              Sources, transformations, snapshots, versions, and cutoff times
              make assessment reproducible.
            </p>
            <Link
              className="knowledge-link mt-4"
              to="/research/data-provenance"
            >
              Data provenance
            </Link>
          </article>
          <article>
            <LockKeyhole className="text-[var(--accent)]" />
            <h2 className="mt-5 text-2xl font-semibold">Security</h2>
            <p className="muted mt-4 leading-7">
              The backend enforces identity, permission, clearance, ownership,
              and resource boundaries.
            </p>
            <Link className="knowledge-link mt-4" to="/docs/security">
              Security architecture
            </Link>
          </article>
        </div>
      </section>
      <section className="shell py-[var(--space-section)]">
        <div className="grid gap-12 lg:grid-cols-2">
          <div>
            <p className="eyebrow">Relationship demonstration</p>
            <h2 className="section-title mt-5">
              A graph is a map of context, not a map of guilt.
            </h2>
            <p className="muted mt-6 leading-7">
              This interactive orientation graphic uses synthetic data. In the
              application, graph queries are bounded by subject, cutoff, hop
              count, node count, permission, and clearance.
            </p>
            <Link className="knowledge-link mt-5" to="/intelligence/graph">
              Learn how to read graph intelligence
            </Link>
          </div>
          <DemoGraph />
        </div>
      </section>
      <section className="bg-[#173f2c] py-[var(--space-section)] text-white">
        <div className="shell grid gap-14 lg:grid-cols-3">
          <div>
            <BookOpen />
            <h2 className="mt-5 text-2xl font-semibold">Research library</h2>
            <p className="mt-4 text-white/70">
              Explore methodology, ethics, AML, evaluation, explainability, and
              graph research.
            </p>
            <Link className="mt-5 block underline" to="/research">
              Browse research
            </Link>
          </div>
          <div>
            <FileSearch />
            <h2 className="mt-5 text-2xl font-semibold">
              Technical documentation
            </h2>
            <p className="mt-4 text-white/70">
              Understand architecture, APIs, data flow, security, chat, and
              error handling.
            </p>
            <Link className="mt-5 block underline" to="/docs">
              Open documentation
            </Link>
          </div>
          <div>
            <Network />
            <h2 className="mt-5 text-2xl font-semibold">Academy</h2>
            <p className="mt-4 text-white/70">
              Build foundations in data science, Python, machine learning, and
              financial intelligence.
            </p>
            <Link className="mt-5 block underline" to="/academy">
              Visit Academy
            </Link>
          </div>
        </div>
      </section>
      <section className="shell py-[var(--space-section)]">
        <div className="grid gap-12 lg:grid-cols-2">
          <div>
            <p className="eyebrow">Questions</p>
            <h2 className="section-title mt-5">
              Understand the boundary before requesting access.
            </h2>
            <Link className="knowledge-link mt-6" to="/faq">
              Read all frequently asked questions
            </Link>
          </div>
          <div className="divide-y divide-[var(--border)] border-y border-[var(--border)]">
            {[
              [
                "Does Prysm decide guilt?",
                "No. It supports authorized human investigation.",
              ],
              [
                "Is public demo data real?",
                "No. Public demonstrations are synthetic.",
              ],
              [
                "Why is access reviewed?",
                "The application is designed for controlled intelligence work.",
              ],
            ].map(([q, a]) => (
              <details className="py-5" key={q}>
                <summary className="cursor-pointer font-semibold">{q}</summary>
                <p className="muted mt-3">{a}</p>
              </details>
            ))}
          </div>
        </div>
        <div className="mt-24 border-l-4 border-[var(--accent)] bg-[var(--surface)] p-8 md:p-12">
          <p className="eyebrow">Controlled beta</p>
          <h2 className="section-title mt-4 max-w-3xl">
            Explore the research. Request the workspace when the purpose is
            clear.
          </h2>
          <div className="mt-7 flex flex-wrap gap-5">
            <Link className="button button-primary" to="/request-access">
              Request access
            </Link>
            <Link className="knowledge-link self-center" to="/beta">
              How beta participation works
            </Link>
          </div>
        </div>
      </section>
      <section className="border-b border-[var(--border)] bg-[var(--surface)] py-[var(--space-section)]">
        <div className="shell">
          <div className="mb-10 flex items-end justify-between gap-6"><div><p className="eyebrow">Latest</p><h2 className="section-title mt-4">News from Prysm</h2></div><Link className="knowledge-link" to="/news">All news</Link></div>
          <NewsFeed compact />
        </div>
      </section>
    </>
  );
}
