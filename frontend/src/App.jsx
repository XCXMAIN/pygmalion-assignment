import { useEffect, useState } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

function App() {
  const [health, setHealth] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/health/db`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(setHealth)
      .catch((err) => setError(err.message))
  }, [])

  return (
    <section id="center">
      <h1>AI 연인 서비스</h1>
      <p>Frontend ↔ Backend 연결 확인</p>
      {error && <p style={{ color: 'crimson' }}>연결 실패: {error}</p>}
      {!error && !health && <p>백엔드 확인 중...</p>}
      {health && (
        <pre>{JSON.stringify(health, null, 2)}</pre>
      )}
    </section>
  )
}

export default App
