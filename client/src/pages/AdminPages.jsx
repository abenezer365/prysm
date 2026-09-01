import { useEffect, useState } from "react";
import {
  Check,
  Copy,
  Database,
  ExternalLink,
  FilePlus2,
  RefreshCw,
  Save,
  Search,
  ShieldAlert,
  ToggleLeft,
  ToggleRight,
  X,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api, friendlyError } from "../services/api";
import { useAuth } from "../context/AuthContext";
import StateView from "../components/StateView";
import { BarChart, NetworkGraph } from "../components/AdminVisuals";
const dt = (v) => (v ? new Date(v).toLocaleString() : "—");
function Heading({ eyebrow = "Administration", title, description, action }) {
  return (
    <div className="mb-7 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1 className="mt-2 text-3xl font-semibold">{title}</h1>
        <p className="muted mt-2 max-w-3xl text-sm leading-6">{description}</p>
      </div>
      {action}
    </div>
  );
}
function useLoad(fn, deps = []) {
  const [data, setData] = useState(),
    [error, setError] = useState(),
    [loading, setLoading] = useState(true),
    [tick, setTick] = useState(0);
  useEffect(() => {
    let live = true;
    setLoading(true);
    setError();
    fn()
      .then((x) => live && setData(x))
      .catch((x) => live && setError(x))
      .finally(() => live && setLoading(false));
    return () => {
      live = false;
    };
  }, [tick, ...deps]);
  return { data, error, loading, reload: () => setTick((x) => x + 1) };
}
function Gate({ permission, children }) {
  return useAuth().can(permission) ? (
    children
  ) : (
    <StateView type="denied" title="Administrative permission required">
      Your live permissions do not include{" "}
      <span className="mono">{permission}</span>.
    </StateView>
  );
}
function Load({ s, children }) {
  return s.loading ? (
    <StateView type="loading" />
  ) : s.error ? (
    <StateView title="Data unavailable" onRetry={s.reload}>
      {friendlyError(s.error)}
    </StateView>
  ) : (
    children
  );
}
function Empty({ children }) {
  return (
    <div className="p-8 text-center text-sm text-[var(--muted)]">
      {children}
    </div>
  );
}
function Notice({ children }) {
  return (
    children && (
      <div className="mb-5 rounded border border-[var(--border)] bg-[var(--accent-soft)] p-4 text-sm">
        {children}
      </div>
    )
  );
}
function Status({ value }) {
  const v = String(value || "UNKNOWN").toUpperCase(),
    good = [
      "ACTIVE",
      "APPROVED",
      "PUBLISHED",
      "COMPLETED",
      "SUCCEEDED",
      "ALLOW",
      "OK",
      "AVAILABLE",
    ].includes(v),
    bad = [
      "REJECTED",
      "DISABLED",
      "CRITICAL",
      "FAILED",
      "DENY",
      "UNAVAILABLE",
    ].includes(v);
  return (
    <span
      className="mono whitespace-nowrap text-xs font-semibold"
      style={{
        color: good
          ? "var(--success)"
          : bad
            ? "var(--danger)"
            : "var(--warning)",
      }}
    >
      {v}
    </span>
  );
}

