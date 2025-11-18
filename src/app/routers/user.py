from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr

from sqlalchemy.orm import Session

from app.core.database import get_db


class UserProfile(BaseModel):
    id: int
    username: str
    real_name: str
    role: str
    email: EmailStr | None = None
    phone: str | None = None


class UpdateUserProfile(BaseModel):
    real_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_profile(db: Session = Depends(get_db)) -> UserProfile:
    return UserProfile(
        id=1,
        username="demo",
        real_name="Demo User",
        role="student",
        email="demo@example.com",
        phone=None,
    )


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    data: UpdateUserProfile,
    db: Session = Depends(get_db),
) -> UserProfile:
    return UserProfile(
        id=1,
        username="demo",
        real_name=data.real_name or "Demo User",
        role="student",
        email=data.email or "demo@example.com",
        phone=data.phone,
    )
