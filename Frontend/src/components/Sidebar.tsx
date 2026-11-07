import AidaLogo from "./AidaLogo";
import type { ChatConversation } from "../types/chat";
import "./Sidebar.css";

type SidebarProps = {
  conversations: ChatConversation[];
  activeId: string | null;
  collapsed: boolean;
  mobileOpen: boolean;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  onClose: () => void;
};

export default function Sidebar({
  conversations,
  activeId,
  collapsed,
  mobileOpen,
  onSelect,
  onNewChat,
  onClose,
}: SidebarProps) {
  return (
    <aside
      className={[
        "sidebar",
        collapsed && "sidebar--collapsed",
        mobileOpen && "sidebar--mobile-open",
      ]
        .filter(Boolean)
        .join(" ")}
      aria-label="Conversation sidebar"
      inert={collapsed && !mobileOpen}
    >
      <div className="sidebar__inner">
        <div className="sidebar__top">
          <div className="sidebar__brand" aria-label="AIDA">
            <AidaLogo size={28} animated={false} />
            <span>AIDA</span>
          </div>
          <button
            className="sidebar__icon-button"
            type="button"
            onClick={onClose}
            aria-label="Hide sidebar"
            title="Hide sidebar"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
              <rect x="3" y="4" width="18" height="16" rx="2" />
              <path d="M9 4v16" />
              <path d="m15 9-3 3 3 3" />
            </svg>
          </button>
        </div>

        <button className="sidebar__new" type="button" onClick={onNewChat}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
            <path d="M12 5v14M5 12h14" />
          </svg>
          <span>New chat</span>
        </button>

        <nav className="sidebar__conversations" aria-label="Conversations">
          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              type="button"
              className={[
                "sidebar__conversation",
                conversation.id === activeId && "sidebar__conversation--active",
              ]
                .filter(Boolean)
                .join(" ")}
              onClick={() => onSelect(conversation.id)}
              aria-current={conversation.id === activeId ? "page" : undefined}
              title={conversation.title}
            >
              {conversation.title}
            </button>
          ))}
        </nav>
      </div>
    </aside>
  );
}
