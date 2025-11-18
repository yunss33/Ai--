#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ChatResponse:
    """AI 对话统一响应结构（面向内部服务调用）"""

    success: bool
    data: Any
    conversation_id: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)

