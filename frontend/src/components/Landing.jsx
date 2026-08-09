import { useEffect, useMemo, useRef, useState } from 'react'
import { animate, stagger } from 'animejs'
import candidateData from '../data/candidates.json'
import curriculum from '../data/curriculum.json'
import SignalLine from './SignalLine.jsx'
import TiltPanel from './TiltPanel.jsx'
import ModuleStack from './ModuleStack.jsx'
import NumberReadout from './NumberReadout.jsx'

const TOTAL_DAYS = curriculum.days.length

function computeProgress(candidate) {
  const completedDays = candidate.missions.filter((m) => m.passed).map((m) => m.day)
  const skipped = candidate.missions.filter((m) => m.skipped)
  const pct = Math.round((candidate.signals.missionsCompleted / TOTAL_DAYS) * 100)
  return { completedDays, skipped, pct: Math.min(pct, 100) }
}

export default function Landing({ onBegin }) {
  const [activeId, setActiveId] = useState(candidateData.candidates[0]?.member.id ?? null)
  const heroRef = useRef(null)
  const rosterRef = useRef(null)

  const active = useMemo(
    () => candidateData.candidates.find((c) => c.member.id === activeId) ?? candidateData.candidates[0],
    [activeId]
  )
  const progress = useMemo(() => computeProgress(active), [active])

  useEffect(() => {
    animate(heroRef.current.querySelectorAll('[data-fade]'), {
      opacity: [0, 1],
      translateY: [16, 0],
      delay: stagger(90),
      duration: 700,
      ease: 'outQuad'
    })
    animate(rosterRef.current.querySelectorAll('[data-card]'), {
      opacity: [0, 1],
      translateX: [-14, 0],
      delay: stagger(70, { start: 400 }),
      duration: 600,
      ease: 'outQuad'
    })
  }, [])

  return (
    <div className="min-h-screen bg-ink-900 bg-grid bg-grid text-paper">
      {/* Top strip */}
      <header className="border-b border-line/70">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-amber animate-pulse" />
            <span className="font-mono text-xs tracking-[0.3em] text-haze">PROBE // INTERVIEW CONSOLE</span>
          </div>
          <span className="font-mono text-[11px] text-haze">{curriculum.cohort}</span>
        </div>
      </header>

      {/* Hero */}
      <section ref={heroRef} className="mx-auto max-w-6xl px-6 pb-6 pt-14 md:pt-20">
        <p data-fade className="font-mono text-xs uppercase tracking-[0.35em] text-amber">
          Evidence-driven technical interview
        </p>
        <h1 data-fade className="mt-4 max-w-3xl font-display text-4xl font-semibold leading-[1.08] text-paper md:text-6xl">
          It reads the candidate's <span className="text-amber">signal</span>, not a script.
        </h1>
        <p data-fade className="mt-5 max-w-xl text-[15px] leading-relaxed text-haze">
          PROBE builds a fresh interview blueprint from each candidate's actual learning journey, then adapts every
          question in real time — going deeper where they're strong, simplifying where they're not.
        </p>

        <div data-fade className="mt-10 rounded-lg border border-line bg-ink-800/60 p-4 md:p-6">
          <div className="flex items-center justify-between font-mono text-[11px] text-haze">
            <span>CANDIDATE SIGNAL — {active.member.name.toUpperCase()}</span>
            <span>AMPLITUDE {(progress.pct / 100).toFixed(2)}</span>
          </div>
          <SignalLine amplitude={Math.max(progress.pct / 100, 0.15)} pulse className="mt-3 h-24 md:h-28" />
        </div>
      </section>

      {/* Candidate roster + profile */}
      <section className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-6 pb-10 md:grid-cols-[320px_1fr]">
        <div ref={rosterRef}>
          <p className="mb-3 font-mono text-[11px] uppercase tracking-[0.25em] text-haze">Select candidate</p>
          <div className="flex flex-col gap-2">
            {candidateData.candidates.map((c) => {
              const p = computeProgress(c)
              const isActive = c.member.id === active.member.id
              return (
                <button
                  data-card
                  key={c.member.id}
                  onClick={() => setActiveId(c.member.id)}
                  className={`group flex items-center justify-between rounded-md border px-4 py-3 text-left transition-colors ${
                    isActive ? 'border-amber/60 bg-amber-soft' : 'border-line bg-ink-800/40 hover:border-line/90 hover:bg-ink-800'
                  }`}
                >
                  <div>
                    <p className="font-display text-sm font-medium text-paper">{c.member.name}</p>
                    <p className="font-mono text-[11px] text-haze">{c.member.jobRole}</p>
                  </div>
                  <span className={`font-mono text-xs ${isActive ? 'text-amber' : 'text-haze'}`}>{p.pct}%</span>
                </button>
              )
            })}
          </div>
        </div>

        <TiltPanel intensity={4} className="rounded-lg border border-line bg-ink-800/60 p-6 md:p-8">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-haze">Candidate profile</p>
              <h2 className="mt-2 font-display text-2xl font-semibold text-paper">{active.member.name}</h2>
              <p className="mt-1 text-sm text-haze">
                {active.member.jobRole} · {active.member.yearsExperience} yrs · {active.member.education}
              </p>
              <span className="mt-3 inline-block rounded border border-teal/40 bg-teal-soft px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-teal">
                {active.member.status}
              </span>
            </div>

            <div className="flex gap-6">
              <div>
                <NumberReadout value={active.signals.missionsCompleted} className="block font-mono text-2xl text-paper" />
                <p className="font-mono text-[10px] uppercase tracking-wider text-haze">missions done</p>
              </div>
              <div>
                <NumberReadout value={active.signals.commitDays} className="block font-mono text-2xl text-paper" />
                <p className="font-mono text-[10px] uppercase tracking-wider text-haze">commit days</p>
              </div>
              <div>
                <NumberReadout value={active.signals.missionsFirstTry} className="block font-mono text-2xl text-paper" />
                <p className="font-mono text-[10px] uppercase tracking-wider text-haze">first-try passes</p>
              </div>
            </div>
          </div>

          {progress.skipped.length > 0 && (
            <div className="mt-6 rounded border border-coral/30 bg-coral-soft px-4 py-3">
              <p className="font-mono text-[11px] uppercase tracking-wider text-coral">Skipped topics — tested differently</p>
              <p className="mt-1 text-sm text-paper/90">{progress.skipped.map((s) => s.title).join(', ')}</p>
            </div>
          )}

          <div className="mt-8">
            <p className="mb-2 font-mono text-[11px] uppercase tracking-[0.25em] text-haze">31-day curriculum map</p>
            <ModuleStack highlightDays={progress.completedDays} accent="amber" />
          </div>

          <button
            onClick={() => onBegin(active)}
            className="mt-4 inline-flex items-center gap-3 rounded-md bg-amber px-6 py-3 font-display text-sm font-semibold text-ink-900 transition-transform hover:-translate-y-0.5 active:translate-y-0"
          >
            Start interview
            <span aria-hidden className="font-mono text-xs">→</span>
          </button>
        </TiltPanel>
      </section>

      <footer className="mx-auto max-w-6xl px-6 pb-10">
        <p className="font-mono text-[10px] text-haze/70">
          Built for the ABTalks Vibe Code Hackathon · Problem Statement 2 — The Interview Agent
        </p>
      </footer>
    </div>
  )
}
