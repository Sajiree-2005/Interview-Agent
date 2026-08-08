import { useEffect, useRef, useState } from 'react'
import { startInterview, sendAnswer, newSessionId } from '../api.js'
import ChatLog from './ChatLog.jsx'
import SidePanel from './SidePanel.jsx'

export default function Interview({ candidate, onFinish }) {
  const sessionIdRef = useRef(newSessionId())
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [thinking, setThinking] = useState(true)
  const [error, setError] = useState(null)
  const [startedAt] = useState(Date.now())
  const [elapsedLabel, setElapsedLabel] = useState('0:00')
  const startedRef = useRef(false)
  const inputRef = useRef(null)

  const questionCount = messages.filter((m) => m.role === 'candidate').length

  useEffect(() => {
    const t = setInterval(() => {
      const s = Math.floor((Date.now() - startedAt) / 1000)
      setElapsedLabel(`${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`)
    }, 1000)
    return () => clearInterval(t)
  }, [startedAt])

  useEffect(() => {
    if (startedRef.current) return
    startedRef.current = true

    ;(async () => {
      try {
        const res = await startInterview(sessionIdRef.current, candidate)
        setMessages([{ role: 'agent', text: res.reply, ts: Date.now() }])
        if (res.done) {
          setTimeout(() => onFinish(res.feedback ?? null, sessionIdRef.current), 900)
        }
      } catch (err) {
        setError(err.message || 'Could not reach the interview backend.')
      } finally {
        setThinking(false)
      }
    })()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSend = async () => {
    const text = draft.trim()
    if (!text || thinking) return

    setMessages((prev) => [...prev, { role: 'candidate', text, ts: Date.now() }])
    setDraft('')
    setThinking(true)
    setError(null)

    try {
      const res = await sendAnswer(sessionIdRef.current, text)
      setMessages((prev) => [...prev, { role: 'agent', text: res.reply, ts: Date.now() }])
      if (res.done) {
        setTimeout(() => onFinish(res.feedback ?? null, sessionIdRef.current), 900)
      }
    } catch (err) {
      setError(err.message || 'Could not reach the interview backend.')
    } finally {
      setThinking(false)
      inputRef.current?.focus()
    }
  }

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-screen flex-col bg-ink-900 text-paper">
      <header className="flex items-center justify-between border-b border-line px-6 py-3">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-teal animate-pulse" />
          <span className="font-mono text-xs tracking-[0.3em] text-haze">LIVE INTERVIEW</span>
        </div>
        <span className="font-mono text-[11px] text-haze">session {sessionIdRef.current.slice(0, 8)}</span>
      </header>

      <div className="flex min-h-0 flex-1">
        <div className="flex min-h-0 flex-1 flex-col">
          <ChatLog messages={messages} thinking={thinking} />

          {error && (
            <div className="mx-6 mb-3 rounded-md border border-coral/40 bg-coral-soft px-4 py-2 font-mono text-xs text-coral">
              {error} — check that the backend is running and VITE_API_URL is set.
            </div>
          )}

          <div className="border-t border-line bg-ink-800/60 p-4 md:p-5">
            <div className="mx-auto flex max-w-2xl items-end gap-3">
              <textarea
                ref={inputRef}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={onKeyDown}
                rows={1}
                placeholder="Type your answer… (Enter to send, Shift+Enter for a new line)"
                className="max-h-32 min-h-[46px] flex-1 resize-none rounded-md border border-line bg-ink-900 px-4 py-3 text-sm text-paper placeholder:text-haze/60 focus:border-amber/60"
              />
              <button
                onClick={handleSend}
                disabled={thinking || !draft.trim()}
                className="h-[46px] shrink-0 rounded-md bg-amber px-5 font-display text-sm font-semibold text-ink-900 transition-opacity disabled:opacity-40"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        <SidePanel candidate={candidate} questionCount={questionCount} elapsedLabel={elapsedLabel} />
      </div>
    </div>
  )
}
