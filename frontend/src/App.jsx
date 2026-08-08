import { useState } from 'react'
import Landing from './components/Landing.jsx'
import Interview from './components/Interview.jsx'
import Results from './components/Results.jsx'

export default function App() {
  const [view, setView] = useState('landing') // 'landing' | 'interview' | 'results'
  const [candidate, setCandidate] = useState(null)
  const [feedback, setFeedback] = useState(null)

  const handleBegin = (selectedCandidate) => {
    setCandidate(selectedCandidate)
    setFeedback(null)
    setView('interview')
  }

  const handleFinish = (finalFeedback) => {
    setFeedback(finalFeedback)
    setView('results')
  }

  const handleRestart = () => {
    setCandidate(null)
    setFeedback(null)
    setView('landing')
  }

  if (view === 'interview' && candidate) {
    return <Interview candidate={candidate} onFinish={handleFinish} />
  }

  if (view === 'results' && candidate) {
    return <Results candidate={candidate} feedback={feedback} onRestart={handleRestart} />
  }

  return <Landing onBegin={handleBegin} />
}
