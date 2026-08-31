import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { docPages, publicPages } from "../config/publicRegistry";
export default function RouteManager() {
  const { pathname } = useLocation();
  useEffect(() => {
    const page = publicPages[pathname],
      doc = docPages[pathname],
      title =
        pathname === "/"
          ? "Prysm Intelligence | Financial intelligence"
          : pathname === "/about"
            ? "About Prysm Intelligence"
            : pathname === "/docs"
              ? "Prysm Intelligence Documentation"
              : page?.title || doc?.[0] || "Prysm Intelligence",
      description =
        page?.description ||
        doc?.[1] ||
        "Evidence-led financial intelligence, graph analysis, documentation, and responsible investigation.",
      url = `${location.origin}${pathname}`;
    document.title = title.includes("Prysm")
      ? title
      : `${title} | Prysm Intelligence`;
    const meta = (selector, attribute, name, value) => {
      let element = document.querySelector(selector);
      if (!element) {
        element = document.createElement("meta");
        element.setAttribute(attribute, name);
        document.head.appendChild(element);
      }
      element.content = value;
    };
    meta('meta[name="description"]', "name", "description", description);
    meta('meta[property="og:title"]', "property", "og:title", title);
    meta(
      'meta[property="og:description"]',
      "property",
      "og:description",
      description,
    );
    meta('meta[property="og:url"]', "property", "og:url", url);
    meta('meta[name="twitter:title"]', "name", "twitter:title", title);
    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement("link");
      canonical.rel = "canonical";
      document.head.appendChild(canonical);
    }
    canonical.href = url;
    scrollTo({ top: 0, behavior: "instant" });
    requestAnimationFrame(() =>
      document.querySelector("main h1")?.focus?.({ preventScroll: true }),
    );
  }, [pathname]);
  return null;
}
