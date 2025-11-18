from __future__ import annotations

from Data.Entity.ChatEntity import ChatEntity
from Data.Entity.ChatResponse import ChatResponse
from Config.LLMConfig import get_llm_config


def generate_reply(entity: ChatEntity) -> ChatResponse:
    """
    生成 AI 回复（当前为占位实现，仅做 echo）。

    后续可以在这里：
    - 调用真实的大语言模型（使用 get_llm_config 提供的配置）
    - 结合 ToolRegistry 执行工具调用
    - 访问数据库查询课程/作业信息等
    """
    cfg = get_llm_config()
    text = f"[model={cfg.model}] {entity.input_text}"
    return ChatResponse(
        success=True,
        data=text,
        conversation_id=entity.conversation_id or "demo-conversation",
        tool_calls=[],
    )
