import { useEffect, useRef } from 'react'
import { animate, stagger, onScroll } from 'animejs'
import curriculum from '../data/curriculum.json'

// A literal isometric rack of the 8 real curriculum modules — not decoration,
// it's the actual shape of the candidate's 31-day learning journey.
export default function ModuleStack({ completedDays = [] }) {
  const rackRef = useRef(null)

  useEffect(() => {
    const blocks = rackRef.current?.querySelectorAll('[data-block]')
    if (!blocks?.length) return
    animate(blocks, {
      translateY: [40, 0],
      rotateX: [18, 0],
      opacity: [0, 1],
      duration: 900,
      delay: stagger(90),
      ease: 'outExpo',
      autoplay: onScroll({
        target: rackRef.current,
        enter: 'bottom-20%',
        leave: 'top top',
        sync: false
      })
    })
  }, [])

  const isDayCovered = (range) => {
    const [start, end] = range
    for (let d = start; d <= end; d++) {
      if (completedDays.includes(d)) return true
    }
    return false
  }

  return (
    <div className="perspective-panel py-6">
      <div
        ref={rackRef}
        className="flex flex-wrap gap-3 md:gap-4"
        style={{ transformStyle: 'preserve-3d', transform: 'rotateX(8deg)' }}
      >
        {curriculum.modules.map((mod, i) => {
          const covered = isDayCovered(mod.days)
          return (
            <div
              key={mod.n}
              data-block
              className="group relative w-[104px] md:w-[122px] h-[132px] md:h-[150px] rounded-md border border-line bg-ink-700/80 opacity-0"
              style={{
                transformStyle: 'preserve-3d',
                boxShadow: covered
                  ? '0 18px 30px -14px rgba(255,180,84,0.35), inset 0 0 0 1px rgba(255,180,84,0.25)'
                  : '0 14px 24px -16px rgba(0,0,0,0.6)'
              }}
            >
              <div
                className="absolute inset-x-0 top-0 h-1 rounded-t-md"
                style={{ background: covered ? '#FFB454' : '#28313F' }}
              />
              <div className="flex h-full flex-col justify-between p-3">
                <span className="font-mono text-[10px] text-haze">MOD {String(mod.n).padStart(2, '0')}</span>
                <div>
                  <p className="font-display text-[13px] leading-tight text-paper line-clamp-3">{mod.title}</p>
                  <p className="mt-2 font-mono text-[10px] text-haze">
                    D{mod.days[0]}–D{mod.days[1]}
                  </p>
                </div>
              </div>
              <div
                className={`absolute right-2 top-2 h-1.5 w-1.5 rounded-full ${
                  covered ? 'bg-amber' : 'bg-line'
                }`}
              />
            </div>
          )
        })}
      </div>
    </div>
  )
}