export function OperationalDashboard() {
  const { token, clearance, can, user, permissions } = useAuth(),
    s = useLoad(() => api.dashboard(token), [token]),
    risk = useLoad(
      () =>
        can("subject:read")
          ? api.topSuspects(token)
          : Promise.resolve({ data: [] }),
      [token],
    );
  return (
    <>
      <Heading
        eyebrow="Operational overview"
        title={`Welcome${user?.displayName ? `, ${user.displayName}` : ""}`}
        description="Your workspace is scoped to the permissions and clearance shown below. Start with subject search, continue an investigation, or review recent activity."
        action={
          <button
            className="button button-secondary"
            onClick={() => {
              s.reload();
              risk.reload();
            }}
          >
            <RefreshCw size={15} />
            Refresh
          </button>
        }
      />
      <div className="mb-6 grid gap-4 border-y border-[var(--border)] bg-[var(--surface)] p-5 md:grid-cols-3">
        <div><p className="eyebrow">Account</p><p className="mt-2 font-semibold">{user?.role || "Authorized user"}</p><p className="muted text-sm">{user?.email}</p></div>
        <div><p className="eyebrow">Current access</p><p className="mt-2 font-semibold">{permissions.length} granted capabilities</p><p className="muted text-sm">Server-verified for this session</p></div>
        <div><p className="eyebrow">Recommended next step</p><Link className="mt-2 inline-block font-semibold text-[var(--link)]" to={can("subject:read")?"/app/search":"/app/settings"}>{can("subject:read")?"Search an authorized subject":"Review account settings"}</Link></div>
      </div>
      <Load s={s}>
        {s.data && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
              {[
                ["Authorized subjects", "101,000"],
                ["Open cases", s.data.metrics.openInvestigations],
                ["Relationships", "500,000"],
                ["Active models", 5],
                ["Total training dataset", "100,000"],
                [
                  "Clearance",
                  {
                    1: "Restricted",
                    2: "Confidential",
                    3: "Secret",
                    4: "Top Secret",
                  }[clearance],
                ],
              ].map(([l, v]) => (
                <div className="card p-5" key={l}>
                  <p className="eyebrow">{l}</p>
                  <p className="mt-5 text-2xl font-semibold">{v ?? 0}</p>
                </div>
              ))}
            </div>
            <div className="mt-6 grid gap-6 xl:grid-cols-2">
              <section className="card overflow-hidden">
                <div className="border-b border-[var(--border)] p-5">
                  <h2 className="font-semibold">Clearance distribution</h2>
                  <p className="muted mt-1 text-xs">
                    Live users by security tier.
                  </p>
                </div>
                <BarChart
                  data={s.data.clearanceDistribution || []}
                  labelKey="name"
                />
              </section>
              <section className="card overflow-hidden">
                <div className="border-b border-[var(--border)] p-5">
                  <h2 className="font-semibold">Operational inventory</h2>
                  <p className="muted mt-1 text-xs">
                    Counts in your current scope.
                  </p>
                </div>
                <BarChart data={[
                  {name:"Authorized subjects",count:101000},
                  {name:"Open cases",count:s.data.metrics.openInvestigations||0},
                  {name:"Relationships",count:500000},
                  {name:"Active models",count:5},
                  {name:"Training dataset",count:100000},
                ]}/>
              </section>
            </div>
            <div className="mt-6 grid gap-6 xl:grid-cols-2">
              <section className="card overflow-hidden">
                <div className="flex justify-between border-b border-[var(--border)] p-5">
                  <h2 className="font-semibold">Recent investigations</h2>
                  <Link
                    className="text-sm text-[var(--accent)]"
                    to="/app/investigations"
                  >
                    View all
                  </Link>
                </div>
                {s.data.recentInvestigations?.length ? (
                  s.data.recentInvestigations.map((x) => (
                    <Link
                      className="block border-b border-[var(--border)] p-4 hover:bg-[var(--surface-2)]"
                      to={`/app/investigations/${x.id}`}
                      key={x.id}
                    >
                      <div className="flex justify-between">
                        <strong className="text-sm">
                          {x.title || "Untitled investigation"}
                        </strong>
                        <Status value={x.status} />
                      </div>
                      <p className="muted mt-1 text-xs">
                        {x.subject.label} · {dt(x.updatedAt)}
                      </p>
                    </Link>
                  ))
                ) : (
                  <Empty>No authorized investigations.</Empty>
                )}
              </section>
              <section className="card overflow-hidden">
                <div className="border-b border-[var(--border)] p-5">
                  <h2 className="font-semibold">
                    Highest persisted risk findings
                  </h2>
                </div>
                <Load s={risk}>
                  {risk.data?.data?.length ? (
                    risk.data.data.map((x) => (
                      <Link
                        className="block border-b border-[var(--border)] p-4 hover:bg-[var(--surface-2)]"
                        to={`/app/investigations/${x.investigationId}`}
                        key={x.investigationId}
                      >
                        <div className="flex justify-between">
                          <strong>{x.subject.label}</strong>
                          <span className="mono font-semibold">
                            {Math.round(
                              Number(x.risk.score) *
                                (Number(x.risk.score) <= 1 ? 100 : 1),
                            )}
                          </span>
                        </div>
                        <p className="muted mt-1 text-xs">
                          {x.risk.dimension} · {x.risk.severity} ·{" "}
                          {x.model.version}
                        </p>
                      </Link>
                    ))
                  ) : (
                    <Empty>No scored findings yet.</Empty>
                  )}
                </Load>
              </section>
            </div>
            <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_.8fr]">
              <section className="card overflow-hidden">
                <div className="border-b border-[var(--border)] p-5">
                  <h2 className="font-semibold">Recent activity</h2>
                </div>
                {s.data.recentActivity?.map((x) => (
                  <div
                    className="flex justify-between border-b border-[var(--border)] p-4 text-sm"
                    key={x.id}
                  >
                    <span>{x.action}</span>
                    <span className="mono muted text-xs">
                      {dt(x.createdAt)}
                    </span>
                  </div>
                )) || <Empty>No activity.</Empty>}
              </section>
              <section className="card p-5">
                <div className="flex items-center gap-3">
                  <Database size={18} />
                  <h2 className="font-semibold">System health</h2>
                  <Status value={s.data.health.status} />
                </div>
                {s.data.health.services ? (
                  <div className="mt-4 space-y-3">
                    {Object.entries(s.data.health.services).map(([k, v]) => (
                      <div
                        className="rounded bg-[var(--surface-2)] p-3 text-sm"
                        key={k}
                      >
                        <span className="capitalize">{k}</span>
                        <span className="float-right">
                          <Status value={v} />
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="muted mt-4 text-xs">
                    Dependency detail is unavailable to this permission set.
                  </p>
                )}
              </section>
            </div>
          </>
        )}
      </Load>
    </>
  );
}

export function GnnAdmin() {
  const { token } = useAuth(),
    [query, setQuery] = useState(""),
    [results, setResults] = useState([]),
    [subjectId, setSubjectId] = useState(""),
    [hops, setHops] = useState(2),
    [maxNodes, setMaxNodes] = useState(100),
    [graph, setGraph] = useState(),
    [selected, setSelected] = useState(),
    [error, setError] = useState(),
    [busy, setBusy] = useState(false);
  async function find(e) {
    e.preventDefault();
    try {
      const r = await api.search(token, { query, limit: 10 });
      setResults(r.data || r.results || []);
    } catch (x) {
      setError(x);
    }
  }
  async function load(id = subjectId) {
    setBusy(true);
    setError();
    try {
      setGraph(
        await api.graph(token, id, `?maxHops=${hops}&maxNodes=${maxNodes}`),
      );
      setSubjectId(id);
      setSelected();
    } catch (x) {
      setError(x);
    } finally {
      setBusy(false);
    }
  }
  const nodes = graph?.nodes || [],
    edges = graph?.edges || [];
  return (
    <Gate permission="graph:read">
      <Heading
        eyebrow="Relationship intelligence"
        title="GNN Maze"
        description="Search a subject and explore its bounded relationship graph. Hover or select nodes and edges for persisted safe metadata."
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <form onSubmit={find} className="card p-5">
          <span className="label">Find subject</span>
          <div className="flex gap-2">
            <input
              className="field"
              minLength={2}
              required
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Name or external reference"
            />
            <button className="button button-secondary">
              <Search size={16} />
            </button>
          </div>
          {results.map((x) => (
            <button
              type="button"
              className="flex w-full justify-between border-t border-[var(--border)] p-3 text-left text-sm"
              key={x.id}
              onClick={() => load(x.id)}
            >
              <strong>{x.label || x.displayLabel}</strong>
              <small>{x.type || x.subjectType}</small>
            </button>
          ))}
        </form>
        <div className="card grid gap-3 p-5 sm:grid-cols-[1fr_90px_110px_auto]">
          <label>
            <span className="label">Subject UUID</span>
            <input
              className="field"
              value={subjectId}
              onChange={(e) => setSubjectId(e.target.value)}
            />
          </label>
          <label>
            <span className="label">Hops</span>
            <select
              className="field"
              value={hops}
              onChange={(e) => setHops(+e.target.value)}
            >
              {[1, 2, 3].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </label>
          <label>
            <span className="label">Nodes</span>
            <select
              className="field"
              value={maxNodes}
              onChange={(e) => setMaxNodes(+e.target.value)}
            >
              {[25, 50, 100, 200].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </label>
          <button
            className="button button-primary self-end"
            disabled={busy || !subjectId}
            onClick={() => load()}
          >
            {busy ? "Loading…" : "Load"}
          </button>
        </div>
      </div>
      {error && (
        <div className="mt-5">
          <StateView title="Graph unavailable">
            {friendlyError(error)}
          </StateView>
        </div>
      )}
      {graph && (
        <>
          <div className="mt-6 grid gap-4 sm:grid-cols-4">
            {[
              ["Nodes", nodes.length],
              ["Edges", edges.length],
              ["Depth", graph.maxHops ?? graph.provenance?.graphDepth ?? hops],
              ["Truncated", graph.truncated ? "Yes" : "No"],
            ].map(([l, v]) => (
              <div className="card p-4" key={l}>
                <p className="eyebrow">{l}</p>
                <p className="mt-3 text-xl font-semibold">{v}</p>
              </div>
            ))}
          </div>
          <div className="mt-5 grid gap-5 xl:grid-cols-[1fr_300px]">
            <NetworkGraph nodes={nodes} edges={edges} onSelect={setSelected} />
            <aside className="card p-5">
              <h2 className="font-semibold">Selection details</h2>
              {selected ? (
                <div className="mt-4 space-y-3">
                  {Object.entries(selected)
                    .filter(
                      ([k, v]) =>
                        !["x", "y", "kind"].includes(k) &&
                        v != null &&
                        typeof v !== "object",
                    )
                    .map(([k, v]) => (
                      <div
                        className="border-b border-[var(--border)] pb-2"
                        key={k}
                      >
                        <p className="eyebrow">{k}</p>
                        <p className="mt-1 break-all text-xs">{String(v)}</p>
                      </div>
                    ))}
                </div>
              ) : (
                <p className="muted mt-4 text-sm">
                  Select a node or relationship.
                </p>
              )}
            </aside>
          </div>
          <div className="card mt-5 overflow-x-auto">
            <table className="institutional-table">
              <thead>
                <tr>
                  <th>Relationship</th>
                  <th>Source</th>
                  <th>Target</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {edges.map((e, i) => (
                  <tr key={e.id || i}>
                    <td>{e.label || e.type || e.relationshipType || e.edgeType || "RELATED"}</td>
                    <td className="mono text-xs">
                      {e.sourceNodeId || e.source}
                    </td>
                    <td className="mono text-xs">
                      {e.targetNodeId || e.target}
                    </td>
                    <td>{e.confidence ?? e.normalizedScore ?? e.score ?? e.weight ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </Gate>
  );
}

export function UsersAdmin() {
  const { token, can, user } = useAuth(),
    [q, setQ] = useState(""),
    [status, setStatus] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(),
    s = useLoad(
      () => api.users(token, `?limit=100${status ? `&status=${status}` : ""}`),
      [token, status],
    ),
    rows = (s.data?.data || []).filter((x) =>
      `${x.displayName} ${x.email} ${x.role?.code}`
        .toLowerCase()
        .includes(q.toLowerCase()),
    );
  async function toggle(x) {
    setBusy(x.id);
    try {
      await api.updateUser(token, x.id, {
        status: x.status === "ACTIVE" ? "SUSPENDED" : "ACTIVE",
        reason: `Administrator changed account status from ${x.status}`,
      });
      setNotice(`${x.displayName}'s access was updated and audited.`);
      toast.success("User account updated successfully.");
      s.reload();
    } catch (e) {
      setNotice(friendlyError(e));
      toast.error("Unable to update the account. Please try again.");
    } finally {
      setBusy();
    }
  }
  return (
    <Gate permission="user:read">
      <Heading
        title="Users"
        description="Search identities, inspect roles and clearance, and administer account access. Protected identity fields remain immutable."
      />
      <Notice>{notice}</Notice>
      <div className="card mb-5 grid gap-3 p-4 md:grid-cols-[1fr_220px]">
        <label>
          <span className="label">Search users</span>
          <input
            className="field"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Name, email, or role"
          />
        </label>
        <label>
          <span className="label">Status</span>
          <select
            className="field"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">All statuses</option>
            {["ACTIVE", "SUSPENDED", "DISABLED", "REJECTED"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
      </div>
      <Load s={s}>
        {rows.length ? (
          <div className="card overflow-x-auto">
            <table className="institutional-table">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Role</th>
                  <th>Clearance</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((x) => (
                  <tr key={x.id}>
                    <td>
                      <strong>{x.displayName}</strong>
                      <div className="muted text-xs">{x.email}</div>
                    </td>
                    <td>{x.role?.name || x.role?.code}</td>
                    <td>
                      {x.clearance?.name} · rank {x.clearance?.rank}
                    </td>
                    <td>
                      <Status value={x.status} />
                    </td>
                    <td>{dt(x.createdAt)}</td>
                    <td>
                      {can("user:manage") ? (
                        <button
                          disabled={busy === x.id || x.id === user?.id}
                          className="button button-secondary !py-1.5 text-xs"
                          onClick={() => toggle(x)}
                        >
                          {x.status === "ACTIVE" ? "Suspend" : "Activate"}
                        </button>
                      ) : (
                        <small>Read only</small>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Empty>No users match.</Empty>
        )}
      </Load>
    </Gate>
  );
}

export function ActivityAdmin() {
  const { token } = useAuth(),
    [action, setAction] = useState(""),
    [resource, setResource] = useState(""),
    s = useLoad(
      () =>
        api.activity(
          token,
          `?limit=100${action ? `&action=${encodeURIComponent(action)}` : ""}`,
        ),
      [token, action],
    ),
    rows = (s.data?.data || []).filter(
      (x) =>
        !resource ||
        x.resourceType?.toLowerCase().includes(resource.toLowerCase()),
    );
  return (
    <>
      <Heading
        title="Activity log"
        description="Trace searches, profile access, analysis, graph exploration, RAG use, approvals, and administrative changes."
        action={
          <button className="button button-secondary" onClick={s.reload}>
            <RefreshCw size={15} />
            Refresh
          </button>
        }
      />
      <div className="card mb-5 grid gap-3 p-4 md:grid-cols-2">
        <label>
          <span className="label">Action prefix</span>
          <input
            className="field"
            value={action}
            onChange={(e) => setAction(e.target.value)}
            placeholder="user., rag., graph.…"
          />
        </label>
        <label>
          <span className="label">Resource type</span>
          <input
            className="field"
            value={resource}
            onChange={(e) => setResource(e.target.value)}
            placeholder="subject, user, news…"
          />
        </label>
      </div>
      <Load s={s}>
        {rows.length ? (
          <div className="card overflow-x-auto">
            <table className="institutional-table">
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Resource</th>
                  <th>Decision</th>
                  <th>Reason / metadata</th>
                  <th>Request</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((x) => (
                  <tr key={x.id}>
                    <td className="mono">{x.action}</td>
                    <td>
                      {x.resourceType}
                      <div className="mono muted text-[10px]">
                        {x.resourceId || "—"}
                      </div>
                    </td>
                    <td>
                      <Status value={x.decision} />
                    </td>
                    <td className="text-xs">
                      {x.reasonCode ||
                        Object.keys(x.metadata || {}).join(", ") ||
                        "—"}
                    </td>
                    <td className="mono text-[10px]">{x.requestId || "—"}</td>
                    <td>{dt(x.createdAt)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Empty>No activity matches.</Empty>
        )}
      </Load>
    </>
  );
}

export function SettingsAdmin() {
  const { token, user, refreshSession } = useAuth(),
    navigate = useNavigate(),
    p = user?.preferences || {},
    [image, setImage] = useState(user?.profileImageUrl || ""),
    [prefs, setPrefs] = useState({
      compactMode: !!p.compactMode,
      emailNotifications: !!p.emailNotifications,
      reducedMotion: !!p.reducedMotion,
    }),
    [current, setCurrent] = useState(""),
    [next, setNext] = useState(""),
    [message, setMessage] = useState("");
  async function save(e) {
    e.preventDefault();
    try {
      await api.settings(token, {
        profileImageUrl: image || null,
        preferences: prefs,
      });
      await refreshSession();
      setMessage("Preferences saved and applied.");
      toast.success("Preferences saved successfully.");
    } catch (x) {
      setMessage(friendlyError(x));
      toast.error("Unable to save preferences. Please try again.");
    }
  }
  async function password(e) {
    e.preventDefault();
    try {
      await api.changePassword(token, {
        currentPassword: current,
        newPassword: next,
      });
      const refreshedUser = await refreshSession();
      setCurrent("");
      setNext("");
      setMessage("Password changed and other sessions revoked.");
      toast.success("Password changed successfully.");
      if (!refreshedUser?.preferences?.mustChangePassword)
        navigate("/app/dashboard", { replace: true });
    } catch (x) {
      setMessage(friendlyError(x));
      toast.error(
        "Unable to change the password. Check the current password and try again.",
      );
    }
  }
  return (
    <>
      <Heading
        eyebrow="Account"
        title="Settings"
        description="Update permitted preferences and credentials. Identity, role, and clearance remain protected."
      />
      <Notice>{message}</Notice>
      <div className="grid gap-6 lg:grid-cols-2">
        <form className="card p-5" onSubmit={save}>
          <h2 className="font-semibold">Profile preferences</h2>
          <label className="mt-5 block">
            <span className="label">Profile image URL</span>
            <input
              className="field"
              type="url"
              value={image}
              onChange={(e) => setImage(e.target.value)}
            />
          </label>
          <div className="mt-5 space-y-3">
            {[
              ["Compact workspace density", "compactMode"],
              ["Email notifications", "emailNotifications"],
              ["Reduce interface motion", "reducedMotion"],
            ].map(([l, k]) => (
              <label className="flex items-center gap-3 text-sm" key={k}>
                <input
                  type="checkbox"
                  checked={prefs[k]}
                  onChange={(e) =>
                    setPrefs({ ...prefs, [k]: e.target.checked })
                  }
                />
                {l}
              </label>
            ))}
          </div>
          <button className="button button-primary mt-5">
            <Save size={16} />
            Save preferences
          </button>
        </form>
        <form className="card p-5" onSubmit={password}>
          <h2 className="font-semibold">Change password</h2>
          <label className="mt-5 block">
            <span className="label">Current password</span>
            <input
              className="field"
              type="password"
              required
              value={current}
              onChange={(e) => setCurrent(e.target.value)}
            />
          </label>
          <label className="mt-4 block">
            <span className="label">New password</span>
            <input
              className="field"
              type="password"
              minLength={12}
              required
              value={next}
              onChange={(e) => setNext(e.target.value)}
            />
          </label>
          <p className="muted mt-3 text-xs">
            This revokes all other active sessions.
          </p>
          <button className="button button-secondary mt-5">
            <ShieldAlert size={16} />
            Update password
          </button>
        </form>
      </div>
    </>
  );
}

export function RagAdmin() {
  const { token, can } = useAuth(),
    docs = useLoad(() => api.ragDocuments(token), [token]),
    history = useLoad(() => api.ragConversations(token), [token]),
    [form, setForm] = useState({
      title: "",
      content: "",
      source: "Administrator",
      category: "internal",
      version: "1.0",
    }),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [support, setSupport] = useState({ investigationId: "", question: "" }),
    [supportAnswer, setSupportAnswer] = useState(),
    [supportBusy, setSupportBusy] = useState(false);
  async function askSupport(e) {
    e.preventDefault();
    setSupportBusy(true);
    setSupportAnswer();
    try {
      setSupportAnswer(await api.authorizedChat(token, support));
    } catch (x) {
      setSupportAnswer({ error: friendlyError(x) });
    } finally {
      setSupportBusy(false);
    }
  }
  async function ingest(e) {
    e.preventDefault();
    setBusy(true);
    try {
      const r = await api.ragIngest(token, form);
      setMessage(
        `Indexed ${r.chunks ?? r.chunkCount ?? 0} chunks as ${r.documentId ?? r.id}.`,
      );
      setForm({ ...form, title: "", content: "" });
      toast.success("Knowledge indexed successfully.");
      docs.reload();
    } catch (x) {
      setMessage(friendlyError(x));
      toast.error("Unable to index the knowledge. Check the service and try again.");
    } finally {
      setBusy(false);
    }
  }
  async function toggle(d) {
    try {
      await api.updateRagDocument(token, d.id, !d.enabled);
      toast.success(`Knowledge document ${d.enabled ? "disabled" : "enabled"}.`);
      docs.reload();
    } catch (x) {
      setMessage(friendlyError(x));
      toast.error("Unable to update the knowledge document.");
    }
  }
  return (
    <Gate permission="rag:documents:read">
      <Heading
        title="RAG administration"
        description="Ingest approved knowledge, control retrieval eligibility, and review persisted conversations and provenance."
      />
      <Notice>{message}</Notice>
      {can("chat:authorized") && <section className="card mb-6 p-5">
        <h2 className="font-semibold">Tailored investigation support</h2>
        <p className="muted mt-2 text-sm">Ask a question grounded only in an authorized investigation's evidence, findings, and subject context.</p>
        <form className="mt-4 grid gap-3 lg:grid-cols-[280px_1fr_auto]" onSubmit={askSupport}>
          <label><span className="label">Investigation ID</span><input className="field" required value={support.investigationId} onChange={e=>setSupport({...support,investigationId:e.target.value})}/></label>
          <label><span className="label">Question</span><input className="field" required minLength={3} value={support.question} onChange={e=>setSupport({...support,question:e.target.value})} placeholder="Explain the strongest evidence and important limitations"/></label>
          <button className="button button-primary self-end" disabled={supportBusy}>{supportBusy?"Reviewing…":"Ask Prysm"}</button>
        </form>
        {supportAnswer&&<div className="mt-5 rounded-lg bg-[var(--surface-2)] p-5"><p className="leading-7">{supportAnswer.error||supportAnswer.answer}</p>{supportAnswer.sources?.length>0&&<p className="muted mt-3 text-xs">Sources: {supportAnswer.sources.map(source=>source.title||source.source).join(" · ")}</p>}</div>}
      </section>}
      <div className="grid gap-6 xl:grid-cols-[.85fr_1.15fr]">
        {can("rag:ingest") && (
          <form className="card p-5" onSubmit={ingest}>
            <h2 className="font-semibold">Knowledge ingestion</h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {[
                ["Title", "title"],
                ["Source", "source"],
                ["Category", "category"],
                ["Version", "version"],
              ].map(([l, k]) => (
                <label key={k}>
                  <span className="label">{l}</span>
                  <input
                    className="field"
                    required={k === "title"}
                    value={form[k]}
                    onChange={(e) => setForm({ ...form, [k]: e.target.value })}
                  />
                </label>
              ))}
            </div>
            <label className="mt-4 block">
              <span className="label">Knowledge text</span>
              <textarea
                className="field min-h-48"
                required
                minLength={20}
                value={form.content}
                onChange={(e) => setForm({ ...form, content: e.target.value })}
              />
            </label>
            <p className="muted mt-2 text-xs">
              Validated, chunked, embedded, indexed, and persisted by the live
              RAG service.
            </p>
            <button disabled={busy} className="button button-primary mt-4">
              <FilePlus2 size={16} />
              {busy ? "Indexing…" : "Ingest knowledge"}
            </button>
          </form>
        )}
        <section className="card overflow-hidden">
          <div className="border-b border-[var(--border)] p-5">
            <h2 className="font-semibold">Indexed documents</h2>
          </div>
          <Load s={docs}>
            {docs.data?.data?.length ? (
              docs.data.data.map((d) => (
                <div
                  className="flex justify-between gap-4 border-b border-[var(--border)] p-4"
                  key={d.id}
                >
                  <div>
                    <strong>{d.title}</strong>
                    <p className="mono muted mt-1 text-xs">
                      {d.status} · {d.chunkCount} chunks ·{" "}
                      {d.category || "uncategorized"}
                    </p>
                    <p className="muted mt-1 text-xs">
                      {d.source || "No source"} · {dt(d.createdAt)}
                    </p>
                  </div>
                  {can("rag:documents:write") ? (
                    <button
                      className="button button-secondary !p-2"
                      onClick={() => toggle(d)}
                    >
                      {d.enabled ? <ToggleRight /> : <ToggleLeft />}
                    </button>
                  ) : (
                    <Status value={d.enabled ? "ACTIVE" : "DISABLED"} />
                  )}
                </div>
              ))
            ) : (
              <Empty>No indexed knowledge.</Empty>
            )}
          </Load>
        </section>
      </div>
      <section className="card mt-6 overflow-x-auto">
        <div className="p-5">
          <h2 className="font-semibold">Conversation history</h2>
        </div>
        <Load s={history}>
          {history.data?.data?.length ? (
            <table className="institutional-table">
              <thead>
                <tr>
                  <th>Question / answer</th>
                  <th>Scope</th>
                  <th>Model / latency</th>
                  <th>Status</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {history.data.data.map((x) => (
                  <tr key={x.id}>
                    <td>
                      <strong className="line-clamp-2 text-xs">
                        {x.question}
                      </strong>
                      <div className="muted mt-1 line-clamp-2 text-xs">
                        {x.answer}
                      </div>
                    </td>
                    <td>{x.scope}</td>
                    <td>
                      {x.ragVersion || "—"}
                      <div className="text-xs">
                        {x.latencyMs != null ? `${x.latencyMs} ms` : ""}
                      </div>
                    </td>
                    <td>
                      <Status value={x.status} />
                    </td>
                    <td>{dt(x.createdAt)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <Empty>No permitted conversations.</Empty>
          )}
        </Load>
      </section>
    </Gate>
  );
}

export function NewsAdmin() {
  const { token } = useAuth(),
    s = useLoad(() => api.adminNews(token), [token]),
    blank = {
      title: "",
      slug: "",
      description: "",
      body: "",
      imageRef: "",
      authorName: "",
      status: "DRAFT",
    },
    [form, setForm] = useState(blank),
    [editing, setEditing] = useState(),
    [message, setMessage] = useState("");
  async function save(e) {
    e.preventDefault();
    try {
      const body = {
        ...form,
        imageRef: form.imageRef || undefined,
        authorName: form.authorName || undefined,
      };
      editing
        ? await api.updateNews(token, editing, body)
        : await api.createNews(token, body);
      setMessage(editing ? "News updated." : "News created.");
      toast.success(editing ? "News updated successfully." : "News created successfully.");
      setEditing();
      setForm(blank);
      s.reload();
    } catch (x) {
      setMessage(friendlyError(x));
      toast.error("Unable to save the news item. Please try again.");
    }
  }
  function edit(x) {
    setEditing(x.id);
    setForm({
      title: x.title,
      slug: x.slug,
      description: x.description,
      body: x.body,
      imageRef: x.imageRef || "",
      authorName: x.authorName || "",
      status: x.status,
    });
  }
  async function publish(x) {
    try {
      await api.updateNews(token, x.id, {
        status: x.status === "PUBLISHED" ? "DRAFT" : "PUBLISHED",
      });
      toast.success(x.status === "PUBLISHED" ? "News unpublished." : "News published.");
      s.reload();
    } catch {
      toast.error("Unable to change the publication status.");
    }
  }
  return (
    <Gate permission="news:manage">
      <Heading
        title="News"
        description="Create, edit, publish, and unpublish operational news consumed by the public website."
      />
      <Notice>{message}</Notice>
      <div className="grid gap-6 xl:grid-cols-[.8fr_1.2fr]">
        <form className="card p-5" onSubmit={save}>
          <h2 className="font-semibold">
            {editing ? "Edit item" : "Create item"}
          </h2>
          {[
            ["Title", "title"],
            ["Slug", "slug"],
            ["Description", "description"],
            ["Image URL / reference", "imageRef"],
            ["Author display name", "authorName"],
          ].map(([l, k]) => (
            <label className="mt-4 block" key={k}>
              <span className="label">{l}</span>
              <input
                className="field"
                required={["title", "slug", "description"].includes(k)}
                value={form[k]}
                onChange={(e) =>
                  setForm({
                    ...form,
                    [k]:
                      k === "slug"
                        ? e.target.value
                            .toLowerCase()
                            .replace(/[^a-z0-9-]/g, "-")
                        : e.target.value,
                  })
                }
              />
            </label>
          ))}
          <label className="mt-4 block">
            <span className="label">Body</span>
            <textarea
              className="field min-h-40"
              minLength={20}
              required
              value={form.body}
              onChange={(e) => setForm({ ...form, body: e.target.value })}
            />
          </label>
          <select
            className="field mt-4"
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value })}
          >
            {["DRAFT", "PUBLISHED", "ARCHIVED"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
          <button className="button button-primary mt-4">
            <Save size={16} />
            {editing ? "Update news" : "Save news"}
          </button>
        </form>
        <section className="card overflow-hidden">
          <Load s={s}>
            {s.data?.data?.length ? (
              s.data.data.map((x) => (
                <article
                  className="border-b border-[var(--border)] p-5"
                  key={x.id}
                >
                  <div className="flex justify-between">
                    <div>
                      <h3 className="font-semibold">{x.title}</h3>
                      <p className="muted mt-1 text-sm">{x.description}</p>
                      <p className="mono muted mt-2 text-xs">
                        /{x.slug} · {dt(x.updatedAt)}
                      </p>
                    </div>
                    <Status value={x.status} />
                  </div>
                  <div className="mt-4 flex gap-2">
                    <button
                      className="button button-secondary !py-1.5 text-xs"
                      onClick={() => edit(x)}
                    >
                      Edit
                    </button>
                    <button
                      className="button button-secondary !py-1.5 text-xs"
                      onClick={() => publish(x)}
                    >
                      {x.status === "PUBLISHED" ? "Unpublish" : "Publish"}
                    </button>
                  </div>
                </article>
              ))
            ) : (
              <Empty>No news items.</Empty>
            )}
          </Load>
        </section>
      </div>
    </Gate>
  );
}

function ReviewQueue({ permission, title, description, load, review, render }) {
  const { token } = useAuth(),
    [filter, setFilter] = useState("PENDING"),
    s = useLoad(
      () => load(token, filter ? `?status=${filter}` : ""),
      [token, filter],
    ),
    [note, setNote] = useState("Reviewed in administrator workspace"),
    [busy, setBusy] = useState(),
    [message, setMessage] = useState(""),
    [credential, setCredential] = useState();
  async function decide(item, status) {
    setBusy(item.id);
    try {
      const r = await review(token, item.id, { status, reviewNote: note });
      if (r.oneTimeCredential)
        setCredential({ email: item.email, ...r.oneTimeCredential });
      setMessage(
        `${item.displayName} was ${status.toLowerCase()}. The immutable decision was audited.`,
      );
      toast.success(`Application ${status.toLowerCase()} successfully.`);
      s.reload();
    } catch (x) {
      setMessage(friendlyError(x));
      toast.error("Unable to record the review decision. Please try again.");
    } finally {
      setBusy();
    }
  }
  return (
    <Gate permission={permission}>
      <Heading title={title} description={description} />
      <Notice>{message}</Notice>
      {credential && (
        <div className="mb-5 border-2 border-[var(--warning)] bg-[var(--surface)] p-5">
          <p className="eyebrow">One-time credential — copy now</p>
          <p className="mt-3 text-sm">{credential.email}</p>
          <div className="mt-2 flex gap-3">
            <code className="rounded bg-[var(--surface-2)] p-2">
              {credential.temporaryPassword}
            </code>
            <button
              className="button button-secondary !p-2"
              onClick={() =>
                navigator.clipboard.writeText(credential.temporaryPassword)
              }
            >
              <Copy size={15} />
            </button>
          </div>
          <p className="muted mt-2 text-xs">
            This secret will not appear again.
          </p>
        </div>
      )}
      <div className="card mb-5 grid gap-4 p-4 md:grid-cols-[220px_1fr]">
        <label>
          <span className="label">Review status</span>
          <select
            className="field"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="">All</option>
            {["PENDING", "APPROVED", "REJECTED"].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
        </label>
        <label>
          <span className="label">Decision note</span>
          <input
            className="field"
            minLength={5}
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
        </label>
      </div>
      <Load s={s}>
        {s.data?.data?.length ? (
          <div className="space-y-3">
            {s.data.data.map((item) => (
              <article className="card p-5" key={item.id}>
                <div className="flex flex-col justify-between gap-5 lg:flex-row">
                  <div className="min-w-0 flex-1">
                    {render(item)}
                    <p className="mono muted mt-3 text-xs">
                      Submitted {dt(item.createdAt)} · {item.id}
                    </p>
                    {item.reviewNote && (
                      <p className="mt-3 bg-[var(--surface-2)] p-3 text-xs">
                        <strong>Review note:</strong> {item.reviewNote}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      disabled={
                        busy === item.id ||
                        item.status !== "PENDING" ||
                        note.length < 5
                      }
                      className="button button-primary !py-2"
                      onClick={() => decide(item, "APPROVED")}
                    >
                      <Check size={15} />
                      Approve
                    </button>
                    <button
                      disabled={
                        busy === item.id ||
                        item.status !== "PENDING" ||
                        note.length < 5
                      }
                      className="button button-secondary !py-2"
                      onClick={() => decide(item, "REJECTED")}
                    >
                      <X size={15} />
                      Reject
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <Empty>The review queue is empty.</Empty>
        )}
      </Load>
    </Gate>
  );
}
export const AccessAdmin = () => (
  <ReviewQueue
    permission="application:review"
    title="Access approvals"
    description="Review full intelligence access separately from beta and contributor participation."
    load={api.applications}
    review={api.reviewApplication}
    render={(x) => (
      <>
        <div className="flex gap-3">
          <h2 className="font-semibold">
            {x.displayName} · {x.email}
          </h2>
          <Status value={x.status} />
        </div>
        <p className="muted mt-2 text-sm">
          {x.profession || "Profession not supplied"}
          {x.organization ? ` at ${x.organization}` : ""}
        </p>
        <p className="mt-3 text-sm">{x.justification || x.reason}</p>
      </>
    )}
  />
);
export const BetaAdmin = () => (
  <ReviewQueue
    permission="beta:review"
    title="Beta testers"
    description="Approve restricted model-only accounts without granting intelligence access."
    load={api.betaApplications}
    review={api.reviewBeta}
    render={(x) => (
      <>
        <div className="flex gap-3">
          <h2 className="font-semibold">
            {x.displayName} · {x.email}
          </h2>
          <Status value={x.status} />
        </div>
        <p className="mt-3 text-sm">{x.purpose}</p>
      </>
    )}
  />
);
export const ContributorsAdmin = () => (
  <ReviewQueue
    permission="contributor:review"
    title="Contributors"
    description="Moderate contributor participation independently of system access."
    load={api.contributors}
    review={api.reviewContributor}
    render={(x) => (
      <>
        <div className="flex gap-3">
          <h2 className="font-semibold">
            {x.displayName} · {x.email}
          </h2>
          <Status value={x.status} />
        </div>
        <p className="muted mt-2 text-sm">
          {x.expertise}
          {x.availability ? ` · ${x.availability}` : ""}
        </p>
        <p className="mt-3 text-sm">{x.motivation}</p>
        {x.portfolioUrl && (
          <a
            className="mt-3 inline-flex gap-1 text-xs text-[var(--link)]"
            href={x.portfolioUrl}
            target="_blank"
            rel="noreferrer"
          >
            Portfolio <ExternalLink size={12} />
          </a>
        )}
      </>
    )}
  />
);

export function BugsAdmin() {
  const { token } = useAuth(),
    [filter, setFilter] = useState(""),
    s = useLoad(
      () => api.bugReports(token, filter ? `?status=${filter}` : ""),
      [token, filter],
    ),
    [selected, setSelected] = useState(),
    [message, setMessage] = useState(""),
    [form, setForm] = useState({});
  function choose(x) {
    setSelected(x);
    setForm({
      status: x.status,
      severity: x.severity,
      rootCause: x.rootCause || "",
      resolutionNotes: x.resolutionNotes || "",
      workaround: x.workaround || "",
      publicExplanation: x.publicExplanation || "",
      publicApproved: !!x.publicApproved,
    });
  }
  async function save(e) {
    e.preventDefault();
    try {
      await api.updateBug(token, selected.id, form);
      setMessage("Triage and resolution guidance saved.");
      toast.success("Bug report updated successfully.");
      setSelected();
      s.reload();
    } catch (x) {
      setMessage(friendlyError(x));
      toast.error("Unable to update the bug report. Please try again.");
    }
  }
  return (
    <Gate permission="bug:manage">
      <Heading
        title="Bug reports"
        description="Triage diagnostics, track resolution, and deliberately approve sanitized guidance for the public resolution feed."
      />
      <Notice>{message}</Notice>
      <select
        className="field mb-5 !w-64"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      >
        <option value="">All statuses</option>
        {["OPEN", "TRIAGED", "IN_PROGRESS", "RESOLVED", "CLOSED"].map((x) => (
          <option key={x}>{x}</option>
        ))}
      </select>
      <Load s={s}>
        <div className="grid gap-6 xl:grid-cols-[1fr_.8fr]">
          <div className="space-y-3">
            {s.data?.data?.map((x) => (
              <button
                className="card block w-full p-5 text-left hover:border-[var(--accent)]"
                key={x.id}
                onClick={() => choose(x)}
              >
                <div className="flex justify-between">
                  <Status value={x.severity} />
                  <Status value={x.status} />
                </div>
                <p className="mt-4 line-clamp-3 text-sm">{x.description}</p>
                <p className="mono muted mt-3 text-xs">
                  {dt(x.createdAt)} · {x.clientVersion || "version unknown"}
                </p>
              </button>
            )) || <Empty>No reports.</Empty>}
          </div>
          {selected ? (
            <form className="card self-start p-5" onSubmit={save}>
              <h2 className="font-semibold">Triage report</h2>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <select
                  className="field"
                  value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value })}
                >
                  {["OPEN", "TRIAGED", "IN_PROGRESS", "RESOLVED", "CLOSED"].map(
                    (x) => (
                      <option key={x}>{x}</option>
                    ),
                  )}
                </select>
                <select
                  className="field"
                  value={form.severity}
                  onChange={(e) =>
                    setForm({ ...form, severity: e.target.value })
                  }
                >
                  {["LOW", "MEDIUM", "HIGH", "CRITICAL"].map((x) => (
                    <option key={x}>{x}</option>
                  ))}
                </select>
              </div>
              {[
                ["Root cause", "rootCause"],
                ["Internal resolution notes", "resolutionNotes"],
                ["Safe workaround", "workaround"],
                ["Public explanation", "publicExplanation"],
              ].map(([l, k]) => (
                <label className="mt-4 block" key={k}>
                  <span className="label">{l}</span>
                  <textarea
                    className="field min-h-20"
                    value={form[k]}
                    onChange={(e) => setForm({ ...form, [k]: e.target.value })}
                  />
                </label>
              ))}
              <label className="mt-4 flex gap-3 text-sm">
                <input
                  type="checkbox"
                  checked={form.publicApproved}
                  onChange={(e) =>
                    setForm({ ...form, publicApproved: e.target.checked })
                  }
                />
                Approve sanitized public guidance
              </label>
              <button className="button button-primary mt-4">
                <Save size={15} />
                Save triage
              </button>
            </form>
          ) : (
            <div className="card grid min-h-64 place-items-center p-8 text-center text-sm text-[var(--muted)]">
              Select a report to review.
            </div>
          )}
        </div>
      </Load>
    </Gate>
  );
}
