import { useState } from "react";
import { api, friendlyError } from "../services/api";
const configs = {
  contact: {
    title: "Contact Abyssinia Associates",
    intro:
      "Send a project or research inquiry. Messages are stored securely for administrative follow-up.",
    fields: [
      ["name", "Name"],
      ["email", "Email"],
      ["subject", "Subject (optional)"],
      ["message", "Message"],
    ],
  },
  bug: {
    title: "Report a problem",
    intro:
      "Describe what happened without sharing passwords, tokens, or restricted information.",
    fields: [
      ["reporterName", "Name (optional)"],
      ["contactEmail", "Contact email (optional)"],
      ["clientVersion", "Client version (optional)"],
      ["description", "What happened"],
    ],
  },
  access: {
    title: "Request controlled access",
    intro:
      "Prysm does not offer unrestricted self-registration. Applications undergo manual review before any account is activated.",
    fields: [
      ["displayName", "Display name"],
      ["email", "Email"],
      ["profession", "Profession"],
      ["organization", "Organization (optional)"],
      ["organizationRole", "Role in organization (optional)"],
      ["phone", "Phone (optional)"],
      ["reason", "Reason for access"],
      ["justification", "Detailed justification"],
    ],
  },
};
const optional = new Set([
  "subject",
  "reporterName",
  "contactEmail",
  "clientVersion",
  "organization",
  "organizationRole",
  "phone",
]);
export default function FormPage({ kind }) {
  const c = configs[kind];
  const [data, setData] = useState({}),
    [state, setState] = useState("idle"),
    [error, setError] = useState(null);
  async function submit(e) {
    e.preventDefault();
    setError(null);
    setState("loading");
    try {
      const clean = Object.fromEntries(
        Object.entries(data).filter(([, value]) => value !== ""),
      );
      if (kind === "access") await api.apply(clean);
      else if (kind === "contact") await api.contact(clean);
      else await api.bugReport(clean);
      setState("success");
      setData({});
    } catch (err) {
      setError(err);
      setState("error");
    }
  }
  return (
    <div className="shell grid gap-12 py-20 lg:grid-cols-[.8fr_1.2fr]">
      <div>
        <p className="eyebrow">
          {kind === "access" ? "Access review" : "Direct channel"}
        </p>
        <h1 className="page-title mt-5" tabIndex="-1">
          {c.title}
        </h1>
        <p className="muted mt-6 max-w-lg text-lg leading-8">{c.intro}</p>
      </div>
      <form className="card p-7 md:p-10" onSubmit={submit}>
        {c.fields.map(([key, label]) => (
          <div className="mb-5" key={key}>
            <label className="label" htmlFor={key}>
              {label}
            </label>
            {["message", "description", "reason", "justification"].includes(
              key,
            ) ? (
              <textarea
                className="field min-h-32"
                id={key}
                required={!optional.has(key)}
                minLength={
                  key === "justification"
                    ? 100
                    : key === "reason" ||
                        key === "message" ||
                        key === "description"
                      ? 20
                      : undefined
                }
                value={data[key] || ""}
                onChange={(e) => setData({ ...data, [key]: e.target.value })}
              />
            ) : (
              <input
                className="field"
                id={key}
                type={
                  key === "email" || key === "contactEmail" ? "email" : "text"
                }
                required={!optional.has(key)}
                value={data[key] || ""}
                onChange={(e) => setData({ ...data, [key]: e.target.value })}
              />
            )}
          </div>
        ))}
        {state === "success" && (
          <p className="mb-5 rounded-[var(--radius-md)] bg-[var(--accent-soft)] p-3 text-sm">
            Your submission was received successfully.
          </p>
        )}
          {state === "error" && <p className="mb-5 text-sm text-[var(--danger)]">{friendlyError(error)}</p>}
        <button
          disabled={state === "loading"}
          className="button button-primary w-full"
        >
          {state === "loading" ? "Submitting…" : "Submit"}
        </button>
        {kind === "access" && (
          <p className="muted mt-4 text-xs leading-5">
            Submission does not grant access. An authorized officer must review
            and approve the application.
          </p>
        )}
      </form>
    </div>
  );
}
