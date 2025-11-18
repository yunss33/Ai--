"""API响应实体模块

定义了一个用于统一API响应格式的R类，支持数据过滤、JSON序列化和FastAPI响应生成。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List


@dataclass(slots=True)
class R:
    """API响应实体类，采用纯数据类风格设计

    用于统一API返回格式，包含成功状态、数据、消息、错误信息等字段。
    支持自动过滤空值，生成标准化的JSON响应。

    Usage example:
      r = R(success=True)
      r.data = {...}
      r.thread_id = "tid"
      r.timings_ms["parse"] = 12
      return r.json_response()
    """

    # 基础响应字段
    success: bool = True  # 操作是否成功
    data: Any = None  # 响应数据，任意类型
    message: str = ""  # 成功消息
    error: Optional[str] = None  # 错误信息，仅在success=False时使用
    code: int = 200  # HTTP状态码

    # 扩展字段
    status: Optional[str] = None  # 业务状态码或描述
    thread_id: Optional[str] = None  # 请求线程ID，用于追踪
    context: Optional[Any] = None  # 上下文信息

    # 高级功能字段
    timings_ms: Dict[str, int] = field(default_factory=dict)  # 性能计时信息
    process_log: List[str] = field(default_factory=list)  # 处理日志
    extras: Dict[str, Any] = field(default_factory=dict)  # 额外自定义字段

    def to_dict(self) -> Dict[str, Any]:
        """将响应对象转换为字典，仅包含非空值

        Returns:
            Dict[str, Any]: 包含非空字段的字典表示
        """
        result: Dict[str, Any] = {"success": self.success}

        if self.data is not None:
            def _drop_keys(obj: Any, drop_keys: set[str]) -> Any:
                """递归删除嵌套数据结构中的指定键

                Args:
                    obj: 要处理的数据对象
                    drop_keys: 要删除的键集合

                Returns:
                    处理后的数据对象
                """
                if isinstance(obj, dict):
                    return {k: _drop_keys(v, drop_keys) for k, v in obj.items() if k not in drop_keys}
                if isinstance(obj, list):
                    return [_drop_keys(v, drop_keys) for v in obj]
                return obj

            # 过滤数据中的不需要的键
            filtered_data = _drop_keys(self.data, {"checkboxes"}) if isinstance(self.data, (dict, list)) else self.data
            
            # 确保类聊天结构包含所有必需字段
            if isinstance(filtered_data, dict):
                chat_like = any(k in filtered_data for k in ("tables", "analysis", "tool_calls", "intention"))
                if chat_like:
                    filtered_data.setdefault("tables", [])
                    if "analysis" not in filtered_data:
                        filtered_data["analysis"] = None
                    filtered_data.setdefault("tool_calls", [])
                    filtered_data.setdefault("intention", "unclear")
            result["data"] = filtered_data
        
        # 仅添加非空字段
        if self.message:
            result["message"] = self.message
        if self.error:
            result["error"] = self.error
        if self.code != 200:
            result["code"] = self.code
        if self.status:
            result["status"] = self.status
        if self.thread_id:
            result["thread_id"] = self.thread_id
        if self.context is not None:
            result["context"] = self.context
        if self.timings_ms:
            result["timings_ms"] = self.timings_ms
        if self.process_log:
            result["process_log"] = self.process_log

        # 添加额外自定义字段，避免覆盖现有字段
        for k, v in (self.extras or {}).items():
            if k not in result:
                result[k] = v
        
        return result

    def json(self, ensure_ascii: bool = False, indent: Optional[int] = None) -> str:
        """将响应对象转换为JSON字符串
        
        Args:
            ensure_ascii: 是否转义非ASCII字符，默认False
            indent: 缩进空格数，默认None（紧凑格式）
            
        Returns:
            str: JSON字符串表示
        """
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

    def json_response(self, status_code: Optional[int] = None):  # type: ignore[override]
        """创建FastAPI JSONResponse对象（如果可用），否则返回字典
        
        Args:
            status_code: HTTP状态码，覆盖self.code
            
        Returns:
            FastAPI JSONResponse或字典：FastAPI环境下返回JSONResponse，否则返回字典
        """
        try:
            from fastapi.responses import JSONResponse  # 延迟导入，避免硬依赖
            return JSONResponse(
                content=self.to_dict(),
                status_code=(status_code if status_code is not None else (self.code or 200)),
            )
        except Exception:
            # 当FastAPI不可用时，返回字典
            return self.to_dict()


__all__ = ["R"]  # 导出R类
