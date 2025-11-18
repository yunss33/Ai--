#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class ChatReplyDTO:
  """HTTP /api/ai/chat 返回实体（用于 FastAPI 路由）"""

  conversation_id: str
  reply: str
  tool_calls: Optional[List[Dict[str, Any]]] = None

