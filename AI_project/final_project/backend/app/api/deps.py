from fastapi import Depends, Header, HTTPException
from typing import Optional
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from utils.app_store import get_user_by_token
from utils.roles import can_access_page, get_role_config


def _extract_token(authorization: Optional[str], x_auth_token: Optional[str]) -> Optional[str]:
    if x_auth_token:
        return x_auth_token.strip()
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return None


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    x_auth_token: Optional[str] = Header(default=None, alias="X-Auth-Token"),
):
    token = _extract_token(authorization, x_auth_token)
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_page(page_key: str):
    def _inner(user=Depends(get_current_user)):
        if not can_access_page(user["job_role"], page_key):
            raise HTTPException(status_code=403, detail=f"Role {user['job_role']} cannot access {page_key}")
        return user
    return _inner


def require_flag(flag: str):
    def _inner(user=Depends(get_current_user)):
        if not get_role_config(user["job_role"]).get(flag):
            raise HTTPException(status_code=403, detail="Not authorized")
        return user
    return _inner
