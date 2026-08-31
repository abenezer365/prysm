import { useEffect, useRef, useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { ChevronDown, Menu, Search, X } from "lucide-react";
import Brand from "./Brand";
import ThemeButton from "./ThemeButton";
import { megaGroups } from "../config/publicRegistry";
export default function PublicHeader() {
  const [active, setActive] = useState(null),
    [mobile, setMobile] = useState(false),
    [hidden, setHidden] = useState(false),
    [compact, setCompact] = useState(false),
    timer = useRef(),
    lastY = useRef(0);
  const open = (i) => {
      clearTimeout(timer.current);
      setActive(i);
      setHidden(false);
    },
    close = () => {
      timer.current = setTimeout(() => setActive(null), 180);
    };
  useEffect(() => {
    const scroll = () => {
      const y = Math.max(scrollY, 0),
        delta = y - lastY.current;
      setCompact(y > 18);
      if (active === null && !mobile) {
        if (delta > 7 && y > 110) setHidden(true);
        else if (delta < 0) setHidden(false);
      }
      lastY.current = y;
    };
    addEventListener("scroll", scroll, { passive: true });
    return () => removeEventListener("scroll", scroll);
  }, [active, mobile]);
  useEffect(() => {
    const key = (e) => {
      if (e.key === "Escape") {
        setActive(null);
        setMobile(false);
        setHidden(false);
      }
    };
    document.addEventListener("keydown", key);
    return () => document.removeEventListener("keydown", key);
  }, []);
  const current = active === null ? null : megaGroups[active];
  return (
    <header
      className={`public-header ${hidden ? "header-hidden" : ""} ${compact ? "header-compact" : ""}`}
      onMouseLeave={close}
    >
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <div className="utility-bar">
        <div className="shell">
          <span>Prysm Intelligence · Financial intelligence platform</span>
          <nav aria-label="Utility navigation">
            <Link to="/report/system-status">System status</Link>
            <Link to="/docs">Documentation</Link>
            <Link to="/contact">Contact</Link>
          </nav>
        </div>
      </div>
      <div className="shell primary-nav">
        <Brand />
        <nav
          className="desktop-navigation"
          aria-label="Main navigation"
          onMouseEnter={() => clearTimeout(timer.current)}
        >
          {megaGroups.map((g, i) => (
            <button
              key={g.label}
              className={active === i ? "active" : ""}
              aria-expanded={active === i}
              aria-controls="mega-navigation"
              onMouseEnter={() => open(i)}
              onFocus={() => open(i)}
              onClick={() => setActive(active === i ? null : i)}
            >
              {g.label}
              <ChevronDown size={13} />
            </button>
          ))}
        </nav>
        <div className="nav-actions">
          <button
            className="icon-link"
            onClick={() => dispatchEvent(new Event("prysm:search"))}
            aria-label="Search Prysm"
            title="Search (Ctrl K)"
          >
            <Search size={17} />
          </button>
          <ThemeButton />
          <Link to="/login" className="button button-primary">
            Sign in
          </Link>
          <button
            className="mobile-toggle"
            onClick={() => {
              setMobile(!mobile);
              setHidden(false);
            }}
            aria-expanded={mobile}
            aria-label={
              mobile ? "Close site navigation" : "Open site navigation"
            }
          >
            {mobile ? <X /> : <Menu />}
          </button>
        </div>
      </div>
      <div
        className={`mega-overlay ${current ? "visible" : ""}`}
        aria-hidden="true"
      />
      {current && (
        <section
          id="mega-navigation"
          className="mega-panel"
          onMouseEnter={() => clearTimeout(timer.current)}
          onMouseLeave={close}
          aria-label={`${current.label} navigation`}
        >
          <div className="shell mega-inner">
            <div className="mega-intro">
              <p className="eyebrow">Explore {current.label}</p>
              <h2>{current.summary}</h2>
              <Link
                to={current.featured}
                onClick={() => setActive(null)}
                className="knowledge-link"
              >
                Open {current.label.toLowerCase()} overview
              </Link>
            </div>
            <div className="mega-columns">
              {current.columns.map(([title, items]) => (
                <div key={title}>
                  <h3>{title}</h3>
                  {items.map(([name, path]) => (
                    <Link key={path} to={path} onClick={() => setActive(null)}>
                      {name}
                    </Link>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
      {mobile && (
        <nav className="mobile-navigation" aria-label="Mobile navigation">
          {megaGroups.map((g) => (
            <details key={g.label}>
              <summary>{g.label}</summary>
              <Link to={g.featured} onClick={() => setMobile(false)}>
                Overview
              </Link>
              {g.columns
                .flatMap((x) => x[1])
                .map(([name, path], i) => (
                  <Link
                    key={`${path}-${i}`}
                    to={path}
                    onClick={() => setMobile(false)}
                  >
                    {name}
                  </Link>
                ))}
            </details>
          ))}
          <NavLink to="/login" onClick={() => setMobile(false)}>
            Sign in
          </NavLink>
        </nav>
      )}
    </header>
  );
}
