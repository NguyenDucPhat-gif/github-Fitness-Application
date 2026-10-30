# -*- coding: utf-8 -*-
"""
Goal.py - Mục tiêu: đạt tổng số phút hoặc calo trong một khoảng ngày
(dùng is_valid_date và date_key có sẵn trong Plan.py)
"""
from Plan import is_valid_date, date_key


class Goal:
    """Mục tiêu của một người dùng: đạt tổng số phút hoặc calo trong một khoảng ngày."""
    GOAL_TYPES = ["minutes", "calories"]                 # loại mục tiêu cho phép
    SPORTS = ["Running", "Swimming", "Cycling"]          # môn cho phép (None = tất cả các môn)

    # ---------- (1) Khởi tạo ----------
    def __init__(self, goal_id, user_id, name, goal_type, target_value,
                 start_date, end_date, sport=None):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Tên mục tiêu không được để trống")
        if goal_type not in Goal.GOAL_TYPES:
            raise ValueError("Loại mục tiêu phải là 'minutes' hoặc 'calories'")
        if not isinstance(target_value, (int, float)) or target_value <= 0:
            raise ValueError("Chỉ tiêu phải là số lớn hơn 0")
        if not is_valid_date(start_date) or not is_valid_date(end_date):
            raise ValueError("Ngày bắt đầu và ngày kết thúc phải có dạng dd/mm/yyyy")
        if date_key(end_date) < date_key(start_date):
            raise ValueError("Ngày kết thúc phải sau hoặc bằng ngày bắt đầu")
        if sport is not None and sport not in Goal.SPORTS:
            raise ValueError("Môn tập không hợp lệ")
        self.goal_id = goal_id
        self.user_id = user_id
        self.name = name
        self.goal_type = goal_type
        self.target_value = target_value
        self.start_date = start_date
        self.end_date = end_date
        self.sport = sport

    # ---------- (2) Tính tiến độ từ các buổi tập thật ----------
    def get_current_value(self, activities):
        """Tổng phút (hoặc calo) đã đạt được trong khoảng ngày của mục tiêu."""
        start = date_key(self.start_date)
        end = date_key(self.end_date)
        total = 0
        for a in activities:
            if a.user_id != self.user_id:
                continue
            if self.sport is not None and a.activity_type != self.sport:
                continue
            d = date_key(a.date)
            if d < start or d > end:
                continue
            if self.goal_type == "minutes":
                total += a.duration
            else:
                total += a.calories
        return round(total, 1)

    def get_progress(self, activities):
        """Tiến độ (%), tối đa 100 (dùng cho CircularProgress)."""
        percent = self.get_current_value(activities) / self.target_value * 100
        if percent > 100:
            percent = 100
        return round(percent, 1)

    def get_remaining(self, activities):
        """Còn thiếu bao nhiêu để đạt mục tiêu (không âm)."""
        remaining = self.target_value - self.get_current_value(activities)
        if remaining < 0:
            remaining = 0
        return round(remaining, 1)

    def is_achieved(self, activities):
        return self.get_current_value(activities) >= self.target_value

    # ---------- (3) Chuyển đổi JSON ----------
    def to_dict(self):
        return {"goal_id": self.goal_id, "user_id": self.user_id, "name": self.name,
                "goal_type": self.goal_type, "target_value": self.target_value,
                "start_date": self.start_date, "end_date": self.end_date,
                "sport": self.sport}

    @staticmethod
    def from_dict(d):
        return Goal(d["goal_id"], d["user_id"], d["name"], d["goal_type"],
                    d["target_value"], d["start_date"], d["end_date"], d.get("sport"))
