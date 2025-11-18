#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Optional


@dataclass
class CourseSlot:
    """课程表中的单个时间格子"""

    course_id: int
    course_title: str
    weekday: int          # 1-7
    start_time: time
    end_time: time
    location: Optional[str] = None

