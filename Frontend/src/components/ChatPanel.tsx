import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import AidaLogo from "./AidaLogo";
import type { AssistantState, ChatConversation } from "../types/chat";
import "./ChatPanel.css";

type ChatPanelProps = {
  conversation: ChatConversation | null;
  assistantState: AssistantState;
  isBusy: boolean;
  error: string | null;
  onSend: (text: string) => void;
  onOpenSidebar: () => void;
};

export default function ChatPanel({
  conversation,
  assistantState,
  isBusy,
  error,
  onSend,
  onOpenSidebar,
}: ChatPanelProps) {
  const [draft, setDraft] = useState("");
  const [draftFor, setDraftFor] = useState(conversation?.id);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const hasMessages = (conversation?.messages.length ?? 0) > 0;
  const lastMessage = conversation?.messages.at(-1);

  // Clear the draft when switching conversation. Done during render, not in an
  // effect, so React doesn't paint the old draft first and then render again.
  if (conversation?.id !== draftFor) {
    setDraftFor(conversation?.id);
    setDraft("");
  }

  useEffect(() => {
    textareaRef.current?.focus();
  }, [conversation?.id]);

  useEffect(() => {
    const element = textareaRef.current;
    if (!element) return;
    element.style.height = "auto";
    element.style.height = `${Math.min(element.scrollHeight, 176)}px`;
  }, [draft]);

  useEffect(() => {
    const element = scrollRef.current;
    if (element) element.scrollTop = element.scrollHeight;
  }, [conversation?.id, conversation?.messages, lastMessage?.content]);

  function submit() {
    if (!draft.trim() || isBusy) return;
    onSend(draft);
    setDraft("");
  }

  return (
    <main className="chat-panel">
      <button
        className="chat-panel__open-sidebar"
        type="button"
        onClick={onOpenSidebar}
        title="Show sidebar"
        aria-label="Show sidebar"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
          <rect x="3" y="4" width="18" height="16" rx="2" />
          <path d="M9 4v16" />
        </svg>
      </button>

      <section className={`chat-panel__stage ${hasMessages ? "chat-panel__stage--active" : "chat-panel__stage--empty"}`}>
        <div className="chat-panel__logo" aria-hidden="true">
          <AidaLogo
            state={assistantState}
            size={hasMessages ? 390 : 270}
            faded={hasMessages}
          />
        </div>

        {!hasMessages ? (
          <div className="chat-panel__empty-copy">
            <h1>Where shall we begin?</h1>
            {error && <p className="chat-panel__error" role="alert">{error}</p>}
          </div>
        ) : (
          <div className="chat-panel__scroll" ref={scrollRef}>
            <div className="chat-panel__messages" aria-live="polite" aria-relevant="additions text">
              {conversation?.messages.map((message) => (
                <article
                  key={message.id}
                  className={`chat-panel__message chat-panel__message--${message.role}`}
                >
                  {message.role === "user" ? (
                    <div className="chat-panel__user-bubble">{message.content}</div>
                  ) : (
                    <div className="chat-panel__assistant-text">
                      {message.content ? (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                      ) : (
                        <span className="chat-panel__cursor" aria-label="Responding" />
                      )}
                    </div>
                  )}
                </article>
              ))}
              {assistantState === "thinking" && (
                <div className="chat-panel__thinking" aria-label="AIDA is thinking">
                  <span /><span /><span />
                </div>
              )}
              {error && <div className="chat-panel__error" role="alert">{error}</div>}
            </div>
          </div>
        )}
      </section>

      <div className="chat-panel__composer-wrap">
        <div className="chat-panel__composer">
          <textarea
            ref={textareaRef}
            rows={1}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
                event.preventDefault();
                submit();
              }
            }}
            placeholder="Message AIDA..."
            aria-label="Message AIDA"
            disabled={isBusy}
          />
          <button
            type="button"
            className="chat-panel__send"
            onClick={submit}
            disabled={!draft.trim() || isBusy}
            aria-label="Send"
            title="Send"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M12 19V5M5 12l7-7 7 7" />
            </svg>
          </button>
        </div>
      </div>
    </main>
  );
}