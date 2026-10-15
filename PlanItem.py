# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 11:00:47 2026

@author: this pc
"""
import re


class PlanItem:
    """Một mục trong kế hoạch: ngày nào, tập bài nào, dự kiến bao nhiêu phút."""
    def __init__(self, date, exercise_id, planned_minutes):
        self.date = date                          # đi qua setter
        self.exercise_id = exercise_id            # đi qua setter
        self.planned_minutes = planned_minutes    # đi qua setter

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if not re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/\d{4}$", value):
            raise ValueError("Ngày phải có dạng dd/mm/yyyy")           
        self._date = value

    @property
    def exercise_id(self):
        return self._exercise_id

    @exercise_id.setter
    def exercise_id(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Mã bài tập không được để trống")
        self._exercise_id = value

    @property
    def planned_minutes(self):
        return self._planned_minutes

    @planned_minutes.setter
    def planned_minutes(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Thời lượng dự kiến phải là số lớn hơn 0")
        self._planned_minutes = value

    def to_dict(self):
        return {"date": self.date, "exercise_id": self.exercise_id,
                "planned_minutes": self.planned_minutes}

    @staticmethod
    def from_dict(d):
        return PlanItem(d["date"], d["exercise_id"], d["planned_minutes"])