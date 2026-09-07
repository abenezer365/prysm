import { useEffect, useRef, useState } from "react";
import { Bot, Send } from "lucide-react";
import { api, friendlyError } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useParams } from "react-router-dom";
import { toast } from "sonner";

export default function InvestigationChat({ investigationId, subjectId, cutoffAt }) {
  const route = useParams();
  investigationId = investigationId || route.id;
  const { token, can, permissions } = useAuth();
  const authorized = permissions.includes("chat:authorized");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const log = useRef(null);

  useEffect(() => {
    if (!authorized) return undefined;
    let active = true;
    api.conversation(token, investigationId).then((response) => {
      if (!active) return;
      setMessages((response.data || []).slice().reverse().flatMap((entry) => [
        { role: "user", text: entry.question },
        { role: "assistant", text: entry.answer, sources: entry.sources || [] },
      ]));
    }).catch(() => {});
    return () => { active = false; };
  }, [token, investigationId, authorized]);

  useEffect(() => {
    log.current?.scrollTo({ top: log.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  async function send(event) {
    event.preventDefault();
    const text = question.trim();
    if (!text || busy) return;
    setQuestion("");
    setMessages((current) => [...current, { role: "user", text }]);
    setBusy(true);
    setError(null);
    try {
      const response = await api.authorizedChat(token, { question: text, investigationId, ...(subjectId ? { subjectId } : {}), ...(cutoffAt ? { cutoffAt } : {}), ...(conversationId ? { conversationId } : {}) });
      setConversationId(response.conversationId);
      setMessages((current) => [...current, { role: "assistant", text: response.answer, sources: response.sources || [] }]);
    } catch (value) { setError(value); toast.error(friendlyError(value)); }
    finally { setBusy(false); }
  }

  if (!can("chat:authorized")) return null;
  return <section className="case-chat card mt-6 overflow-hidden">
    <header className="border-b border-[var(--border)] p-6"><div className="flex items-center gap-3"><Bot size={19}/><h2 className="font-semibold">Ask Prysm about this investigation</h2></div><p className="muted mt-2 text-sm">Generated explanations use the stored analysis and authorized evidence. They explain findings but never become evidence themselves.</p></header>
    <div ref={log} className="case-chat-log space-y-4 p-6" aria-live="polite">{messages.length === 0 && <p className="muted text-sm">Ask for the strongest signals, relevant relationships, supporting evidence, or analytical limitations.</p>}{messages.map((message,index) => <article className={`case-chat-message ${message.role}`} key={index}><p className="eyebrow">{message.role === "user" ? "Investigator" : "Generated explanation"}</p><p className="chat-answer mt-2 whitespace-pre-wrap text-sm leading-7">{message.text}</p>{message.sources?.length > 0 && <details className="mt-3 text-xs"><summary>View cited sources ({message.sources.length})</summary><ul>{message.sources.map((source,i)=><li key={i}>{source.title || source.source || `Source ${i+1}`}</li>)}</ul></details>}</article>)}{busy && <div className="chat-thinking" aria-label="Prysm is preparing a response"><i/><i/><i/></div>}{error && <p className="text-sm text-[var(--danger)]">{friendlyError(error)}</p>}</div>
    <form onSubmit={send} className="flex gap-2 border-t border-[var(--border)] p-4"><label className="sr-only" htmlFor="case-question">Question about this investigation</label><input id="case-question" className="field" value={question} onChange={(event)=>setQuestion(event.target.value)} maxLength={4000} placeholder="Ask about evidence, relationships, or limitations"/><button className="button button-primary" disabled={busy}><Send size={16}/>Send</button></form>
  </section>;
}
