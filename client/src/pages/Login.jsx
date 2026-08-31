import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import Brand from "../components/Brand";
import ThemeButton from "../components/ThemeButton";
import { useAuth } from "../context/AuthContext";
import { friendlyError } from "../services/api";
import { toast } from "sonner";
export default function Login() {
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [error, setError] = useState(null),
    [busy, setBusy] = useState(false);
  const auth = useAuth(),
    navigate = useNavigate(),
    location = useLocation();
  if (auth.token) return <Navigate to="/app/dashboard" replace />;
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await auth.login({ email, password, deviceInfo: navigator.userAgent });
      toast.success("Signed in successfully.");
      navigate(location.state?.from || "/app/dashboard", { replace: true });
    } catch (err) {
      setError(err);
      toast.error(friendlyError(err));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="hidden bg-[#0d0d0d] p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <Brand />
        <div>
          <p className="font-mono text-xs uppercase tracking-[.18em] text-white/60">
            Controlled workspace
          </p>
          <h1 className="mt-6 max-w-xl text-5xl font-semibold leading-[1.02] tracking-[-.05em]">
            Evidence, relationships, and decisions in one line of sight.
          </h1>
        </div>
        <p className="text-sm text-white/50">
          Authorized access only. Sessions are audited.
        </p>
      </div>
      <div className="flex items-center justify-center p-6">
        <div className="w-full max-w-md">
          <div className="mb-12 flex justify-between lg:justify-end">
            <div className="lg:hidden">
              <Brand />
            </div>
            <ThemeButton />
          </div>
          <p className="eyebrow">Sign in</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight">
            Return to your workspace
          </h2>
          <p className="muted mt-3">Use your approved Prysm credentials.</p>
          <form className="mt-9" onSubmit={submit}>
            <label className="label" htmlFor="email">
              Email
            </label>
            <input
              className="field mb-5"
              id="email"
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <label className="label" htmlFor="password">
              Password
            </label>
            <input
              className="field"
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && (
              <p className="mt-4 text-sm text-[var(--danger)]">
                {friendlyError(error)}{" "}
                {error.requestId && (
                  <span className="mono block mt-1">
                    Request {error.requestId}
                  </span>
                )}
              </p>
            )}
            <button
              disabled={busy}
              className="button button-primary mt-6 w-full"
            >
              {busy ? "Verifying…" : "Sign in"}
            </button>
          </form>
          <p className="muted mt-7 text-center text-sm">
            No account?{" "}
            <Link
              className="font-semibold text-[var(--accent)]"
              to="/request-access"
            >
              Request access
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
