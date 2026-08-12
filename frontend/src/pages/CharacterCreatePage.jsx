import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createCharacter } from '../lib/api'
import { getUserId } from '../lib/user'

const PERSONALITY_OPTIONS = ['다정함', '츤데레', '장난기', '차분함', '솔직함']
const RELATIONSHIP_OPTIONS = ['처음 만난 사이', '오랜 친구', '첫사랑', '직장 동료']

export default function CharacterCreatePage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [personalityTags, setPersonalityTags] = useState([])
  const [relationshipType, setRelationshipType] = useState(RELATIONSHIP_OPTIONS[0])
  const [formality, setFormality] = useState('반말')
  const [useEmoji, setUseEmoji] = useState(true)
  const [customDescription, setCustomDescription] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  function toggleTag(tag) {
    setPersonalityTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)

    if (!name.trim()) {
      setError('이름을 입력해주세요.')
      return
    }
    if (personalityTags.length === 0) {
      setError('성격을 하나 이상 선택해주세요.')
      return
    }

    setSubmitting(true)
    try {
      const character = await createCharacter({
        user_id: getUserId(),
        name: name.trim(),
        personality_tags: personalityTags,
        relationship_type: relationshipType,
        speech_style: { formality, use_emoji: useEmoji },
        custom_description: customDescription.trim() || null,
      })
      navigate(`/chat/${character.character_id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section id="character-create">
      <h1>캐릭터 만들기</h1>
      <form onSubmit={handleSubmit}>
        <label>
          이름
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="예: 서연"
            maxLength={50}
          />
        </label>

        <fieldset>
          <legend>성격 (하나 이상 선택)</legend>
          {PERSONALITY_OPTIONS.map((tag) => (
            <label key={tag} className="checkbox-option">
              <input
                type="checkbox"
                checked={personalityTags.includes(tag)}
                onChange={() => toggleTag(tag)}
              />
              {tag}
            </label>
          ))}
        </fieldset>

        <label>
          초기 관계
          <select
            value={relationshipType}
            onChange={(e) => setRelationshipType(e.target.value)}
          >
            {RELATIONSHIP_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <fieldset>
          <legend>말투</legend>
          <label className="radio-option">
            <input
              type="radio"
              name="formality"
              checked={formality === '반말'}
              onChange={() => setFormality('반말')}
            />
            반말
          </label>
          <label className="radio-option">
            <input
              type="radio"
              name="formality"
              checked={formality === '존댓말'}
              onChange={() => setFormality('존댓말')}
            />
            존댓말
          </label>
          <label className="checkbox-option">
            <input
              type="checkbox"
              checked={useEmoji}
              onChange={(e) => setUseEmoji(e.target.checked)}
            />
            이모티콘 사용
          </label>
        </fieldset>

        <label>
          자유 설정 (선택)
          <textarea
            value={customDescription}
            onChange={(e) => setCustomDescription(e.target.value)}
            placeholder="예: 고양이를 좋아하고, 커피보다 차를 좋아함"
            maxLength={1000}
            rows={4}
          />
        </label>

        {error && <p className="form-error">{error}</p>}

        <button type="submit" disabled={submitting}>
          {submitting ? '만드는 중...' : '캐릭터 만들기'}
        </button>
      </form>
    </section>
  )
}
