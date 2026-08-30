from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, List, Optional
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.api.deps import get_current_user
from utils.app_store import (
    add_message,
    create_conversation,
    delete_conversation,
    get_conversation,
    list_conversations,
    list_messages,
)
from utils.roles import get_role_config

router = APIRouter()


class NewChatRequest(BaseModel):
    title: Optional[str] = "New chat"


class MessageRequest(BaseModel):
    role: str
    content: str
    sources: Optional[List[Any]] = None


@router.get("")
def my_chats(user=Depends(get_current_user)):
    return {"conversations": list_conversations(user["id"])}


@router.post("")
def new_chat(req: NewChatRequest, user=Depends(get_current_user)):
    return create_conversation(user["id"], req.title or "New chat")


@router.get("/{conversation_id}")
def get_chat(conversation_id: str, user=Depends(get_current_user)):
    conv = get_conversation(user["id"], conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation": conv, "messages": list_messages(user["id"], conversation_id)}


@router.post("/{conversation_id}/messages")
def post_message(conversation_id: str, req: MessageRequest, user=Depends(get_current_user)):
    try:
        return add_message(user["id"], conversation_id, req.role, req.content, req.sources)
    except PermissionError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.delete("/{conversation_id}")
def remove_chat(conversation_id: str, user=Depends(get_current_user)):
    if not get_role_config(user["job_role"]).get("can_delete_chats"):
        raise HTTPException(status_code=403, detail="Your role cannot delete chats")
    if not delete_conversation(user["id"], conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True}
