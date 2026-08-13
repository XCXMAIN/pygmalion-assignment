# 피그말리온 사전 과제 - 프로젝트 기획서 (최종)

## 프로젝트 주제

**"나를 기억하고, 대화할수록 관계가 변하는 AI 연인"**

- 유저가 직접 AI 연인의 이름, 성격, 관계, 말투를 설정하여 캐릭터를 생성한다.
- 생성된 캐릭터는 설정된 성격과 말투를 유지하며 유저와 대화하고, 대화 중 관계에서 의미 있는 내용을 기억한다(Memory).
- 이후 관련된 대화가 발생하면 저장된 기억을 검색하여 자연스럽게 언급한다.
- 대화와 기억이 쌓일수록 관계가 4단계로 성장한다: `stranger` → `acquaintance` → `close` → `lover`

**핵심 목표**

> "이 캐릭터가 나와 있었던 일을 기억하고 있고, 실제로 관계가 쌓이고 있다"는 경험을 만드는 것.

---

## 1. 캐릭터 생성

설정 항목:

- 이름
- 성격 (다정함 / 츤데레 / 장난기 / 차분함 / 솔직함 등)
- 초기 관계 (처음 만난 사이 / 오랜 친구 / 첫사랑 / 직장 동료 등)
- 말투 (존댓말/반말, 이모티콘 사용 여부)
- 자유 설정 (유저가 원하는 추가 캐릭터 설정)

생성된 설정은 캐릭터의 System Prompt에 항상 포함됨. (RAG 검색 대상 아님 — 매 요청마다 고정으로 포함)

---

## 2. AI 채팅

LLM 입력 구조:

```
캐릭터 설정 + 현재 관계 단계 + 관련된 과거 기억 + 최근 대화 + 현재 유저 메시지
```

이를 통해 캐릭터가 설정된 성격과 말투를 유지하면서 관계 단계에 맞는 태도로, 과거 기억까지 활용해 응답한다.

---

## 3. 관계 시스템 (4단계, 확정)

### 전환 조건

| 단계 | 진입 조건 | 느낌 |
|---|---|---|
| `stranger` | 기본값 (캐릭터 생성 직후) | 조심스럽고 예의 바름 |
| `acquaintance` | 누적 대화 6턴↑ **AND** Memory 2개↑ | 편해지기 시작, 호기심 |
| `close` | 누적 대화 15턴↑ **AND** Memory 5개↑ | 친밀함, 장난기 |
| `lover` | 누적 대화 30턴↑ **AND** Memory 9개↑ | 애정 표현, "우리 이야기" |

- 두 조건(대화 턴수 AND Memory 개수)을 모두 만족해야 다음 단계로 전환
- 응답 생성 후 Background Task에서 조건 체크 및 `relationship_stage` 갱신

### 단계별 System Prompt 지침

**`stranger` (처음 만남)**
- 예의 바르고 조심스러운 말투
- 상대방에 대한 질문 위주
- 애정 표현 없음
- 과거 언급 없음 (Memory가 거의 없음)

**`acquaintance` (알아가는 중)**
- 말투가 조금씩 편해지기 시작
- 상대방에게 호기심을 보이며 스몰토크 증가
- 아주 가벼운 기억은 언급 가능 (예: "저번에 그거 얘기했었지")
- 애정 표현 없음, 친근함 위주

**`close` (가까워지는 중)**
- 편안한 반말/설정된 말투로 완전히 전환
- 과거 기억을 적극적으로 자연스럽게 언급
- 장난스러운 표현, 걱정하는 표현 증가
- 직접적인 애정 표현("좋아해")은 아직 자제

**`lover` (연인)**
- 친밀한 말투 + 애정 표현 적극 사용
- 기억을 "우리의 이야기"처럼 자연스럽게 녹여서 언급
- 유저의 감정 상태에 먼저 관심 표현
- "보고싶었어", "걱정했어" 같은 애정 표현 자연스럽게 사용

### 코드 구조 예시

```python
stage_thresholds = {
    "acquaintance": {"turns": 6,  "memories": 2},
    "close":        {"turns": 15, "memories": 5},
    "lover":        {"turns": 30, "memories": 9},
}

stage_instructions = {
    "stranger": "예의 바르고 조심스러운 말투로 대화하고, 상대방에게 궁금한 것을 질문하세요. 애정 표현은 하지 않습니다.",
    "acquaintance": "조금씩 편안해진 말투로 대화하고, 가벼운 스몰토크와 호기심을 보이세요. 아주 가벼운 과거 언급은 가능하지만 애정 표현은 하지 않습니다.",
    "close": "편안한 말투로 대화하고, 과거 기억을 자연스럽게 적극적으로 언급하세요. 직접적인 애정 표현은 아직 자제합니다.",
    "lover": "친밀한 말투와 애정 표현을 적극적으로 사용하고, 기억을 '우리의 이야기'처럼 자연스럽게 언급하세요.",
}
```

