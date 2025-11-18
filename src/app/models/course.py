from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.database import Base


class Course(Base):
    __tablename__ = "course"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1024))
    owner_id = Column(Integer, ForeignKey("user.id"))
    cover_url = Column(String(255))
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class CourseEnrollment(Base):
    __tablename__ = "course_enrollment"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    enroll_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(20), default="active", nullable=False)


class Chapter(Base):
    __tablename__ = "chapter"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)


class Lesson(Base):
    __tablename__ = "lesson"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapter.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(String)
    order_index = Column(Integer, nullable=False, default=0)
