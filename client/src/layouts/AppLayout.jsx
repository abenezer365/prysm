import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  Bot,
  Bug,
  Clock3,
  FileCheck2,
  FileSearch,
  Gauge,
  Home,
  LogOut,
  Menu,
  Network,
  Newspaper,
  RefreshCw,
  Search,
  Settings,
  UserCheck,
  Users,
  UsersRound,
  X,
} from "lucide-react";
import Brand from "../components/Brand";
import ThemeButton from "../components/ThemeButton";
import { useAuth } from "../context/AuthContext";
const links = [
  ["Dashboard", "/app/dashboard", Gauge],
  ["Search / Case", "/app/search", Search, "subject:read"],
  ["Investigations", "/app/investigations", FileSearch, "investigation:read"],
  ["GNN Maze", "/app/gnn-maze", Network, "graph:read"],
  ["Users", "/app/users", Users, "user:read"],
  ["Access approvals", "/app/access", FileCheck2, "application:review"],
  ["RAG administration", "/app/rag", Bot, "rag:documents:read"],
  ["News", "/app/news", Newspaper, "news:manage"],
  ["Activity log", "/app/activity", Activity],
  ["Bug reports", "/app/bugs", Bug, "bug:manage"],
  ["Beta testers", "/app/beta-testers", UserCheck, "beta:review"],
  ["Contributors", "/app/contributors", UsersRound, "contributor:review"],
  ["Settings", "/app/settings", Settings],
];
const clearanceNames = {
  1: "Restricted",
  2: "Confidential",
  3: "Secret",
  4: "Top Secret",
};
const clearanceBadgeStyles = {
  1: "border-slate-300 bg-slate-100 text-slate-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200",
  2: "border-sky-300 bg-sky-100 text-sky-800 dark:border-sky-700 dark:bg-sky-950 dark:text-sky-200",
  3: "border-amber-300 bg-amber-100 text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200",
  4: "border-red-300 bg-red-100 text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200",
};
export default function AppLayout() {
  const [menu, setMenu] = useState(false),
    [time, setTime] = useState(new Date());
  const auth = useAuth(),
    nav = useNavigate(),
    loc = useLocation();
  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);
  const visible = links.filter(
    ([, , , permission]) => !permission || auth.can(permission),
  );
  return (
    <div className="min-h-screen bg-[var(--bg)]">
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-[var(--border)] bg-[var(--surface)] p-4 transition-transform lg:translate-x-0 ${menu ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="flex items-center justify-between px-2 py-2">
          <Brand />
          <button className="lg:hidden" onClick={() => setMenu(false)}>
            <X />
          </button>
        </div>
        <div className="mt-5 rounded-lg bg-[var(--surface-2)] px-4 py-5 text-center">
          <div className="relative mx-auto mb-5 w-fit">
            <div className="flex h-24 w-24 items-center justify-center overflow-hidden rounded-full bg-[var(--accent)] text-3xl font-semibold text-white ring-4 ring-[var(--surface)]">
              {auth.user?.profileImageUrl ? (
                <img
                  alt={`${auth.user?.displayName || "User"} profile`}
                  className="h-full w-full object-cover"
                  src={auth.user.profileImageUrl}
                />
              ) : (
                (auth.user?.displayName ||
                  auth.user?.email ||
                  "P")[0].toUpperCase()
              )}
            </div>
            <span
              className={`absolute -bottom-2 left-[68%] whitespace-nowrap rounded-full border px-2.5 py-1 text-[10px] font-bold shadow-sm ${clearanceBadgeStyles[auth.clearance] || clearanceBadgeStyles[1]}`}
            >
              {clearanceNames[auth.clearance] || "Pending"} :{" "}
              {auth.clearance || 1}
            </span>
          </div>
          <p className="mt-3 truncate text-sm font-semibold">
            {auth.user?.displayName || auth.user?.email || "Authorized user"}
          </p>
          <p className="mt-1 text-xs text-[var(--muted)]">
            Investigation dashboard
          </p>
        </div>
        <nav className="mt-4 flex-1 space-y-0.5 overflow-y-auto">
          {visible.map(([n, h, I]) => (
            <NavLink
              onClick={() => setMenu(false)}
              key={h}
              to={h}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium ${isActive ? "bg-[var(--accent-soft)] text-[var(--accent)]" : "text-[var(--muted)] hover:bg-[var(--surface-2)] hover:text-[var(--text)]"}`
              }
            >
              <I size={16} />
              {n}
            </NavLink>
          ))}
        </nav>
        <button
          onClick={auth.logout}
          className="flex items-center gap-3 px-3 py-2 text-sm text-[var(--muted)]"
        >
          <LogOut size={17} />
          Sign out
        </button>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-[var(--border)] bg-[color:var(--bg)]/95 px-4 backdrop-blur md:px-7">
          <div className="flex items-center gap-1">
            <button className="mr-2 lg:hidden" onClick={() => setMenu(true)}>
              <Menu />
            </button>
            <button
              className="button button-secondary !p-2"
              onClick={() => nav("/")}
              aria-label="Public home"
            >
              <Home size={16} />
            </button>
            <button
              className="button button-secondary !p-2"
              onClick={() => nav(-1)}
              aria-label="Back"
            >
              <ArrowLeft size={16} />
            </button>
            <button
              className="button button-secondary !p-2"
              onClick={() => nav(1)}
              aria-label="Forward"
            >
              <ArrowRight size={16} />
            </button>
            <button
              className="button button-secondary !p-2"
              onClick={() => window.location.reload()}
              aria-label="Reload"
            >
              <RefreshCw size={16} />
            </button>
          </div>
          <div className="flex items-center gap-2">
            <span className="muted hidden items-center gap-2 font-mono text-xs sm:flex">
              <Clock3 size={14} />
              {time.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
            <ThemeButton />
          </div>
        </header>
        <main className="p-4 md:p-8">
          <div className="mx-auto max-w-[1450px]" key={loc.pathname}>
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
