import { useEffect, useRef } from "react";
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
    ["Business", -Math.PI / 2],
    ["Persons", -Math.PI / 2 + (Math.PI * 2) / 5],
    ["Account", -Math.PI / 2 + (Math.PI * 4) / 5],
    ["Money", -Math.PI / 2 + (Math.PI * 6) / 5],
    ["Invoices", -Math.PI / 2 + (Math.PI * 8) / 5],
  ];
  const calculate = () => {
    const center = { x: 260, y: 190 };
    const nodes = definitions.map(([label, angle]) => {
      const radius = 148;
      return { label, x: center.x + Math.cos(angle) * radius, y: center.y + Math.sin(angle) * radius };
    });
    return { center, nodes };
  };
  const network = calculate();
  const edgePath = (a, b, bend = 0) => {
    const mx=(a.x+b.x)/2-(b.y-a.y)*bend,my=(a.y+b.y)/2+(b.x-a.x)*bend;
    return `M ${a.x} ${a.y} Q ${mx} ${my} ${b.x} ${b.y}`;
  };
  return (
    <figure className="hero-graph" aria-labelledby="hero-graph-caption">
      <svg
        viewBox="0 0 520 380"
        role="img"
        aria-label="A person connected to an institution, persons, accounts, organization, and business"
      >
        <g className="hero-graph-edges">
          {network.nodes.map((node,index) => <path key={`spoke-${node.label}`} d={edgePath(network.center,node,index%2?.055:-.055)}><title>Person to {node.label}</title></path>)}
        </g>
        <g className="hero-graph-flow" aria-hidden="true">
          {network.nodes.map((node,index)=><g key={`flow-${node.label}`}>
            <circle r="2.4"><animateMotion path={edgePath(network.center,node)} dur={`${3.4 + index * .25}s`} begin={`${index * -.55}s`} repeatCount="indefinite"/>
            </circle>
            <circle r="1.6"><animateMotion path={edgePath(network.center,node)} dur={`${3.4 + index * .25}s`} begin={`${index * -.55 + 1.15}s`} repeatCount="indefinite"/>
            </circle>
          </g>)}
        </g>
        <g className="hero-graph-nodes">
          <g className="node-person" transform={`translate(${network.center.x} ${network.center.y})`}><circle r="30"/><g className="hero-node-icon central-person-icon"><circle cy="-9" r="6"/><path d="M-14 16c1-9 5-13 14-13s13 4 14 13"/></g><text y="50">Person</text></g>
          {network.nodes.map((node,index)=><g className={`node-related node-related-${index+1}`} transform={`translate(${node.x} ${node.y})`} key={node.label}><circle r="21"/><g className="hero-node-icon">{node.label==="Business"?<><rect x="-10" y="-6" width="20" height="13" rx="1"/><path d="M-4-6v-4h8v4M-10 1h20"/></>:node.label==="Account"?<><rect x="-10" y="-9" width="20" height="18" rx="1"/><path d="M-6-3h12M-6 4h7"/></>:node.label==="Money"?<><circle r="10"/><path d="M0-6v12M-3-4c5-3 6 4 1 4s-4 6 1 4"/></>:node.label==="Invoices"?<><path d="M-9-11h6l6 6v16h-12zM-3-11v6h6M-6 1h6M-6 6h6"/></>:<><circle cy="-5" r="3.5"/><circle cx="-7" cy="-1" r="2.7"/><circle cx="7" cy="-1" r="2.7"/><path d="M-7 10c.5-6 2.5-8 7-8s6.5 2 7 8"/></>}</g><text y="36">{node.label}</text></g>)}
        </g>
      </svg>
      <figcaption id="hero-graph-caption">
        A living view of financial relationships.
      </figcaption>
    </figure>
  );
}
export default function Home() {
  const heroRef=useRef(null),layoutRef=useRef(null);
  useEffect(()=>{const fit=()=>{const hero=heroRef.current,layout=layoutRef.current;if(!hero||!layout)return;hero.style.setProperty("--hero-fit","1");requestAnimationFrame(()=>{const available=hero.clientHeight-8,needed=layout.scrollHeight;hero.style.setProperty("--hero-fit",String(Math.max(.82,Math.min(1,available/needed))))})};fit();const observer=new ResizeObserver(fit);observer.observe(document.documentElement);observer.observe(layoutRef.current);return()=>observer.disconnect()},[]);
  return (
    <>
      <section className="home-hero" ref={heroRef}>
        <div className="shell home-hero-layout" ref={layoutRef}>
          <div className="home-hero-copy">
            <p className="home-hero-quote">
              “Follow the evidence. See the whole.”
            </p>
            <h1 tabIndex="-1" aria-label="Track the flow. Connect the dots. Expose the Fraud."><span>Track the flow.</span><span>Connect the dots.</span><span>Expose the Fraud.</span></h1>
            <p className="home-hero-brand">Prysm Intelligence</p>
            <Link
              to="/request-access"
              className="button button-primary home-hero-cta"
            >
              Start using Prysm <ArrowRight size={17} />
            </Link>
            <Link to="/report/intelligence" className="knowledge-link mt-5 inline-flex">
              Report suspected crime or fraud anonymously
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
      <section className="border-y border-[var(--border)] bg-[var(--surface)] py-[var(--space-section)] text-[var(--text)]">
        <div className="shell">
          <p className="eyebrow">Investigation workflow</p>
          <h2 className="section-title mt-5 max-w-3xl">
            A repeatable line from question to assessment.
          </h2>
          <ol className="mt-14 grid border-y border-[var(--border)] md:grid-cols-5">
            {steps.map(([n, t, d]) => (
              <li
                className="border-b border-[var(--border)] p-5 last:border-b-0 md:border-b-0 md:border-r md:last:border-r-0"
                key={n}
              >
                <span className="font-mono text-xs text-[var(--muted)]">{n}</span>
                <h3 className="mt-8 font-semibold">{t}</h3>
                <p className="muted mt-3 text-sm leading-6">{d}</p>
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
      <section className="border-y border-[var(--border)] bg-black py-[var(--space-section)] text-white">
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