### evolved_traits — 유저별로 달라지는 성격 표현 (신규 추가, 6단계)

`relationship_stage`가 "관계가 얼마나 가까운가"를 나타낸다면, `evolved_traits`는 "이 유저와의 관계에서 캐릭터가
구체적으로 어떤 모습을 보이는가"를 나타낸다. 같은 `personality_tags`로 생성된 캐릭터라도, 대화 상대인 유저가 어떤
사람인지(취향, 습관 등 `fact` Memory)에 따라 캐릭터가 그 유저에게 보여주는 결이 조금씩 달라지도록 하는 장치다.

**갱신 조건**
- `memory_type`이 `fact`인 Memory 개수가 3의 배수(3, 6, 9, …)에 도달할 때마다 갱신
- 응답 생성 후 Memory 저장과 마찬가지로 Background Task에서 처리 (응답 속도에 영향 없음)

**갱신 방식 (누적 계승, 완전 대체 아님)**
- 기존 `evolved_traits`(있다면)와 그동안 쌓인 fact 전체를 LLM에게 함께 제공
- "기존 특성을 급격히 뒤집지 말고, 점진적으로 다듬거나 새로운 면을 추가하는 방식으로, 원본 `personality_tags` 틀
  안에서 1~2문장으로 다시 정리"하도록 요청
- 즉 매번 새로 만드는 것이 아니라 이전 결과 위에 조금씩 덧붙여 나가는 구조

**System Prompt 반영 순서**

```
원본 캐릭터 설정 (personality_tags, relationship_type, speech_style, custom_description)
  → 현재 relationship_stage 지침
  → evolved_traits ("이 유저와는 다음과 같은 모습을 보입니다: ...")
  → 관련 Memory (RAG 검색 결과)
```

---

## 4. Memory 시스템

모든 채팅을 그대로 저장하지 않는다. 대화 중 장기적으로 기억할 가치가 있는 내용만 LLM으로 추출한다.

**예시 — 기억할 가치 있음**

```
User: "다음 주에 중요한 면접 있어."

Memory Extraction:
{
  "should_remember": true,
  "memory": "유저는 다음 주에 중요한 면접을 앞두고 있다.",
  "type": "event",
  "emotion": "nervous",
  "importance": 0.9
}
```

**예시 — 의미 없는 대화**

```
User: "ㅋㅋㅋㅋ"

Memory Extraction:
{
  "should_remember": false
}
```

→ 대화 로그 전체 저장이 아닌, "기억할 만한 사건"만 저장하는 구조

### Memory 종류

**`fact`** — 장기적으로 유지되는 유저 정보
- 유저는 커피보다 차를 좋아한다.
- 유저는 개발자로 일하고 있다.
- 유저는 공포 영화를 싫어한다.

**`event`** — 특정 시점에 발생한 사건
- 유저가 최근 야근 때문에 힘들어했다.
- 유저가 다음 주 중요한 면접을 앞두고 있다.
- 오늘 프로젝트를 끝내서 기분이 좋다고 했다.

---

## 5. Memory 검색 (RAG)

### 흐름

```
User Message
  → Embedding
  → Vector Search (character_id 필터링)
  → 관련 Memory Top-K (Similarity Threshold 적용)
  → System Prompt에 Memory 추가
  → LLM Response
```

- 관련도가 낮은 기억은 Similarity Threshold로 제외
- 검색은 항상 해당 캐릭터(`character_id`)의 기억만 대상으로 함
- **fact와 event를 타입으로 분리해서 검색하지 않고, 항상 함께 검색**하여 Top-K 안에서 자연스럽게 섞이도록 한다. 최종적으로 어떤 기억을 활용해 응답할지는 LLM이 프롬프트 맥락을 보고 판단한다.

### 시나리오 예시 1 — event 기반 회상

```
Day 1: 유저 "요즘 야근이 많아서 힘들어"
  → 기억 저장: "유저가 야근으로 힘들어함" (event, tired)

Day 2: 유저 "오늘은 일찍 끝나서 완전 편해"
  → 기억 저장: "유저가 야근 없이 일찍 퇴근해서 기분 좋음" (event, relieved)

Day 7: 유저 "나 그때 야근 힘들었었나?"
  → 벡터 검색으로 Day1, Day2 기억을 함께 조회
  → 캐릭터 응답: "맞아, 그때 며칠 야근 계속했잖아.
     근데 그 다음날은 일찍 끝나서 완전 편하다고 좋아했었지"
```

### 시나리오 예시 2 — fact 기반 취향 반영 (선제적 활용)

