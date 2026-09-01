import { useEffect, useState } from "react";
import { Bot, Send, X } from "lucide-react";
import { api, friendlyError } from "../services/api";
export default function ChatWidget() {
  const [open, setOpen] = useState(false),
    [question, setQuestion] = useState(""),
    [messages, setMessages] = useState([]),
    [busy, setBusy] = useState(false),
    [conversationId, setConversationId] = useState(null);
  useEffect(() => {
    document.body.dataset.chatOpen = open ? "true" : "false";
    return () => delete document.body.dataset.chatOpen;
  }, [open]);
  async function ask(q) {
    setMessages((m) => [...m, { role: "user", text: q }]);
    setBusy(true);
    try {
      const r = await api.publicChat({
        question: q,
        ...(conversationId ? { conversationId } : {}),
      });
      setConversationId(r.conversationId);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: r.answer,
          sources: r.sources || [],
          requestId: r.requestId,
        },
      ]);
    } catch (err) {
      const unavailable = err.status === 503 || err.code === "RAG_UNAVAILABLE";
      setMessages((m) => [
        ...m,
        {
          role: "error",
          text: unavailable
            ? "The public knowledge service is not available. The backend or retrieval service may be offline."
            : friendlyError(err),
          requestId: err.requestId,
          retry: q,
        },
      ]);
    } finally {
      setBusy(false);
    }
  }
  async function send(e) {
    e.preventDefault();
    if (!question.trim() || busy) return;
    const q = question.trim();
    setQuestion("");
    await ask(q);
  }
  return (
    <div className="fixed bottom-5 right-5 z-50">
      {open && (
        <section
          className="chat-panel mb-3 flex h-[min(600px,78vh)] w-[min(430px,calc(100vw-24px))] flex-col overflow-hidden rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow)]"
          aria-label="Prysm assistant"
        >
          <header className="flex items-center justify-between border-b border-[var(--border)] p-4">
            <div>
              <p className="font-semibold">Prysm AI</p>
              <p className="muted text-xs">Public knowledge only</p>
            </div>
            <button onClick={() => setOpen(false)} aria-label="Close chat">
              <X size={19} />
            </button>
          </header>
          <div
            className="flex-1 space-y-3 overflow-y-auto p-4"
            aria-live="polite"
            aria-busy={busy}
          >
            {messages.length === 0 && (
              <div className="muted text-sm leading-6">
                Ask about Prysm, graph intelligence, ethical AI, or access. This
                public mode never receives investigation context.
              </div>
            )}
            {messages.map((m, i) => (
              <div
                key={i}
                className={`max-w-[90%] rounded-[var(--radius-md)] p-4 text-sm leading-6 ${m.role === "user" ? "chat-message-user ml-auto" : "chat-message-assistant"} ${m.role === "error" ? "text-[var(--danger)]" : ""}`}
              >
                <p>{m.text}</p>
                {m.sources?.length > 0 && (
                  <details className="mt-2 text-xs">
                    <summary>
                      {m.sources.length} source{m.sources.length > 1 ? "s" : ""}
                    </summary>
                    {m.sources.map((s, j) => (
                      <p className="mt-1" key={j}>
                        {s.title || s.source || `Source ${j + 1}`}
                      </p>
                    ))}
                  </details>
                )}
                {m.retry && (
                  <button
                    className="mt-2 text-xs underline"
                    disabled={busy}
                    onClick={() => ask(m.retry)}
                  >
                    Retry question
                  </button>
                )}
              </div>
            ))}
            {busy && (
              <p className="muted text-sm">Consulting public knowledge...</p>
            )}
          </div>
          <form
            onSubmit={send}
            className="flex gap-2 border-t border-[var(--border)] p-3"
          >
            <label className="sr-only" htmlFor="chat-question">
              Question
            </label>
            <input
              id="chat-question"
              className="field"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask Prysm..."
              maxLength={4000}
            />
            <button
              className="button button-primary !px-3"
              aria-label="Send question"
              disabled={busy}
            >
              <Send size={17} />
            </button>
          </form>
        </section>
      )}
      <button
        onClick={() => setOpen(!open)}
        className="chat-launcher ml-auto flex h-12 w-12 items-center justify-center rounded-full"
        aria-label="Open Prysm assistant"
      >
        <Bot size={21} />
      </button>
    </div>
  );
}
