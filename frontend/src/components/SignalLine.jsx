import { useEffect, useRef } from 'react'
import { animate, utils } from 'animejs'

// The signature visual: a two-channel signal trace (amber = candidate signal,
// teal = curriculum baseline). Draws itself in once, then breathes gently.
// Amplitude is derived from real candidate signal data, not decorative.
export default function SignalLine({ amplitude = 0.5, className = '', pulse = false }) {
  const ampRef = useRef(null)
  const baseRef = useRef(null)
  const wrapRef = useRef(null)

  const buildPath = (amp, seed) => {
    const pts = []
    const w = 640
    const h = 120
    const steps = 24
    for (let i = 0; i <= steps; i++) {
      const x = (w / steps) * i
      const t = i / steps
      const wobble = Math.sin(t * Math.PI * 6 + seed) * (h * 0.22 * amp)
      const drift = Math.sin(t * Math.PI * 1.4 + seed * 0.4) * (h * 0.12 * amp)
      const y = h / 2 + wobble + drift
      pts.push(`${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`)
    }
    return pts.join(' ')
  }

  useEffect(() => {
    if (ampRef.current) ampRef.current.setAttribute('d', buildPath(amplitude, 0))
    if (baseRef.current) baseRef.current.setAttribute('d', buildPath(0.22, 2))

    const paths = [ampRef.current, baseRef.current].filter(Boolean)
    paths.forEach((p) => {
      const len = p.getTotalLength()
      utils.set(p, { strokeDasharray: len, strokeDashoffset: len })
    })

    animate(paths, {
      strokeDashoffset: 0,
      duration: 1400,
      delay: (_, i) => i * 220,
      ease: 'outCubic'
    })

    if (pulse && wrapRef.current) {
      animate(wrapRef.current, {
        translateY: [0, -3, 0],
        opacity: [1, 0.86, 1],
        duration: 2600,
        loop: true,
        ease: 'inOutSine'
      })
    }
  }, [amplitude, pulse])

  return (
    <div ref={wrapRef} className={className}>
      <svg viewBox="0 0 640 120" className="w-full h-full" preserveAspectRatio="none">
        <path ref={baseRef} fill="none" stroke="#5FE3C4" strokeOpacity="0.45" strokeWidth="1.5" />
        <path ref={ampRef} fill="none" stroke="#FFB454" strokeWidth="2" strokeLinecap="round" />
      </svg>
    </div>
  )
}
