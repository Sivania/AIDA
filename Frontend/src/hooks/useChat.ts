import { useEffect, useRef, useState } from 'react'
import { createConversation, getConversations, getMessages, sendToAida } from '../api/aida'
import type { AssistantState, ChatConversation, ChatMessage } from '../types/chat'

// Replies arrive whole. They're revealed over at most this long so the
// "responding" waves have a moment. Remove when the server streams.
const REVEAL_MS = 1200
const REVEAL_TICK_MS = 30

// First line of the first message, shortened, as the conversation title.
function titleFrom(text: string): string {
  const firstLine = text.split('\n')[0].trim()
  return firstLine.length > 60 ? `${firstLine.slice(0, 57)}…` : firstLine
}

type Reveal = { timer: number; finish: () => void }

export function useChat() {
  const [conversations, setConversations] = useState<ChatConversation[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [assistantState, setAssistantState] = useState<AssistantState>('idle')
  const [error, setError] = useState<string | null>(null)
  const [isLoadingMessages, setIsLoadingMessages] = useState(false)

  const abortRef = useRef<AbortController | null>(null)
  const revealRef = useRef<Reveal | null>(null)

  const activeConversation = conversations.find((c) => c.id === activeId) ?? null
  // Sending is blocked while history loads, so a new message can't be overwritten by it.
  const isBusy = assistantState !== 'idle' || isLoadingMessages

  // Load the conversation list once when the page opens.
  useEffect(() => {
    const controller = new AbortController()

    getConversations(controller.signal)
      .then((list) => {
        // StrictMode runs this effect twice in development; only the second run may land.
        if (controller.signal.aborted) return
        // Titles only. A conversation's messages are loaded when you open it.
        const loaded = list.map((c) => ({ id: String(c.id), title: c.title, messages: [] }))
        setConversations((current) => [...current, ...loaded])
      })
      .catch((err) => {
        if (controller.signal.aborted) return
        setError(`Could not load conversations. ${err instanceof Error ? err.message : ''}`)
      })

    return () => controller.abort()
  }, [])

  // Stop any request or reveal if the app unmounts.
  useEffect(
    () => () => {
      abortRef.current?.abort()
      if (revealRef.current) window.clearInterval(revealRef.current.timer)
    },
    [],
  )

  function setMessages(conversationId: string, messages: ChatMessage[]) {
    setConversations((current) =>
      current.map((c) => (c.id === conversationId ? { ...c, messages } : c)),
    )
  }

  // Cancel a running request. A reply that's mid-reveal is shown in full, not cut off.
  function stop() {
    abortRef.current?.abort()
    abortRef.current = null
    revealRef.current?.finish()
    setAssistantState('idle')
    setIsLoadingMessages(false)
  }

  function newChat() {
    stop()
    setActiveId(null)
    setError(null)
  }

  function selectChat(id: string) {
    stop()
    setActiveId(id)
    setError(null)

    // A local- conversation was never created on the server, so there's nothing to load.
    if (id.startsWith('local-')) return

    // Load every time it's opened, so messages sent from another device show up too.
    const controller = new AbortController()
    abortRef.current = controller
    setIsLoadingMessages(true)

    getMessages(id, controller.signal)
      .then((messages) => {
        if (controller.signal.aborted) return
        setMessages(id, messages)
      })
      .catch((err) => {
        if (controller.signal.aborted) return
        setError(`Could not load this conversation. ${err instanceof Error ? err.message : ''}`)
      })
      .finally(() => {
        if (abortRef.current !== controller) return
        abortRef.current = null
        setIsLoadingMessages(false)
      })
  }

  function reveal(conversationId: string, history: ChatMessage[], reply: string) {
    const assistant: ChatMessage = { id: crypto.randomUUID(), role: 'assistant', content: '' }
    const chunk = Math.max(1, Math.ceil(reply.length / (REVEAL_MS / REVEAL_TICK_MS)))
    let shown = 0

    const finish = () => {
      window.clearInterval(timer)
      revealRef.current = null
      setMessages(conversationId, [...history, { ...assistant, content: reply }])
      setAssistantState('idle')
    }

    const timer = window.setInterval(() => {
      shown += chunk
      if (shown >= reply.length) {
        finish()
      } else {
        setMessages(conversationId, [...history, { ...assistant, content: reply.slice(0, shown) }])
      }
    }, REVEAL_TICK_MS)

    revealRef.current = { timer, finish }
    setAssistantState('responding')
    setMessages(conversationId, [...history, assistant])
  }

  async function sendMessage(text: string) {
    const content = text.trim()
    if (!content || isBusy) return

    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: 'user', content }
    let conversationId = activeId
    let history: ChatMessage[]
    let localId: string | null = null

    if (conversationId === null) {
      // Show the new chat right away under a temporary id. It's created on the
      // server below, so empty chats never pile up there.
      localId = `local-${crypto.randomUUID()}`
      conversationId = localId
      history = [userMessage]
      const conversation = { id: localId, title: titleFrom(content), messages: history }
      setConversations((current) => [conversation, ...current])
      setActiveId(localId)
    } else {
      history = [...(activeConversation?.messages ?? []), userMessage]
      setMessages(conversationId, history)
    }

    setError(null)
    setAssistantState('thinking')

    const controller = new AbortController()
    abortRef.current = controller

    try {
      if (localId !== null) {
        const created = await createConversation(titleFrom(content), controller.signal)
        if (controller.signal.aborted) return
        // Swap the temporary id for the server's id.
        const serverId = String(created.id)
        const replacedId = localId
        setConversations((current) =>
          current.map((c) => (c.id === replacedId ? { ...c, id: serverId, title: created.title } : c)),
        )
        setActiveId(serverId)
        conversationId = serverId
      }

      const reply = await sendToAida(conversationId, content, controller.signal)
      if (controller.signal.aborted) return
      if (!reply) throw new Error('AIDA sent an empty reply.')
      abortRef.current = null
      reveal(conversationId, history, reply)
    } catch (err) {
      if (controller.signal.aborted) return
      abortRef.current = null
      setError(err instanceof Error ? err.message : 'Something went wrong.')
      setAssistantState('idle')
    }
  }

  return {
    conversations,
    activeConversation,
    activeId,
    assistantState,
    isBusy,
    error,
    newChat,
    selectChat,
    sendMessage,
  }
}