#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络搜索工具实现

参考 Agent 项目中工具模块的设计思路，这里实现可被 ToolRegistry 使用的网络搜索工具：
- DuckDuckGoSearchClient：使用 DuckDuckGo 的公开搜索 API
- SearchApiClient：使用 SearchApi.io（需要配置 API Key）

并提供 duckduckgo_search / searchapi_search 这两个函数型工具，
以及 register_net_search_tools 便捷函数，用于一次性注册到全局 ToolRegistry。
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

import os

import requests

from Config.ToolConfig import AITool, global_tool_registry
from Config.logger_config import get_logger

# 可选的第三方搜索库（如未安装，对应客户端在运行时会给出友好错误提示）
try:  # duckduckgo_search 库
    from duckduckgo_search import DDGS  # type: ignore
except Exception:  # pragma: no cover - 环境未安装时的兜底
    DDGS = None  # type: ignore

try:  # SerpAPI 官方 Python 客户端
    from serpapi import GoogleSearch  # type: ignore
except Exception:  # pragma: no cover - 环境未安装时的兜底
    GoogleSearch = None  # type: ignore


logger = get_logger(__name__)


@dataclass
class SearchResult:
    """单条搜索结果视图"""

    title: str
    url: str
    snippet: str | None = None
    source: str | None = None


class BaseSearchClient:
    """搜索客户端基类，定义统一接口"""

    def search(self, query: str, *, max_results: int = 5) -> List[SearchResult]:  # pragma: no cover - 接口定义
        raise NotImplementedError


class DuckDuckGoSearchClient(BaseSearchClient):
    """
    使用 DuckDuckGo 公开 API 进行搜索的客户端

    文档示例：https://api.duckduckgo.com/?q=python&format=json
    """

    API_URL = "https://api.duckduckgo.com/"

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def search(self, query: str, *, max_results: int = 5) -> List[SearchResult]:
        if not query:
            raise ValueError("query 不能为空")

        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1,
        }
        logger.info("DuckDuckGo 搜索请求: %s", query)
        resp = requests.get(self.API_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()

        results: List[SearchResult] = []

        # DuckDuckGo 的 RelatedTopics 结果结构较为特殊，这里做一个简化的展平处理
        related_topics = data.get("RelatedTopics") or []
        for item in related_topics:
            # item 可能是分组，或直接是结果
            if "Text" in item and "FirstURL" in item:
                results.append(
                    SearchResult(
                        title=str(item.get("Text") or ""),
                        url=str(item.get("FirstURL") or ""),
                        snippet=str(item.get("Text") or ""),
                        source="duckduckgo",
                    ),
                )
            elif isinstance(item, dict) and "Topics" in item:
                for sub in item.get("Topics") or []:
                    if "Text" in sub and "FirstURL" in sub:
                        results.append(
                            SearchResult(
                                title=str(sub.get("Text") or ""),
                                url=str(sub.get("FirstURL") or ""),
                                snippet=str(sub.get("Text") or ""),
                                source="duckduckgo",
                            ),
                        )
            if len(results) >= max_results:
                break

        return results


class SearchApiClient(BaseSearchClient):
    """
    基于 SearchApi.io 的搜索客户端

    需要配置环境变量 SEARCH_API_KEY，或在初始化时传入 api_key。
    参考文档：https://www.searchapi.io/
    """

    API_URL = "https://www.searchapi.io/api/v1/search"

    def __init__(
        self,
        api_key: Optional[str] = None,
        engine: str = "google",
        timeout: int = 15,
    ) -> None:
        self.api_key = api_key or os.getenv("SEARCH_API_KEY") or ""
        self.engine = engine
        self.timeout = timeout

    def search(self, query: str, *, max_results: int = 5) -> List[SearchResult]:
        if not query:
            raise ValueError("query 不能为空")
        if not self.api_key:
            raise RuntimeError("SEARCH_API_KEY 未配置，无法调用 SearchApi.io")

        params = {
            "engine": self.engine,
            "q": query,
            "api_key": self.api_key,
            "num": max_results,
        }
        logger.info("SearchApi 搜索请求: %s", query)
        resp = requests.get(self.API_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()

        results: List[SearchResult] = []

        for item in data.get("organic_results") or []:
            title = str(item.get("title") or "")
            url = str(item.get("link") or "")
            snippet = item.get("snippet") or ""
            if not snippet and item.get("snippet_highlighted_words"):
                snippet = " ".join(item.get("snippet_highlighted_words") or [])
            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=str(snippet),
                    source=self.engine,
                ),
            )
            if len(results) >= max_results:
                break

        return results


class DuckDuckGoLibSearchClient(BaseSearchClient):
    """
    基于第三方库 duckduckgo_search 的搜索客户端

    优点：对 DuckDuckGo 的接口封装更完善，支持更多参数。
    需要安装依赖：pip install duckduckgo_search
    """

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout
        if DDGS is None:
            raise RuntimeError(
                "duckduckgo_search 库未安装，请先执行 `pip install duckduckgo_search`",
            )

    def search(self, query: str, *, max_results: int = 5) -> List[SearchResult]:
        if not query:
            raise ValueError("query 不能为空")

        # duckduckgo_search 内部已处理网络调用，这里的 timeout 主要用于未来扩展
        results: List[SearchResult] = []
        with DDGS() as ddgs:  # type: ignore[operator]
            for item in ddgs.text(query, max_results=max_results):
                results.append(
                    SearchResult(
                        title=str(item.get("title") or ""),
                        url=str(item.get("href") or ""),
                        snippet=str(item.get("body") or ""),
                        source="duckduckgo_search_lib",
                    ),
                )
        return results


