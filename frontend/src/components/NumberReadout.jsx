import { useEffect, useRef } from 'react'
import { animate } from 'animejs'

export default function NumberReadout({ value, suffix = '', duration = 1100, className = '' }) {
  const ref = useRef(null)

  useEffect(() => {
    const counter = { val: 0 }
    animate(counter, {
      val: value,
      duration,
      ease: 'outExpo',
      onUpdate: () => {
        if (ref.current) ref.current.textContent = `${Math.round(counter.val)}${suffix}`
      }
    })
  }, [value, suffix, duration])

  return (
    <span ref={ref} className={`tick-label ${className}`}>
      0{suffix}
    </span>
  )
}
