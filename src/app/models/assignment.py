from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.core.database import Base


class Assignment(Base):
    """作业表：描述每个课程布置的作业任务。

    仅存储作业本身的信息（标题、说明、截止时间等），不包含学生提交。
    """
    __tablename__ = "assignment"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_time = Column(DateTime)
    max_score = Column(Integer, default=100, nullable=False)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class AssignmentSubmission(Base):
    """作业提交表：记录学生对某次作业的具体提交。

    包含提交内容、附件、得分和人工/AI 评语等信息。
    """
    __tablename__ = "assignment_submission"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(
        Integer,
        ForeignKey("assignment.id"),
        nullable=False,
        index=True,
    )
    student_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    attachments = Column(Text)
    score = Column(Integer)
    review_comment = Column(Text)
    ai_comment = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