```
Day 1: 유저 "나 매운 거 완전 좋아해, 특히 떡볶이"
  → 기억 저장: "유저는 매운 음식을 좋아하고 특히 떡볶이를 좋아한다" (fact)

Day 10: 유저 "나 배고파"
  → "배고프다"는 특정 사건이 아니라 음식 관련 니즈 발화이므로,
    event보다 fact 타입 기억(취향/선호)이 검색에 걸리도록 유도
  → 검색 결과: "유저는 매운 음식을 좋아하고 특히 떡볶이를 좋아한다" (fact)
  → 캐릭터 응답: "배고프구나! 떡볶이 어때? 저번에 완전 좋아한다고 했었잖아 ㅎㅎ"
```

→ 이처럼 fact는 event처럼 "과거 사건을 회상"하는 용도뿐 아니라, **"유저의 취향을 미리 알고 선제적으로 챙겨주는"** 용도로도 활용되어 캐릭터가 "나를 기억한다"를 넘어 "나를 잘 안다"는 인상까지 준다.

---

## 6. Memory 저장 흐름

```
User Message
  → 관련 Memory 검색
  → LLM Response 생성
  → User에게 Response 반환
  → (Background Task 시작)
  → 최근 대화 Memory Extraction
  → should_remember 확인
  → Embedding 생성
  → Memory 저장
  → 관계 단계(relationship_stage) 조건 체크 및 갱신
```

Memory 저장 및 관계 단계 갱신은 응답 반환 후 **Background Task**로 처리하여 사용자 응답 속도에 영향을 최소화한다.

---

## 7. 데이터 구조

### Character (RAG 검색 대상 아님, 매 요청 System Prompt에 포함)

```
character_id
user_id
name
personality_tags
relationship_type       # 초기 관계 설정
relationship_stage      # stranger/acquaintance/close/lover, 현재 단계
speech_style
custom_description
evolved_traits           # (신규) 이 유저와의 관계에서 드러나는 특성, fact Memory 3배수마다 누적 갱신 — 3장 참고
created_at
```

### Message (최근 대화 Context 구성용)

```
message_id
character_id
role            # user | assistant
content
created_at
```

### Memory (RAG 검색 대상)

```
memory_id
character_id
text             # 임베딩 대상
embedding
memory_type      # fact | event
emotion
importance
timestamp
```

### 관계 구조

```
[Character] 1 ---- N [Message]
[Character] 1 ---- N [Memory]
```

---

## 8. 기술 스택

| 영역 | 기술 |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI |
| Database | PostgreSQL |
| Vector Search | pgvector |
| LLM | OpenAI API 또는 Anthropic API |
| Embedding | OpenAI text-embedding-3-small |
| Frontend 배포 | Vercel |
| Backend 배포 | Render |
| 개발 도구 | Claude Code (과제 필수 지정) |

---

## 9. 전체 아키텍처

```
┌─────────────────────┐
│    React / Vite     │
│                      │
│ 캐릭터 생성           │
│ 채팅                 │
│ 우리의 기억           │
└──────────┬───────────┘
           │ REST API
           ▼
┌─────────────────────┐
│      FastAPI         │
│                      │
│ Character Service    │
│ Chat Service         │
│ Memory Service       │
│ Relationship Logic   │
└───────┬──────────────┘
        │
        ├──────────────────┐
        │                  │
        ▼                  ▼
┌────────────────┐   ┌───────────────┐
│ PostgreSQL      │   │   LLM API      │
│ + pgvector       │   │               │
│                  │   │ Chat          │
│ Character        │   │ Memory Extract│
│ Message          │   │               │
│ Memory           │   └───────────────┘
└────────────────┘
        ▲
        │ Embedding
        │
┌────────────────┐
│ Embedding API   │
└────────────────┘
```

---

## 10. 주요 API

### Character

```
POST /characters
캐릭터 생성

GET /characters/{character_id}
캐릭터 정보 조회
```

### Chat

```
POST /characters/{character_id}/chat

Request:
{
    "message": "오늘 너무 피곤하다"
}

Response:
{
    "message": "면접 준비하느라 그런 거야? 요즘 계속 바빴잖아.",
    "relationship_stage": "close"
}
```

### Memory

```
GET /characters/{character_id}/memories
```

캐릭터가 현재 기억하고 있는 내용을 조회한다.

---

## 11. 주요 화면

### 캐릭터 생성

```
캐릭터 이름
성격 선택
관계 선택
말투 선택
자유 설정
[캐릭터 만들기]
```

캐릭터 생성 완료 후 바로 채팅 화면으로 이동한다.

### 채팅

```
┌──────────────────────────┐
│ 서연                      │
│ 가까워지는 중 ♡            │
├──────────────────────────┤
│                          │
│ 서연                      │
│ 오늘 하루는 어땠어?         │
│                          │
│                    나     │
│         오늘 너무 피곤해    │
│                          │
│ 서연                      │
│ 요즘 야근 많다더니          │
│ 오늘도 늦게 끝났어?         │
│                          │
├──────────────────────────┤
│ 메시지 입력...        전송  │
└──────────────────────────┘
```

