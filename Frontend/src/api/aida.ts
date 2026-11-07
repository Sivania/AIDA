import type { ChatMessage, Role } from '../types/chat'

// Set VITE_AIDA_MOCK=true in .env.local to try the UI without the backend.
export const USE_MOCK = import.meta.env.VITE_AIDA_MOCK === 'true'

// Contract with the backend:
//   GET  /api/conversations                      ->  ConversationSummary[]
//   POST /api/conversations  { title }           ->  ConversationSummary
//   POST /api/chat  { conversation_id, message } ->  { reply: string }
// The server keeps the history. Only the new message is sent.
export type ConversationSummary = {
  id: number
  title: string
  created_at: string
  updated_at: string
}

const MOCK_CONVERSATIONS: ConversationSummary[] = [
  { id: 2, title: 'Planning next week', created_at: '2026-11-07 14:02:11', updated_at: '2026-11-07 15:40:03' },
  { id: 1, title: 'New conversation', created_at: '2026-11-06 09:15:40', updated_at: '2026-11-06 09:20:12' },
]

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export async function getConversations(signal: AbortSignal): Promise<ConversationSummary[]> {
  if (USE_MOCK) {
    await wait(300)
    return MOCK_CONVERSATIONS
  }

  const response = await fetch('/api/conversations', { signal })

  if (!response.ok) {
    throw new Error(`AIDA answered with status ${response.status}.`)
  }

  return response.json()
}

export async function createConversation(title: string, signal: AbortSignal): Promise<ConversationSummary> {
  if (USE_MOCK) {
    await wait(200)
    const now = new Date().toISOString()
    return { id: MOCK_CONVERSATIONS.length + Date.now(), title, created_at: now, updated_at: now }
  }

  const response = await fetch('/api/conversations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
    signal,
  })

  if (!response.ok) {
    throw new Error(`AIDA answered with status ${response.status}.`)
  }

  return response.json()
}

export async function getMessages(conversationId: string, signal: AbortSignal): Promise<ChatMessage[]> {
  if (USE_MOCK) {
    await wait(300)
    return []
  }

  const response = await fetch(`/api/conversations/${conversationId}/messages`, { signal })

  if (!response.ok) {
    throw new Error(`AIDA answered with status ${response.status}.`)
  }

  const rows: { id: number; role: Role; content: string }[] = await response.json()
  return rows.map(({ id, role, content }) => ({ id: String(id), role, content }))
}

export async function sendToAida(conversationId: string, message: string, signal: AbortSignal): Promise<string> {
  if (USE_MOCK) {
    await wait(1800)
    return 'Mock reply. Set `VITE_AIDA_MOCK=false` and start the FastAPI server to talk to the real AIDA.'
  }

  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: Number(conversationId), message }),
    signal,
  })

  if (!response.ok) {
    throw new Error(`AIDA answered with status ${response.status}.`)
  }

  const data: { reply: string } = await response.json()
  return data.reply
}