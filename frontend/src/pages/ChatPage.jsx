import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getCharacter, getMessages, sendMessage } from '../lib/api'

const STAGE_LABELS = {
  stranger: '처음 만난 사이',
  acquaintance: '알아가는 중',
  close: '가까워지는 중',
  lover: '연인',
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function randomDelay(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

// 응답이 너무 빨리 와도 타이핑 표시가 스쳐 지나가지 않도록 두는 최소 노출 시간
const TYPING_MIN_MS = 600
const SEGMENT_GAP_MIN_MS = 500
const SEGMENT_GAP_MAX_MS = 1500

export default function ChatPage() {
  const { characterId } = useParams()
  const [character, setCharacter] = useState(null)
  const [messages, setMessages] = useState([])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [typing, setTyping] = useState(false)
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
    setTyping(true)
    setMessages((prev) => [
      ...prev,
      { message_id: `local-${Date.now()}`, role: 'user', content: text },
    ])

    try {
      const requestStartedAt = Date.now()
      const res = await sendMessage(characterId, text)

      const elapsed = Date.now() - requestStartedAt
      if (elapsed < TYPING_MIN_MS) await sleep(TYPING_MIN_MS - elapsed)

      for (let i = 0; i < res.messages.length; i++) {
        if (i > 0) {
          setTyping(true)
          await sleep(randomDelay(SEGMENT_GAP_MIN_MS, SEGMENT_GAP_MAX_MS))
        }
        setTyping(false)
        setMessages((prev) => [
          ...prev,
          { message_id: `local-reply-${Date.now()}-${i}`, role: 'assistant', content: res.messages[i] },
        ])
        // 메시지가 막 도착한 뒤 실제로 잠깐 멈춰야, 다음 반복의 setTyping(true)가 방금 호출한
        // setTyping(false)와 같은 렌더에 배칭되어 "꺼짐"이 화면에 반영되지 않는 문제를 막을 수 있다.
        if (i < res.messages.length - 1) await sleep(150)
      }
      setCharacter((prev) => ({ ...prev, relationship_stage: res.relationship_stage }))
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
      setTyping(false)
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
        <Link to={`/chat/${characterId}/memories`} className="memories-link">
          우리의 기억 보기
        </Link>
      </header>

      <div className="message-list">
        {messages.map((m) => (
          <div key={m.message_id} className={`message-row ${m.role}`}>
            <span className="message-sender">{m.role === 'user' ? '나' : character.name}</span>
            <p className="message-bubble">{m.content}</p>
          </div>
        ))}
        {typing && (
          <div className="message-row assistant">
            <span className="message-sender">{character.name}</span>
            <p className="message-bubble typing-bubble">
              <span className="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </span>
            </p>
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
