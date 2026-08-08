import SignalLine from './SignalLine.jsx'

const MIN_QUESTIONS = 8
const MAX_QUESTIONS = 10

export default function SidePanel({ candidate, questionCount, elapsedLabel }) {
  const pct = Math.min((questionCount / MIN_QUESTIONS) * 100, 100)

  return (
    <aside className="hidden w-[300px] shrink-0 flex-col gap-6 border-l border-line bg-ink-800/60 p-6 md:flex">
      <div>
        <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-haze">Candidate</p>
        <p className="mt-1 font-display text-lg font-semibold text-paper">{candidate.member.name}</p>
        <p className="font-mono text-[11px] text-haze">
          {candidate.member.jobRole} · {candidate.member.yearsExperience} yrs
        </p>
      </div>

      <div>
        <p className="font-mono text-[10px] uppercase tracking-[0.25em] text-haze">Live signal</p>
        <SignalLine amplitude={0.55} pulse className="mt-2 h-16" />
      </div>

      <div>
        <div className="flex items-center justify-between font-mono text-[10px] uppercase tracking-[0.25em] text-haze">
          <span>Question</span>
          <span className="text-paper">
            {questionCount}/{MIN_QUESTIONS}
            <span className="text-haze"> (max {MAX_QUESTIONS})</span>
          </span>
        </div>
        <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-ink-600">
          <div
            className="h-full rounded-full bg-amber transition-[width] duration-500 ease-out"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Stat label="Curriculum days min" value="4" />
        <Stat label="Session time" value={elapsedLabel} />
      </div>

      <div className="mt-auto rounded-md border border-line bg-ink-700/60 p-3">
        <p className="font-mono text-[10px] uppercase tracking-wider text-haze">Interviewer approach</p>
        <p className="mt-1 text-xs leading-relaxed text-paper/80">
          Depth over definition — probing understanding, application, trade-offs, and system design based on what
          you actually completed.
        </p>
      </div>
    </aside>
  )
}

function Stat({ label, value }) {
  return (
    <div className="rounded-md border border-line bg-ink-700/50 p-3">
      <p className="font-mono text-base text-paper">{value}</p>
      <p className="mt-0.5 font-mono text-[10px] uppercase tracking-wider text-haze">{label}</p>
    </div>
  )
}
