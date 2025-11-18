#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
课程助手对话 Graph（基于 LangGraph）

本模块负责：
- 定义一个最小可用的 LangGraph，用于调用大模型生成课程助手回复；
- 将「设定提示词」和「信息提示词」组合到一次调用中；
- 暂不做多步 Tool 调用，只是包装一次 LLM 调用，后续可在此基础上扩展。

注意：
- 依赖外部库：`langgraph` 和 `openai`（新版官方 SDK）。
- 依赖本项目中的：
  - `app.core.LLMConfig.get_llm_config`：提供模型名称、base_url、api_key 等；
  - `app.AI.Promt.SetPromts`：提供课程助手提示词模板。
"""

from __future__ import annotations

from typing import TypedDict

from app.AI.Promt.SetPromts import (
    CoursePromptParams,
    build_setting_prompt,
    build_info_prompt,
)
from app.core.LLMConfig import get_llm_config


class CourseChatState(TypedDict):
    """LangGraph 状态：简单起见，只包含用户输入和回复文本。"""

    user_query: str
    reply: str


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    使用 OpenAI 官方 SDK 调用 chat.completions。

    如需适配其他网关，只要保持 messages 语义一致即可。
    """
    # 延迟导入，避免在未安装 openai 时导致整个应用无法启动
    try:
        from openai import OpenAI  # type: ignore
    except Exception as exc:  # pragma: no cover - 运行环境相关
        # 在未安装 openai 时退回一个明确错误提示
        return f"[LLM 调用失败：缺少 openai 依赖：{exc}]"

    cfg = get_llm_config()
    client = OpenAI(
        api_key=cfg.api_key,
        base_url=cfg.api_base or None,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        completion = client.chat.completions.create(
            model=cfg.model,
            messages=messages,
            temperature=cfg.temperature,
        )
        content = completion.choices[0].message.content or ""
    except Exception as exc:  # pragma: no cover - 运行期错误兜底
        content = f"[LLM 调用异常：{exc}]"

    return content


def _assistant_node(state: CourseChatState, params: CoursePromptParams) -> dict:
    """
    LangGraph 中的单一节点：
    - 读取当前 user_query；
    - 使用课程参数构造设定提示词和信息提示词；
    - 调用 LLM 得到 reply。
    """
    setting_prompt = build_setting_prompt()
    info_prompt = build_info_prompt(params, user_query=state["user_query"])

    reply_text = _call_llm(setting_prompt, info_prompt)
    return {"reply": reply_text}


def build_course_chat_graph(params: CoursePromptParams):
    """
    构造课程助手的最小 LangGraph。

    使用方式（示例）：
        from langgraph.graph import START
        from app.AI.Promt.SetPromts import CoursePromptParams
        from app.AI.Graph.course_assistant_graph import build_course_chat_graph

        params = CoursePromptParams(course_name="高等数学")
        graph = build_course_chat_graph(params)
        result = graph.invoke({"user_query": "极限怎么学？", "reply": ""})
        print(result["reply"])
    """
    # 延迟导入，避免在未安装 langgraph 时应用无法启动
    from langgraph.graph import StateGraph, END  # type: ignore

    workflow = StateGraph(CourseChatState)
    workflow.add_node("assistant", lambda s: _assistant_node(s, params))
    workflow.set_entry_point("assistant")
    workflow.add_edge("assistant", END)

    return workflow.compile()


__all__ = [
    "CourseChatState",
    "build_course_chat_graph",
]

