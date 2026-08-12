from app.models.character import Character

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


def build_system_prompt(character: Character) -> str:
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
    lines.append("항상 이 성격과 말투, 관계 단계에 맞는 태도를 유지하며 대화하세요.")

    return "\n".join(lines)
