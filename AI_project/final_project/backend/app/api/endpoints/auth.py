from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from utils.app_store import authenticate, create_user, get_user_by_token, init_db, revoke_token
from utils.roles import JOB_ROLES
from app.api.deps import get_current_user
from fastapi import Depends

router = APIRouter()
init_db()


class RegisterRequest(BaseModel):
    username: str
    password: str
    job_role: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.get("/roles")
def list_roles():
    return {"roles": JOB_ROLES}


@router.post("/register")
def register(req: RegisterRequest):
    try:
        user = create_user(req.username, req.password, req.job_role)
        return {"ok": True, "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(req: LoginRequest):
    user = authenticate(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user


@router.post("/logout")
def logout(authorization: Optional[str] = None):
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    revoke_token(token)
    return {"ok": True}
