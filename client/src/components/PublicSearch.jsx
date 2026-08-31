import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Search, X } from "lucide-react";
import { searchTopics } from "../config/searchIndex";
export default function PublicSearch() {
  const [open, setOpen] = useState(false),
    [query, setQuery] = useState(""),
    [active, setActive] = useState(0);
  const input = useRef(),
    navigate = useNavigate(),
    results = useMemo(() => searchTopics(query), [query]);
  useEffect(() => {
    const key = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen(true);
      }
    };
    const custom = (e) => {
      setQuery(e.detail?.query || "");
      setOpen(true);
    };
    window.addEventListener("keydown", key);
    window.addEventListener("prysm:search", custom);
    return () => {
      window.removeEventListener("keydown", key);
      window.removeEventListener("prysm:search", custom);
    };
  }, []);
  useEffect(() => {
    if (open) {
      setActive(0);
      setTimeout(() => input.current?.focus(), 20);
    }
  }, [open]);
  function go(item) {
    setOpen(false);
    setQuery("");
    navigate(item.route);
  }
  function keys(e) {
    if (e.key === "Escape") setOpen(false);
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((x) => Math.min(x + 1, results.length - 1));
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((x) => Math.max(x - 1, 0));
    }
    if (e.key === "Enter" && results[active]) {
      e.preventDefault();
      go(results[active]);
    }
  }
  if (!open) return null;
  return (
    <div
      className="search-backdrop"
      role="presentation"
      onMouseDown={(e) => e.target === e.currentTarget && setOpen(false)}
    >
      <section
        className="search-dialog"
        role="dialog"
        aria-modal="true"
        aria-label="Search Prysm knowledge"
      >
        <div className="search-input-row">
          <Search size={18} />
          <label className="sr-only" htmlFor="public-search">
            Search pages, topics, and documentation
          </label>
          <input
            ref={input}
            id="public-search"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setActive(0);
            }}
            onKeyDown={keys}
            placeholder="Search Prysm knowledge…"
            autoComplete="off"
          />
          <kbd>Ctrl K</kbd>
          <button onClick={() => setOpen(false)} aria-label="Close search">
            <X size={18} />
          </button>
        </div>
        <div
          className="search-results"
          role="listbox"
          aria-label="Search results"
        >
          {results.length ? (
            results.map((item, i) => (
              <button
                key={`${item.route}-${item.title}`}
                role="option"
                aria-selected={i === active}
                className={i === active ? "active" : ""}
                onMouseEnter={() => setActive(i)}
                onClick={() => go(item)}
              >
                <span>
                  <strong>{item.title}</strong>
                  <small>
                    {item.category} · {item.description}
                  </small>
                </span>
                <ArrowRight size={15} />
              </button>
            ))
          ) : (
            <p className="search-empty">
              No matching topic. Try provenance, AML, graph, privacy, or
              authorization.
            </p>
          )}
        </div>
        <footer>
          <span>
            {results.length} result{results.length === 1 ? "" : "s"}
          </span>
          <span>↑↓ select　Enter open　Esc close</span>
        </footer>
      </section>
    </div>
  );
}
