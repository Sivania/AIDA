import type { ChatMessage } from '../types/chat'

// Set VITE_AIDA_MOCK=true in .env.local to try the UI without the backend.
export const USE_MOCK = import.meta.env.VITE_AIDA_MOCK === 'true'

// Contract with the backend:
//   GET  /api/conversations  ->  ConversationSummary[]
//   POST /api/chat  { messages: [{ role, content }] }  ->  { reply: string }   (not built yet)
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

export async function sendToAida(messages: ChatMessage[], signal: AbortSignal): Promise<string> {
  if (USE_MOCK) {
    await wait(1800)
    return 'Mock reply. Set `VITE_AIDA_MOCK=false` and start the FastAPI server to talk to the real AIDA.'
  }

  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages: messages.map(({ role, content }) => ({ role, content })),
    }),
    signal,
  })

  if (!response.ok) {
    throw new Error(`AIDA answered with status ${response.status}.`)
  }

  const data: { reply: string } = await response.json()
  return data.reply
}
