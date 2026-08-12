const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

async function request(path, options) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export function createCharacter(payload) {
  return request('/api/characters', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getCharacter(characterId) {
  return request(`/api/characters/${characterId}`)
}

export function listCharacters(userId) {
  return request(`/api/characters?user_id=${userId}`)
}