class SerpApiSearchClient(BaseSearchClient):
    """
    基于 SerpAPI (google-search-results) 的搜索客户端

    需要：
    - pip install google-search-results
    - 配置环境变量 SERPAPI_API_KEY
    文档：https://serpapi.com/
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        engine: str = "google",
        timeout: int = 15,
    ) -> None:
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY") or ""
        self.engine = engine
        self.timeout = timeout
        if GoogleSearch is None:
            raise RuntimeError(
                "serpapi 库未安装，请先执行 `pip install google-search-results`",
            )

    def search(self, query: str, *, max_results: int = 5) -> List[SearchResult]:
        if not query:
            raise ValueError("query 不能为空")
        if not self.api_key:
            raise RuntimeError("SERPAPI_API_KEY 未配置，无法调用 SerpAPI")

        params: Dict[str, Any] = {
            "engine": self.engine,
            "q": query,
            "api_key": self.api_key,
            "num": max_results,
        }
        logger.info("SerpAPI 搜索请求: %s", query)
        search = GoogleSearch(params)  # type: ignore[call-arg]
        data: Dict[str, Any] = search.get_dict()

        results: List[SearchResult] = []
        for item in data.get("organic_results") or []:
            results.append(
                SearchResult(
                    title=str(item.get("title") or ""),
                    url=str(item.get("link") or ""),
                    snippet=str(item.get("snippet") or ""),
                    source=self.engine,
                ),
            )
            if len(results) >= max_results:
                break

        return results


def _results_to_dict_list(results: List[SearchResult]) -> List[Dict[str, Any]]:
    """将 SearchResult 列表转换为可 JSON 序列化的 dict 列表"""
    return [asdict(r) for r in results]


def duckduckgo_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    使用 DuckDuckGo 进行网页搜索

    参数:
        query: 搜索关键字
        max_results: 返回结果条数（默认 5）

    返回:
        一个由字典组成的列表，每个字典包含 title、url、snippet、source 等字段。
    """
    client = DuckDuckGoSearchClient()
    results = client.search(query=query, max_results=max_results)
    return _results_to_dict_list(results)


def searchapi_search(
    query: str,
    max_results: int = 5,
    engine: str = "google",
) -> List[Dict[str, Any]]:
    """
    使用 SearchApi.io 进行网页搜索

    参数:
        query: 搜索关键字
        max_results: 返回结果条数（默认 5）
        engine: 搜索引擎（默认 google）

    返回:
        一个由字典组成的列表，每个字典包含 title、url、snippet、source 等字段。
    """
    client = SearchApiClient(engine=engine)
    results = client.search(query=query, max_results=max_results)
    return _results_to_dict_list(results)


def duckduckgo_lib_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    使用 duckduckgo_search 库进行网页搜索

    参数:
        query: 搜索关键字
        max_results: 返回结果条数（默认 5）

    返回:
        一个由字典组成的列表，每个字典包含 title、url、snippet、source 等字段。
    """
    client = DuckDuckGoLibSearchClient()
    results = client.search(query=query, max_results=max_results)
    return _results_to_dict_list(results)


def serpapi_search(
    query: str,
    max_results: int = 5,
    engine: str = "google",
) -> List[Dict[str, Any]]:
    """
    使用 SerpAPI 进行网页搜索

    需要提前安装 google-search-results 库并配置 SERPAPI_API_KEY。

    参数:
        query: 搜索关键字
        max_results: 返回结果条数（默认 5）
        engine: 搜索引擎（默认 google）

    返回:
        一个由字典组成的列表，每个字典包含 title、url、snippet、source 等字段。
    """
    client = SerpApiSearchClient(engine=engine)
    results = client.search(query=query, max_results=max_results)
    return _results_to_dict_list(results)


def register_net_search_tools() -> None:
    """
    将网络搜索工具注册到全局 ToolRegistry 中

    注册的工具包括：
    - duckduckgo_search
    - searchapi_search
    - duckduckgo_lib_search
    - serpapi_search
    """
    # 避免重复注册
    existing = {tool.name for tool in global_tool_registry.all()}

    if "duckduckgo_search" not in existing:
        global_tool_registry.register(
            AITool(
                name="duckduckgo_search",
                description=(
                    "使用 DuckDuckGo 进行网页搜索，返回若干条结果。"
                    "参数：query(str, 必填, 搜索关键字)，max_results(int, 可选)。"
                ),
                handler=duckduckgo_search,
            ),
        )

    if "searchapi_search" not in existing:
        global_tool_registry.register(
            AITool(
                name="searchapi_search",
                description=(
                    "使用 SearchApi.io 进行网页搜索（需要配置 SEARCH_API_KEY）。"
                    "参数：query(str, 必填)，max_results(int, 可选)，engine(str, 可选，默认 google)。"
                ),
                handler=searchapi_search,
            ),
        )

    if "duckduckgo_lib_search" not in existing:
        global_tool_registry.register(
            AITool(
                name="duckduckgo_lib_search",
                description=(
                    "使用 duckduckgo_search 第三方库进行网页搜索。"
                    "参数：query(str, 必填)，max_results(int, 可选，默认 5)。"
                ),
                handler=duckduckgo_lib_search,
            ),
        )

    if "serpapi_search" not in existing:
        global_tool_registry.register(
            AITool(
                name="serpapi_search",
                description=(
                    "使用 SerpAPI 进行网页搜索（需要配置 SERPAPI_API_KEY，且安装 google-search-results 库）。"
                    "参数：query(str, 必填)，max_results(int, 可选)，engine(str, 可选，默认 google)。"
                ),
                handler=serpapi_search,
            ),
        )
