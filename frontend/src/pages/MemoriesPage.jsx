import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getCharacter, getMemories } from '../lib/api'

function formatDate(isoString) {
  const d = new Date(isoString)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}.${m}.${day}`
}

function groupByDate(memories) {
  const groups = []
  for (const memory of memories) {
    const date = formatDate(memory.timestamp)
    const last = groups[groups.length - 1]
    if (last && last.date === date) {
      last.items.push(memory)
    } else {
      groups.push({ date, items: [memory] })
    }
  }
  return groups
}

export default function MemoriesPage() {
  const { characterId } = useParams()
  const [character, setCharacter] = useState(null)
  const [memories, setMemories] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getCharacter(characterId), getMemories(characterId)])
      .then(([characterData, memoryData]) => {
        setCharacter(characterData)
        setMemories(memoryData)
      })
      .catch((err) => setError(err.message))
  }, [characterId])

  if (error) {
    return (
      <section id="memories">
        <p className="form-error">불러오지 못했습니다: {error}</p>
      </section>
    )
  }

  if (!memories) {
    return (
      <section id="memories">
        <p>불러오는 중...</p>
      </section>
    )
  }

  const groups = groupByDate(memories)

  return (
    <section id="memories">
      <header>
        <Link to={`/chat/${characterId}`} className="back-link">
          ← 채팅으로
        </Link>
        <h1>우리의 기억</h1>
        {character && <p>{character.name}와(과) 쌓아온 기억들</p>}
      </header>

      {groups.length === 0 && <p className="memories-empty">아직 쌓인 기억이 없어요.</p>}

      {groups.map((group) => (
        <div key={group.date} className="memory-date-group">
          <h2 className="memory-date">{group.date}</h2>
          {group.items.map((memory) => (
            <div key={memory.memory_id} className="memory-item">
              <p className="memory-text">{memory.text}</p>
              {memory.entities && memory.entities.length > 0 && (
                <div className="memory-tags">
                  {memory.entities.map((tag) => (
                    <span key={tag} className="memory-tag">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      ))}
    </section>
  )
}
