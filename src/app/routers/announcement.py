from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.core.database import get_db


class Announcement(BaseModel):
    id: int
    course_id: int | None = None
    title: str
    content: str


router = APIRouter()


@router.get("/announcements", response_model=List[Announcement])
async def list_announcements(
    db: Session = Depends(get_db),
) -> List[Announcement]:
    return [
        Announcement(
            id=1,
            course_id=None,
            title="System Announcement",
            content="Welcome to the AI Course Platform.",
        ),
    ]
