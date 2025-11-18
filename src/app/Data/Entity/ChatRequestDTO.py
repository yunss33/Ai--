#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatRequestDTO:
    """HTTP /api/ai/chat 请求实体（用于 FastAPI 路由）"""

    conversation_id: Optional[str] = None
    course_id: Optional[int] = None
    message: str = ""

