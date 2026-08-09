import { useEffect, useRef } from 'react'
import { animate, stagger } from 'animejs'

const LABELS = {
  conceptual_knowledge: 'Conceptual knowledge',
  practical_application: 'Practical application',
  engineering_reasoning: 'Engineering reasoning',
  system_design: 'System design',
  communication: 'Communication',
  overall_readiness: 'Overall readiness'
}

// Renders the backend's competency fingerprint (0-100 per dimension) as
// oscilloscope-style bar readouts — the single richest piece of evidence
// the interview produces, so it gets the most visual weight on the report.
export default function ScoreCards({ fingerprint }) {
  const rootRef = useRef(null)

  const entries = Object.entries(fingerprint).filter(([key]) => LABELS[key])

  useEffect(() => {
    const bars = rootRef.current?.querySelectorAll('[data-bar]')
    const nums = rootRef.current?.querySelectorAll('[data-num]')
    if (!bars?.length) return

    animate(bars, {
      width: (el) => el.dataset.target + '%',
      duration: 1200,
      delay: stagger(90),
      ease: 'outExpo'
    })

    nums.forEach((el, i) => {
      const target = Number(el.dataset.target)
      const counter = { val: 0 }
      animate(counter, {
        val: target,
        duration: 1200,
        delay: i * 90,
        ease: 'outExpo',
        onUpdate: () => {
          el.textContent = `${Math.round(counter.val)}%`
        }
      })
    })
  }, [fingerprint])

  return (
    <div ref={rootRef} className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {entries.map(([key, value]) => {
        const isOverall = key === 'overall_readiness'
        return (
          <div
            key={key}
            className={`rounded-lg border p-4 ${
              isOverall ? 'border-amber/40 bg-amber-soft sm:col-span-2' : 'border-line bg-ink-800/50'
            }`}
          >
            <div className="flex items-center justify-between">
              <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-haze">{LABELS[key]}</p>
              <span data-num data-target={value} className={`font-mono text-sm ${isOverall ? 'text-amber' : 'text-paper'}`}>
                0%
              </span>
            </div>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-ink-600">
              <div
                data-bar
                data-target={value}
                className={`h-full rounded-full ${isOverall ? 'bg-amber' : 'bg-teal'}`}
                style={{ width: '0%' }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
