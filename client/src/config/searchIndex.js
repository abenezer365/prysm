import { docPages, glossary, publicPages } from "./publicRegistry.js";
const clean = (value) =>
  String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
const aliases = {
  AML: ["anti money laundering", "suspicious activity"],
  GNN: ["graph neural network", "network model"],
  RAG: ["retrieval augmented generation", "grounded chat"],
  Provenance: ["source history", "lineage"],
  Clearance: ["access level", "classification"],
};
const staticEntries = [
  [
    "Prysm Intelligence",
    "Evidence-led financial intelligence research and investigation.",
    "Organization",
    "/",
    "home platform overview",
  ],
  [
    "About Prysm",
    "Origin, principles, architecture, team, and project evolution.",
    "Organization",
    "/about",
    "story mission people",
  ],
  [
    "Documentation",
    "Technical architecture, APIs, security, data, chat, and integration.",
    "Resources",
    "/docs",
    "developer technical guide",
  ],
  [
    "Frequently asked questions",
    "Practical answers about scope, access, models, and responsible use.",
    "Resources",
    "/faq",
    "help questions",
  ],
  [
    "Request access",
    "Apply for controlled access to the intelligence workspace.",
    "Organization",
    "/request-access",
    "application get started",
  ],
];
const entries = [
  ...staticEntries.map(([title, description, category, route, keywords]) => ({
    title,
    description,
    category,
    route,
    keywords,
  })),
  ...Object.entries(publicPages).map(([route, p]) => ({
    route,
    title: p.title,
    description: p.description,
    category: p.category,
    keywords: p.sections.map((s) => s.join(" ")).join(" "),
  })),
  ...Object.entries(docPages).map(([route, [title, description]]) => ({
    route,
    title,
    description,
    category: "Documentation",
    keywords: `technical api ${title}`,
  })),
  ...Object.entries(glossary).map(([title, description]) => ({
    route: "/docs/glossary",
    title,
    description,
    category: "Glossary",
    keywords: (aliases[title] || []).join(" "),
  })),
];
export const searchIndex = entries.map((x) => ({
  ...x,
  searchable: clean(
    `${x.title} ${x.description} ${x.category} ${x.keywords} ${(aliases[x.title] || []).join(" ")}`,
  ),
}));
export function searchTopics(query) {
  const terms = clean(query).split(" ").filter(Boolean);
  if (!terms.length) return searchIndex.slice(0, 8);
  return searchIndex
    .map((item) => {
      const title = clean(item.title),
        description = clean(item.description);
      let score = 0;
      for (const term of terms) {
        if (title === term) score += 12;
        else if (title.startsWith(term)) score += 8;
        else if (title.includes(term)) score += 5;
        if (description.includes(term)) score += 2;
        if (item.searchable.includes(term)) score += 1;
      }
      if (terms.every((t) => item.searchable.includes(t))) score += 5;
      return { ...item, score };
    })
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score || a.title.localeCompare(b.title))
    .slice(0, 12);
}
