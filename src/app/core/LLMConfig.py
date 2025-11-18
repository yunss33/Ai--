#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM 配置模块

注意：所有实际配置均来自 app.core.config.Settings，
本模块只是一个方便 AI 服务层使用的小封装，避免在业务代码中到处访问环境变量。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.core.config import get_settings


@dataclass(slots=True)
class LLMConfig:
    """大模型配置视图，源自全局 Settings"""

    model: str
    temperature: float
    api_base: Optional[str]
    api_key: Optional[str]

    def as_kwargs(self) -> dict:
        """返回用于创建 LLM 客户端的关键配置"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "api_base": self.api_base,
            "api_key": self.api_key,
        }


def get_llm_config() -> LLMConfig:
    """从全局 Settings 构造 LLMConfig，供 AI 服务使用"""
    settings = get_settings()
    return LLMConfig(
        model=settings.ai_model,
        temperature=settings.ai_temperature,
        api_base=settings.ai_api_base,
        api_key=settings.ai_api_key,
    )

