export type Role = 'user' | 'assistant'

export type ChatMessage = {
  id: string
  role: Role
  content: string
}

export type ChatConversation = {
  id: string
  title: string
  messages: ChatMessage[]
}

// Drives the triangle: idle = breathing, thinking = spin, responding = speaking waves.
export type AssistantState = 'idle' | 'thinking' | 'responding'
