import { useEffect, useRef } from 'react'
import { animate, stagger } from 'animejs'
import SignalLine from './SignalLine.jsx'

function Section({ title, items, accent, empty }) {
  if (!items || items.length === 0) {
    return (
      <div className="rounded-lg border border-line bg-ink-800/50 p-5">
        <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-haze">{title}</p>
        <p className="mt-2 text-sm text-haze/70">{empty}</p>
      </div>
    )
  }
  return (
    <div className="rounded-lg border border-line bg-ink-800/50 p-5">
      <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-haze">{title}</p>
      <ul className="mt-3 flex flex-col gap-2">
        {items.map((it, i) => (
          <li key={i} className="flex items-start gap-2 text-[14px] leading-relaxed text-paper/90">
            <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${accent}`} />
            <span>{typeof it === 'string' ? it : JSON.stringify(it)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function Results({ candidate, feedback, onRestart }) {
  const rootRef = useRef(null)

  useEffect(() => {
    animate(rootRef.current.querySelectorAll('[data-reveal]'), {
      opacity: [0, 1],
      translateY: [16, 0],
      delay: stagger(90),
      duration: 650,
      ease: 'outQuad'
    })
  }, [])

  const hasFeedback = Boolean(feedback)

  return (
    <div ref={rootRef} className="min-h-screen bg-ink-900 bg-grid text-paper">
      <header className="border-b border-line/70">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-4">
          <span className="font-mono text-xs tracking-[0.3em] text-haze">PROBE // INTERVIEW REPORT</span>
          <span className="font-mono text-[11px] text-haze">{candidate.member.name}</span>
        </div>
      </header>

      <section className="mx-auto max-w-4xl px-6 pb-16 pt-12">
        <p data-reveal className="font-mono text-xs uppercase tracking-[0.35em] text-teal">
          Interview complete
        </p>
        <h1 data-reveal className="mt-3 font-display text-3xl font-semibold md:text-4xl">
          Evidence-backed report for {candidate.member.name}
        </h1>

        <div data-reveal className="mt-6 rounded-lg border border-line bg-ink-800/60 p-4 md:p-6">
          <SignalLine amplitude={0.6} className="h-16" />
        </div>

        {!hasFeedback && (
          <div data-reveal className="mt-8 rounded-lg border border-coral/30 bg-coral-soft p-5 text-sm text-coral">
            The interview ended without a feedback payload from the backend. Check that the final response includes
            a <code className="font-mono">feedback</code> object as defined in the API contract.
          </div>
        )}

        {hasFeedback && (
          <>
            <div data-reveal className="mt-8 rounded-lg border border-amber/30 bg-amber-soft p-5 md:p-6">
              <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-amber">Summary</p>
              <p className="mt-2 text-[15px] leading-relaxed text-paper">{feedback.summary}</p>
            </div>

            <div data-reveal className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
              <Section title="Strengths" items={feedback.strengths} accent="bg-teal" empty="No strengths recorded." />
              <Section title="Gaps" items={feedback.gaps} accent="bg-coral" empty="No gaps recorded." />
              <Section
                title="Suggested next"
                items={feedback.next}
                accent="bg-amber"
                empty="No recommendations recorded."
              />
            </div>
          </>
        )}

        <button
          data-reveal
          onClick={onRestart}
          className="mt-10 inline-flex items-center gap-2 rounded-md border border-line px-5 py-3 font-display text-sm font-medium text-paper transition-colors hover:border-amber/50 hover:text-amber"
        >
          ← Back to console
        </button>
      </section>
    </div>
  )
}