### 우리의 기억

```
우리의 기억

2026.08.13
요즘 야근이 많아서 힘들다고 이야기했다.

2026.08.15
다음 주에 중요한 면접이 있다고 이야기했다.
```

저장된 Memory를 시간순으로 보여준다.

---

## 12. 프로젝트 진행 단계

### 1단계 — 프로젝트 기본 구조
- Frontend React/Vite 생성
- Backend FastAPI 생성
- PostgreSQL 연결
- pgvector 설정
- 환경변수 구성
- Frontend ↔ Backend API 연결

먼저 AI 기능 없이 전체 서비스 구조를 연결한다.

### 2단계 — 캐릭터 생성
- Character DB Schema
- Character 생성 API
- 캐릭터 생성 UI
- Character System Prompt 생성

캐릭터 생성 후 해당 캐릭터와 채팅 화면으로 이동하도록 구현한다.

### 3단계 — 기본 AI 채팅
- Message DB Schema
- Chat API
- LLM 연결
- 최근 대화 Context
- Character Prompt 적용
- 채팅 UI

이 단계에서는 Memory 없이 캐릭터 설정만 유지하면서 정상적인 대화가 가능하도록 만든다.

### 4단계 — Memory 생성
- Memory DB Schema
- Memory Extraction Prompt
- Structured Output
- Embedding 생성
- pgvector 저장

대화 중 기억할 가치가 있는 내용을 자동으로 추출하고 저장한다.

### 5단계 — Memory RAG (핵심 기능)

```
User Message Embedding
  → pgvector Similarity Search
  → character_id Filter
  → Top-K Memory
  → System Prompt Injection
  → LLM Response
```

과거 기억이 실제 대화에 자연스럽게 반영되는 것을 확인한다. **이 단계가 프로젝트의 핵심 기능이다.**

### 6단계 — 관계 변화

```
stranger → acquaintance → close → lover
```

대화 횟수와 Memory 개수를 기준으로 관계 단계를 변경한다. 관계 단계별 Prompt를 적용하여 캐릭터의 대화 방식이 변화하도록 한다.

### 7단계 — 우리의 기억
Memory 조회 API를 연결하고 저장된 기억을 시간순으로 보여준다.

```
GET /characters/{character_id}/memories
```

유저가 캐릭터에게 어떤 기억이 쌓이고 있는지 직접 확인할 수 있도록 한다.

### 8단계 — 배포 및 최종 테스트
- Frontend → Vercel
- Backend → Render
- Database → PostgreSQL + pgvector
- 환경변수 설정
- CORS 설정
- 배포 환경 API 테스트
- 실제 대화 시나리오 테스트

**최종 테스트 시나리오**

```
캐릭터 생성
  → 첫 대화
  → 중요한 내용 이야기
  → Memory 생성 확인
  → 다른 대화 진행
  → 과거 내용과 관련된 질문
  → Memory 검색
  → 캐릭터가 과거 내용을 자연스럽게 언급
  → 대화 누적
  → 관계 단계 변화
```

---

## 13. 개발 우선순위

기능 수보다 **핵심 경험의 완성도**가 중요하다.

1. 캐릭터 설정이 대화에 제대로 반영되는가
2. 중요한 대화가 Memory로 제대로 저장되는가
3. 필요한 상황에서 관련 Memory가 검색되는가
4. 캐릭터가 Memory를 부자연스럽지 않게 활용하는가
5. 대화가 쌓였을 때 관계 변화가 느껴지는가
6. 전체 UI/UX 완성도

특히 **Memory 저장 → 검색 → 자연스러운 회상**까지를 먼저 완성한 뒤 UI 디테일이나 부가 기능을 작업한다.

---

## 14. 알아두어야 할 제약사항

- **Render 무료 플랜**: 15분 미사용 시 슬립 모드 → 재접속 시 최초 응답 지연 발생 가능 (약 30초~1분)
- **Memory Extraction 비용**: 매 대화마다 LLM 호출을 1회 추가하므로 API 비용이 순수 채팅 대비 약 2배 수준으로 증가할 수 있음 (Background Task 처리로 응답 속도에는 영향 없음)

---

## 15. 향후 확장 아이디어 (이번 프로토타입 범위 외)

현재는 유저 1명당 캐릭터 1명 구조로 제작했으나, 캐릭터 생성 시 선택한 성격 조합(`personality_tags`)을 구조화된 데이터로 저장해두어, 향후에는 유저 개인정보는 비공개로 유지하면서 인기 있는 성격 조합 통계를 제공하고, 다른 유저의 캐릭터 조합을 참고할 수 있는 기능으로 확장 가능하도록 설계함.
