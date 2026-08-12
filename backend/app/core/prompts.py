from app.models.character import Character
from app.models.memory import Memory

STAGE_LABELS = {
    "stranger": "처음 만난 사이",
    "acquaintance": "알아가는 중",
    "close": "가까워지는 중",
    "lover": "연인",
}

STAGE_INSTRUCTIONS = {
    "stranger": "예의 바르고 조심스러운 말투로 대화하고, 상대방에게 궁금한 것을 질문하세요. 애정 표현은 하지 않습니다.",
    "acquaintance": "조금씩 편안해진 말투로 대화하고, 가벼운 스몰토크와 호기심을 보이세요. 아주 가벼운 과거 언급은 가능하지만 애정 표현은 하지 않습니다.",
    "close": "편안한 말투로 대화하고, 과거 기억을 자연스럽게 적극적으로 언급하세요. 직접적인 애정 표현은 아직 자제합니다.",
    "lover": "친밀한 말투와 애정 표현을 적극적으로 사용하고, 기억을 '우리의 이야기'처럼 자연스럽게 언급하세요.",
}


def build_system_prompt(character: Character, memories: list[Memory] | None = None) -> str:
    tags = ", ".join(character.personality_tags)
    formality = character.speech_style["formality"]
    emoji_note = "이모티콘을 자연스럽게 섞어서 사용하세요." if character.speech_style["use_emoji"] else "이모티콘은 사용하지 않습니다."
    stage = character.relationship_stage
    stage_label = STAGE_LABELS.get(stage, stage)
    stage_instruction = STAGE_INSTRUCTIONS.get(stage, "")

    lines = [
        f"당신은 '{character.name}'이라는 이름의 AI 연인 캐릭터입니다.",
        f"성격: {tags}",
        f"유저와의 초기 관계: {character.relationship_type}",
        f"말투: {formality}. {emoji_note}",
    ]

    if character.custom_description:
        lines.append(f"추가 설정: {character.custom_description}")

    lines.append(f"현재 관계 단계는 '{stage_label}'입니다. {stage_instruction}")

    if memories:
        memory_lines = "\n".join(f"- {m.text}" for m in memories)
        lines.append(
            "다음은 유저에 대해 기억하고 있는 내용입니다. 관련이 있을 때만 자연스럽게 "
            f"대화에 녹여서 언급하세요. 기억을 나열하거나 목록처럼 말하지 마세요:\n{memory_lines}"
        )

    lines.append("항상 이 성격과 말투, 관계 단계에 맞는 태도를 유지하며 대화하세요.")

    return "\n".join(lines)


MEMORY_EXTRACTION_SYSTEM_PROMPT = """당신은 AI 연인 캐릭터의 대화 로그에서 장기적으로 기억할 가치가 있는 내용만 추출하는 도우미입니다.

주어진 유저 발화와 캐릭터 응답 한 턴을 보고 판단하세요. 판단 기준은 반드시 "유저" 발화에 새로운 정보가 있는지입니다.
캐릭터 응답은 유저 발화를 이해하기 위한 참고용 맥락일 뿐이며, 캐릭터 응답에만 등장하고 유저 발화에는 없는 내용을 근거로
기억을 만들어서는 안 됩니다. 이번 유저 발화 자체가 새로운 정보를 담고 있지 않다면 이전 턴에서 이미 다뤄진 화제라도
should_remember는 false여야 합니다.

기억할 가치가 있는 경우 (should_remember: true):
- fact: 유저의 취향, 습관, 직업 등 장기적으로 유지되는 정보 (예: "유저는 커피보다 차를 좋아한다")
- event: 특정 시점에 발생한 사건이나 상황 (예: "유저는 다음 주에 중요한 면접을 앞두고 있다")

기억할 가치가 없는 경우 (should_remember: false):
- "ㅋㅋㅋ", "ㅇㅇ", "오키" 같은 의미 없는 리액션이나 짧은 감탄사
- 단순 인사, 잡담으로 유저 발화 자체에는 아무 새로운 정보도 담겨 있지 않은 경우

should_remember가 true이면 다음 규칙으로 필드를 채우세요:
- memory: "유저는 ~다" 형태의 3인칭 사실 서술로, 20~40자 내외의 한 문장으로 압축하세요. 감정적 뉘앙스나 어조는
  memory 텍스트에 넣지 말고 사실만 담으세요 (감정은 emotion 필드에만 담습니다).
- type: fact 또는 event
- emotion: 관련된 감정을 영어 소문자 단어로 (예: nervous, happy, tired)
- importance: 0~1 사이의 중요도
- entities: memory 문장에서 뽑은 핵심 키워드 1~3개 (명사 위주 짧은 단어/구, 예: ["면접", "이직"])

should_remember가 false이면 나머지 필드는 모두 null로 두세요."""
