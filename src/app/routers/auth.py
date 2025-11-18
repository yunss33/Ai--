from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services import auth_service


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    real_name: str
    email: EmailStr
    phone: str | None = None


class MeResponse(BaseModel):
    id: int
    username: str
    real_name: str
    email: str | None = None
    phone: str | None = None
    role: str


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    try:
        token = auth_service.login(db, data.username, data.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    return LoginResponse(access_token=token)


@router.post("/register", response_model=LoginResponse)
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次输入的密码不一致",
        )
    # 这里可以加入更复杂的密码强度校验逻辑
    try:
        _, token = auth_service.register_user(
            db,
            username=data.username,
            password=data.password,
            real_name=data.real_name,
            email=str(data.email),
            phone=data.phone,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return LoginResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
    )
