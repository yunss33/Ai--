#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatEntity:
    """学生发起到 AI 的对话请求实体

    - input_text: 本次用户输入的内容
    - course_id: 课程 ID，可选，用于课程内对话
    - conversation_id: 会话 ID，字符串；为空表示新会话
    """

    input_text: str
    course_id: Optional[int] = None
    conversation_id: str = ""

