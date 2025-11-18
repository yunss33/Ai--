from typing import Any, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.ai_chat_service import generate_reply
from Config.ToolConfig import global_tool_registry, AITool
from Tool.NetTool import register_net_search_tools
from Data.Entity.ChatEntity import ChatEntity
from Data.Entity.ChatRequestDTO import ChatRequestDTO
from Data.Entity.ChatReplyDTO import ChatReplyDTO


class ConversationSummary(BaseModel):
    id: int
    title: str
    course_id: int | None = None


class Message(BaseModel):
    id: int
    sender_type: str
    content: Any


class ToolDescription(BaseModel):
    name: str
    description: str


class ToolInvokeRequest(BaseModel):
    tool_name: str
    params: dict


router = APIRouter()


@router.post("/chat", response_model=ChatReplyDTO)
async def chat(
    data: ChatRequestDTO,
    db: Session = Depends(get_db),
) -> ChatReplyDTO:
    entity = ChatEntity(
        input_text=data.message,
        course_id=data.course_id,
        conversation_id=data.conversation_id or "",
    )
    result = generate_reply(entity)
    return ChatReplyDTO(
        conversation_id=result.conversation_id,
        reply=str(result.data),
        tool_calls=result.tool_calls,
    )


@router.get("/conversations", response_model=List[ConversationSummary])
async def list_conversations(
    db: Session = Depends(get_db),
) -> List[ConversationSummary]:
    return []


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[Message],
)
async def list_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
) -> List[Message]:
    return []


@router.get("/tools/available", response_model=List[ToolDescription])
async def list_available_tools(
    db: Session = Depends(get_db),
) -> List[ToolDescription]:
    if not global_tool_registry.all():
        # 首次访问时，注册内置网络搜索工具
        register_net_search_tools()
    return [
        ToolDescription(name=tool.name, description=tool.description)
        for tool in global_tool_registry.all()
    ]


@router.post("/tools/invoke")
async def invoke_tool(
    data: ToolInvokeRequest,
    db: Session = Depends(get_db),
) -> dict:
    tool = global_tool_registry.get(data.tool_name)
    if tool is None:
        return {"tool_name": data.tool_name, "error": "tool not found"}
    # 调用实际工具处理函数，优先按关键字参数解包
    try:
        if data.params:
            result = tool.handler(**data.params)
        else:
            result = tool.handler()
        return {"tool_name": tool.name, "result": result}
    except TypeError:
        # 兼容少量仅接受单一 dict 参数的工具实现
        try:
            result = tool.handler(data.params)
            return {"tool_name": tool.name, "result": result}
        except Exception as exc:  # pragma: no cover - 运行期错误兜底
            return {"tool_name": tool.name, "error": str(exc)}
    except Exception as exc:  # pragma: no cover - 运行期错误兜底
        return {"tool_name": tool.name, "error": str(exc)}
