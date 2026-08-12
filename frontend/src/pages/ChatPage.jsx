import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getCharacter } from '../lib/api'

const STAGE_LABELS = {
  stranger: '처음 만난 사이',
  acquaintance: '알아가는 중',
  close: '가까워지는 중',
  lover: '연인',
}

export default function ChatPage() {
  const { characterId } = useParams()
  const [character, setCharacter] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getCharacter(characterId)
      .then(setCharacter)
      .catch((err) => setError(err.message))
  }, [characterId])

  if (error) {
    return (
      <section id="chat">
        <p className="form-error">캐릭터를 불러오지 못했습니다: {error}</p>
      </section>
    )
  }

  if (!character) {
    return (
      <section id="chat">
        <p>불러오는 중...</p>
      </section>
    )
  }

  return (
    <section id="chat">
      <header>
        <h1>{character.name}</h1>
        <p>{STAGE_LABELS[character.relationship_stage] ?? character.relationship_stage} ♡</p>
      </header>
      <p className="chat-placeholder">채팅 기능은 다음 단계에서 연결됩니다.</p>
    </section>
  )
}
