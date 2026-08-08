import { useRef } from 'react'
import { animate, utils } from 'animejs'

export default function TiltPanel({ children, className = '', intensity = 10 }) {
  const ref = useRef(null)
  const raf = useRef(null)

  const onMove = (e) => {
    const el = ref.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    const px = (e.clientX - rect.left) / rect.width - 0.5
    const py = (e.clientY - rect.top) / rect.height - 0.5

    if (raf.current) cancelAnimationFrame(raf.current)
    raf.current = requestAnimationFrame(() => {
      utils.set(el, {
        rotateY: `${px * intensity}deg`,
        rotateX: `${-py * intensity}deg`,
        translateZ: '0px'
      })
      const glow = el.querySelector('[data-tilt-glow]')
      if (glow) {
        utils.set(glow, {
          background: `radial-gradient(circle at ${50 + px * 60}% ${50 + py * 60}%, rgba(255,180,84,0.16), transparent 55%)`
        })
      }
    })
  }

  const onLeave = () => {
    const el = ref.current
    if (!el) return
    animate(el, { rotateX: 0, rotateY: 0, duration: 600, ease: 'outElastic(1, .6)' })
  }

  return (
    <div className="perspective-panel">
      <div
        ref={ref}
        onMouseMove={onMove}
        onMouseLeave={onLeave}
        className={`relative transform-gpu will-change-transform ${className}`}
        style={{ transformStyle: 'preserve-3d' }}
      >
        <div data-tilt-glow className="pointer-events-none absolute inset-0 rounded-[inherit]" />
        {children}
      </div>
    </div>
  )
}
