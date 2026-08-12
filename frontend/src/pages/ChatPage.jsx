import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getCharacter, getMessages, sendMessage } from '../lib/api'

const STAGE_LABELS = {
  stranger: '처음 만난 사이',
  acquaintance: '알아가는 중',
  close: '가까워지는 중',
  lover: '연인',
}

export default function ChatPage() {
  const { characterId } = useParams()
  const [character, setCharacter] = useState(null)
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    Promise.all([getCharacter(characterId), getMessages(characterId)])
      .then(([characterData, messageData]) => {
        setCharacter(characterData)
        setMessages(messageData)
      })
      .catch((err) => setError(err.message))
  }, [characterId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSubmit(e) {
    e.preventDefault()
    const text = draft.trim()
    if (!text || sending) return

    setError(null)
    setDraft('')
    setSending(true)
    setMessages((prev) => [
      ...prev,
      { message_id: `local-${Date.now()}`, role: 'user', content: text },
    ])

    try {
      const res = await sendMessage(characterId, text)
      setMessages((prev) => [
        ...prev,
        { message_id: `local-reply-${Date.now()}`, role: 'assistant', content: res.message },
      ])
      setCharacter((prev) => ({ ...prev, relationship_stage: res.relationship_stage }))
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  if (error && !character) {
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

      <div className="message-list">
        {messages.map((m) => (
          <div key={m.message_id} className={`message-row ${m.role}`}>
            <span className="message-sender">{m.role === 'user' ? '나' : character.name}</span>
            <p className="message-bubble">{m.content}</p>
          </div>
        ))}
        {sending && (
          <div className="message-row assistant">
            <span className="message-sender">{character.name}</span>
            <p className="message-bubble typing">...</p>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <p className="form-error">{error}</p>}

      <form className="message-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="메시지 입력..."
          disabled={sending}
        />
        <button type="submit" disabled={sending || !draft.trim()}>
          전송
        </button>
      </form>
    </section>
  )
}
