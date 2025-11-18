from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.core.database import get_db


class Assignment(BaseModel):
    id: int
    course_id: int
    title: str
    description: str | None = None


class AssignmentSubmission(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    content: str


class CreateSubmissionRequest(BaseModel):
    content: str


router = APIRouter()


@router.get("/courses/{course_id}/assignments", response_model=List[Assignment])
async def list_assignments(
    course_id: int,
    db: Session = Depends(get_db),
) -> List[Assignment]:
    return [
        Assignment(id=1, course_id=course_id, title="Demo Assignment", description=None),
    ]


@router.get("/assignments/{assignment_id}", response_model=Assignment)
async def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
) -> Assignment:
    return Assignment(id=assignment_id, course_id=1, title="Demo Assignment", description=None)


@router.post(
    "/assignments/{assignment_id}/submissions",
    response_model=AssignmentSubmission,
)
async def submit_assignment(
    assignment_id: int,
    data: CreateSubmissionRequest,
    db: Session = Depends(get_db),
) -> AssignmentSubmission:
    return AssignmentSubmission(
        id=1,
        assignment_id=assignment_id,
        student_id=1,
        content=data.content,
    )
