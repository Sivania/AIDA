import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import Sidebar from "./components/Sidebar";
import { useChat } from "./hooks/useChat";
import "./App.css";

export default function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const {
    conversations,
    activeConversation,
    activeId,
    assistantState,
    isBusy,
    error,
    newChat,
    selectChat,
    sendMessage,
  } = useChat();

  function openSidebar() {
    if (window.matchMedia("(max-width: 760px)").matches) {
      setMobileSidebarOpen(true);
    } else {
      setSidebarCollapsed(false);
    }
  }

  function closeSidebar() {
    if (window.matchMedia("(max-width: 760px)").matches) {
      setMobileSidebarOpen(false);
    } else {
      setSidebarCollapsed(true);
    }
  }

  function handleNewChat() {
    newChat();
    setMobileSidebarOpen(false);
  }

  function handleSelectChat(id: string) {
    selectChat(id);
    setMobileSidebarOpen(false);
  }

  return (
    <div className={`app-shell ${sidebarCollapsed ? "app-shell--collapsed" : ""}`}>
      {mobileSidebarOpen && (
        <button
          type="button"
          className="app-shell__scrim"
          onClick={() => setMobileSidebarOpen(false)}
          aria-label="Close sidebar"
        />
      )}

      <Sidebar
        conversations={conversations}
        activeId={activeId}
        collapsed={sidebarCollapsed}
        mobileOpen={mobileSidebarOpen}
        onSelect={handleSelectChat}
        onNewChat={handleNewChat}
        onClose={closeSidebar}
      />

      <ChatPanel
        conversation={activeConversation}
        assistantState={assistantState}
        isBusy={isBusy}
        error={error}
        onSend={sendMessage}
        onOpenSidebar={openSidebar}
      />
    </div>
  );
}
