import { useEffect, useState } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import { listCharacters } from './lib/api'
import { getUserId } from './lib/user'
import CharacterCreatePage from './pages/CharacterCreatePage'
import ChatPage from './pages/ChatPage'

function HomePage() {
  const [existingCharacterId, setExistingCharacterId] = useState(undefined)

  useEffect(() => {
    listCharacters(getUserId())
      .then((characters) => setExistingCharacterId(characters[0]?.character_id ?? null))
      .catch(() => setExistingCharacterId(null))
  }, [])

  if (existingCharacterId === undefined) return null
  if (existingCharacterId) return <Navigate to={`/chat/${existingCharacterId}`} replace />
  return <CharacterCreatePage />
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/chat/:characterId" element={<ChatPage />} />
    </Routes>
  )
}

export default App
