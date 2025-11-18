#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .CourseSlot import CourseSlot


@dataclass
class StudentSchedule:
    """学生课程表实体（聚合若干 CourseSlot）"""

    student_id: int
    slots: List[CourseSlot]

