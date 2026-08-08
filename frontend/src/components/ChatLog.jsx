import { useEffect, useRef } from 'react'
import { animate } from 'animejs'

function formatTime(ts) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

export default function ChatLog({ messages, thinking }) {
  const logRef = useRef(null)
  const lastCount = useRef(0)

  useEffect(() => {
    const nodes = logRef.current?.querySelectorAll('[data-msg]')
    if (nodes && nodes.length > lastCount.current) {
      const fresh = Array.from(nodes).slice(lastCount.current)
      animate(fresh, {
        opacity: [0, 1],
        translateY: [10, 0],
        duration: 420,
        ease: 'outQuad'
      })
      lastCount.current = nodes.length
    }
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, thinking])

  return (
    <div ref={logRef} className="flex-1 overflow-y-auto px-5 py-6 md:px-8">
      <div className="mx-auto flex max-w-2xl flex-col gap-4">
        {messages.map((m, i) => (
          <div key={i} data-msg className={`flex ${m.role === 'candidate' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] ${m.role === 'candidate' ? 'text-right' : 'text-left'}`}>
              <div className="mb-1 flex items-center gap-2 font-mono text-[10px] text-haze">
                {m.role === 'candidate' ? (
                  <>
                    <span>{formatTime(m.ts)}</span>
                    <span>YOU</span>
                  </>
                ) : (
                  <>
                    <span className="text-amber">PROBE</span>
                    <span>{formatTime(m.ts)}</span>
                  </>
                )}
              </div>
              <div
                className={`rounded-lg px-4 py-3 text-[14px] leading-relaxed ${
                  m.role === 'candidate'
                    ? 'border border-teal/30 bg-teal-soft text-paper'
                    : 'border border-line bg-ink-800 text-paper'
                }`}
              >
                {m.text}
              </div>
            </div>
          </div>
        ))}

        {thinking && (
          <div data-msg className="flex justify-start">
            <div className="max-w-[85%]">
              <div className="mb-1 font-mono text-[10px] text-amber">PROBE</div>
              <div className="flex items-center gap-1 rounded-lg border border-line bg-ink-800 px-4 py-3">
                {[0, 1, 2].map((i) => (
                  <span
                    key={i}
                    className="h-1.5 w-1.5 animate-bounce rounded-full bg-haze"
                    style={{ animationDelay: `${i * 0.12}s` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
