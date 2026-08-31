import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  ArrowRight,
  Copy,
  ExternalLink,
  RefreshCw,
  Search,
} from "lucide-react";
import PublicSearch from "./PublicSearch";
export default function GlobalInteractions() {
  const [menu, setMenu] = useState(),
    firstItem = useRef(),
    navigate = useNavigate(),
    route = useLocation();
  useEffect(() => setMenu(), [route.pathname]);
  useEffect(() => {
    const context = (e) => {
        e.preventDefault();
        setMenu({
          x: Math.max(8, Math.min(e.clientX, innerWidth - 225)),
          y: Math.max(8, Math.min(e.clientY, innerHeight - 270)),
          selected: getSelection()?.toString().trim(),
          link: e.target.closest?.("a")?.href,
        });
      },
      dismiss = () => setMenu(),
      key = (e) => {
        if (e.key === "Escape") setMenu();
      };
    document.addEventListener("contextmenu", context);
    document.addEventListener("click", dismiss);
    document.addEventListener("keydown", key);
    addEventListener("blur", dismiss);
    return () => {
      document.removeEventListener("contextmenu", context);
      document.removeEventListener("click", dismiss);
      document.removeEventListener("keydown", key);
      removeEventListener("blur", dismiss);
    };
  }, []);
  useEffect(() => {
    if (menu) setTimeout(() => firstItem.current?.focus(), 0);
  }, [menu]);
  const actions = [
    ["Back", ArrowLeft, () => navigate(-1)],
    ["Forward", ArrowRight, () => navigate(1)],
    ["Reload", RefreshCw, () => location.reload()],
    [
      "Copy page link",
      Copy,
      () => navigator.clipboard.writeText(location.href),
    ],
    ...(menu?.link
      ? [
          [
            "Open link in new tab",
            ExternalLink,
            () => open(menu.link, "_blank", "noopener"),
          ],
        ]
      : []),
    ...(menu?.selected
      ? [
          [
            "Search selected topic",
            Search,
            () =>
              dispatchEvent(
                new CustomEvent("prysm:search", {
                  detail: { query: menu.selected },
                }),
              ),
          ],
        ]
      : []),
  ];
  return (
    <>
      <PublicSearch />
      {menu && (
        <div
          className="context-menu"
          role="menu"
          aria-label="Page actions"
          style={{ left: menu.x, top: menu.y }}
          onClick={(e) => e.stopPropagation()}
        >
          {actions.map(([label, Icon, action], i) => (
            <button
              ref={i === 0 ? firstItem : null}
              role="menuitem"
              key={label}
              onClick={() => {
                action();
                setMenu();
              }}
            >
              <Icon size={14} />
              <span>{label}</span>
            </button>
          ))}
        </div>
      )}
    </>
  );
}
