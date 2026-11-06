import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'

type Role = 'user' | 'assistant'

type Message = {
  id: string
  role: Role
  content: string
}

// Set VITE_AIDA_MOCK=true in .env.local to try the UI without the backend.
const USE_MOCK = import.meta.env.VITE_AIDA_MOCK === 'true'

const SUGGESTIONS = [
  'What should I focus on today?',
  'Show my Now tasks',
  'What is due this week?',
]

// Contract with the backend:
//   POST /chat  { messages: [{ role, content }] }  ->  { reply: string }
async function sendToAida(messages: Message[], signal: AbortSignal): Promise<string> {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 700))
    return 'Mock reply. Set `VITE_AIDA_MOCK=false` and start the FastAPI server to talk to the real AIDA.'
  }

  const response = await fetch('/chat', {
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

function Logo({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 100 90" aria-hidden="true">
      <path d="M50 6 L94 84 L6 84 Z" fill="none" stroke="currentColor" strokeWidth="7" strokeLinejoin="miter" />
    </svg>
  )
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const abortRef = useRef<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement | null>(null)
  const inputRef = useRef<HTMLTextAreaElement | null>(null)

  // Keep the newest message in view.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  // Let the input grow with its text, up to the max height in CSS.
  useEffect(() => {
    const el = inputRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight}px`
  }, [input])

  // Cancel a running request if the component unmounts.
  useEffect(() => () => abortRef.current?.abort(), [])

  async function send(text: string) {
    const content = text.trim()
    if (!content || isLoading) return

    const userMessage: Message = { id: crypto.randomUUID(), role: 'user', content }
    const history = [...messages, userMessage]

    setMessages(history)
    setInput('')
    setError(null)
    setIsLoading(true)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const reply = await sendToAida(history, controller.signal)
      setMessages((current) => [
        ...current,
        { id: crypto.randomUUID(), role: 'assistant', content: reply },
      ])
    } catch (err) {
      if (controller.signal.aborted) return
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      if (abortRef.current === controller) {
        abortRef.current = null
        setIsLoading(false)
      }
    }
  }

  function newChat() {
    abortRef.current?.abort()
    abortRef.current = null
    setMessages([])
    setInput('')
    setError(null)
    setIsLoading(false)
    inputRef.current?.focus()
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    void send(input)
  }

  // Enter sends, Shift+Enter makes a new line.
  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault()
      void send(input)
    }
  }

  const isEmpty = messages.length === 0

  return (
    <div className="app">
      <header className="topbar">
        <span className="wordmark">AIDA</span>
        <button type="button" className="icon-button" onClick={newChat} aria-label="New chat">
          +
        </button>
      </header>

      <main className="chat">
        {isEmpty ? (
          <div className="empty">
            <Logo className={`logo ${isLoading ? 'thinking' : ''}`} />
            <div className="suggestions">
              {SUGGESTIONS.map((suggestion) => (
                <button key={suggestion} type="button" onClick={() => void send(suggestion)}>
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.role}`}>
                {message.role === 'assistant' ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                ) : (
                  message.content
                )}
              </div>
            ))}

            {isLoading && (
              <div className="message assistant">
                <Logo className="logo small thinking" />
              </div>
            )}

            {error && <div className="error">{error}</div>}
            <div ref={bottomRef} />
          </div>
        )}
      </main>

      <form className="composer" onSubmit={handleSubmit}>
        <textarea
          ref={inputRef}
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message AIDA"
          rows={1}
          autoFocus
        />
        <button type="submit" className="send" disabled={!input.trim() || isLoading} aria-label="Send">
          ↑
        </button>
      </form>

      <footer className="status">{USE_MOCK ? 'Mock replies' : 'Connected to AIDA backend'}</footer>
    </div>
  )
}

export default App