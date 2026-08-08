// Talks to the single required endpoint: POST /api/interview
// Contract (technical-spec.md is authoritative):
//   Start:    { sessionId, candidate }              -> { reply, done }
//   Continue: { sessionId, message }                 -> { reply, done }
//   Finish:                                           -> { reply, done: true, feedback: { summary, strengths, gaps, next } }

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const ENDPOINT = `${BASE_URL.replace(/\/$/, '')}/api/interview`

async function post(body) {
  const res = await fetch(ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })

  if (!res.ok) {
    let detail = ''
    try {
      const errBody = await res.json()
      detail = errBody?.detail || errBody?.message || ''
    } catch (_) {
      // response wasn't JSON, ignore
    }
    throw new Error(detail || `Interview API responded with ${res.status}`)
  }

  return res.json()
}

export function startInterview(sessionId, candidate) {
  return post({ sessionId, candidate })
}

export function sendAnswer(sessionId, message) {
  return post({ sessionId, message })
}

export function newSessionId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `sess-${Date.now()}-${Math.random().toString(16).slice(2)}`
}
