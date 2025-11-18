#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络搜索工具包

在本包中实现若干可被 AI 智能体 / ToolRegistry 调用的网络搜索工具，
例如 DuckDuckGo 搜索、SearchApi 搜索等。
"""
from __future__ import annotations

from .net_search import (
    SearchResult,
    DuckDuckGoSearchClient,
    SearchApiClient,
    DuckDuckGoLibSearchClient,
    SerpApiSearchClient,
    duckduckgo_search,
    searchapi_search,
    duckduckgo_lib_search,
    serpapi_search,
    register_net_search_tools,
)

__all__ = [
    "SearchResult",
    "DuckDuckGoSearchClient",
    "SearchApiClient",
    "DuckDuckGoLibSearchClient",
    "SerpApiSearchClient",
    "duckduckgo_search",
    "searchapi_search",
    "duckduckgo_lib_search",
    "serpapi_search",
    "register_net_search_tools",
]
