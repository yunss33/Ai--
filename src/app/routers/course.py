from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.core.database import get_db


class Course(BaseModel):
    id: int
    title: str
    description: str | None = None
    owner_id: int | None = None


router = APIRouter()


@router.get("/courses", response_model=List[Course])
async def list_courses(db: Session = Depends(get_db)) -> List[Course]:
    return [
        Course(id=1, title="Demo Course", description="Sample course", owner_id=None),
    ]


@router.get("/courses/{course_id}", response_model=Course)
async def get_course(
    course_id: int,
    db: Session = Depends(get_db),
) -> Course:
    return Course(id=course_id, title="Demo Course", description="Sample course", owner_id=None)
