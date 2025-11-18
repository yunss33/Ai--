from __future__ import annotations

from datetime import time

from fastapi import APIRouter

from Data.Entity.CourseSlot import CourseSlot
from Data.Entity.StudentSchedule import StudentSchedule


router = APIRouter()


@router.get("/schedule/sample")
async def get_sample_schedule() -> StudentSchedule:
    """
    返回一个示例课程表，用于演示学生课程表接口结构。
    后续可以对接数据库，根据当前学生真实返回。
    """
    slots = [
        CourseSlot(
            course_id=1,
            course_title="示例课程 A",
            weekday=1,
            start_time=time(9, 0),
            end_time=time(9, 45),
            location="教学楼 1-101",
        ),
        CourseSlot(
            course_id=2,
            course_title="示例课程 B",
            weekday=3,
            start_time=time(14, 0),
            end_time=time(14, 45),
            location="教学楼 2-203",
        ),
    ]
    return StudentSchedule(student_id=1, slots=slots)
