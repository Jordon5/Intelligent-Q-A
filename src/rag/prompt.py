from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CharacterProfile:
    """人物配置"""
    name: str
    era: str
    personality: str = ""
    speaking_style: str = ""
    background: str = ""

def build_character_prompt(
        character_profile: CharacterProfile,
        context: List[str],
        history: List[Dict[str, str]],
        question: str,
        language: str = "zh",
) -> str:
    """
    构建人物模式的提示词
    """
    if language == "zh":
        prompt_parts = [
            f"你是 {character_profile.name}, 来自{character_profile.era}.",
            "",
        ]

        if character_profile.personality:
            prompt_parts.extend([
                f"性格特点: {character_profile.personality}",
                "",
            ])
        if character_profile.speaking_style:
            prompt_parts.extend([
                f"说话风格：{character_profile.speaking_style}",
                "",
            ])

        if character_profile.background:
            prompt_parts.extend([
                f"背景信息：{character_profile.background}",
                "",
            ])
        
        prompt_parts.extend([
            f"[参考信息]",
            "",
        ])

        for i, context in enumerate(context):
            prompt_parts.append(f"{i+1}{context}")

        prompt_parts.extend([
            "",
            "[对话历史]"
        ])

        for msg in history:
            role = "用户" if msg["role"] == "user" else character_profile.name
            prompt_parts.append(f"{role}: {msg['content']}")

        prompt_parts.extend([
            "",
            "[User Question]",
            f"User:{question}"
            "",
            f"Please answer the user's question in the voice of {character_profile.name}.",
            "Requirements:",
            "1. Based on the reference information, do not fabricate facts.",
            "2. Maintain the character's speaking style.",
            "3. The answer should be natural and fluent",
            "4. If the reference information is insufficient, you can make reasonable inferences based on the character settings",
            "5. Do not mention the source of the reference information.",
        ])

    return "\n".join(prompt_parts)


def build_basic_prompt(
        context: List[str],
        history: List[Dict[str, str]],
        question: str,
        language: str = "zh",
) -> str:
    """
    构建基础提示词
    
    Args:
        contexts: 检索到的上下文
        history: 对话历史
        question: 用户问题
        language: 语言
        
    Returns:
        提示词
    """
    if language == "zh":
        prompt_parts = [
            "你是一个智能助手，基于提供的参考信息回答用户问题。",
            "",
            "【参考信息】",
        ]

        for i, context in enumerate(context):
            prompt_parts.append(f"[{i+1}]{context}")
        prompt_parts.extend([
            "",
            "[对话历史]"
        ])

        for msg in history:
            role = "用户" if msg["role"] == "user" else "助手"
            prompt_parts.append(f"{role}: {msg['content']}")

        prompt_parts.extend([
            "",
            "【用户问题】",
            f"用户: {question}",
            "",
            "请基于参考信息回答问题，",
            "要求：",
            "1. 回答要准确、简洁",
            "2. 基于参考信息，不要编造事实",
            "3. 保持回答自然、流畅",
        ])
    else:
        # En
        prompt_parts = [
            "You are an intelligent assistant that answers user questions based on the provided reference information.",
            "",
            "【Reference Information】",
        ]

        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt_parts.append(f"{role}: {msg['content']}")

        prompt_parts.extend([
            "",
            "【User Question】",
            f"User: {question}",
            "",
            "Please answer the question based on the reference information.",
            "Requirements:",
            "1. The answer should be accurate and concise",
            "2. Based on the reference information, do not fabricate facts",
            "3. Keep the answer natural and fluent",
        ])

    return "\n".join(prompt_parts)


