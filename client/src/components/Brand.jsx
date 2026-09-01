import { Link } from "react-router-dom";
export default function Brand({ compact = false }) {
  return (
    <Link
      to="/"
      className="brand flex items-center gap-3"
      aria-label="Prysm Intelligence home"
    >
      <span className="brand-mark" aria-hidden="true">
        <img
          className="brand-light"
          src="/assets/logo-white.png"
          alt=""
        />
        <img className="brand-dark" src="/assets/logo-dark.png" alt="" />
      </span>
      <span className={compact ? "sr-only" : "font-semibold tracking-[-.02em]"}>
        Prysm <span className="text-[var(--muted)]">Intelligence</span>
      </span>
    </Link>
  );
}
