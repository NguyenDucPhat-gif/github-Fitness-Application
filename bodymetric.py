# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 13:55:36 2026

@author: this pc
"""

# -*- coding: utf-8 -*-
"""
BodyMetric.py - Chỉ số cơ thể của người dùng tại một ngày (cân nặng, chiều cao, BMI)
"""

import re
DATE_PATTERN = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/\d{4}$" 

class BodyMetric:
    """Một lần đo chỉ số cơ thể của một người dùng."""
    MIN_WEIGHT = 20       # kg
    MAX_WEIGHT = 300
    MIN_HEIGHT = 50       # cm
    MAX_HEIGHT = 250

    # ---------- (1) Khởi tạo ----------
    def __init__(self, metric_id, user_id, date, weight_kg, height_cm):
        self.metric_id = metric_id
        self.user_id = user_id
        self.date = date                  # đi qua setter
        self.weight_kg = weight_kg        # đi qua setter
        self.height_cm = height_cm        # đi qua setter

    # ---------- (2) Thuộc tính có kiểm tra dữ liệu ----------
    @property
    def date(self):
        return self._date

    
    @date.setter
    def date(self, value):
        if not re.match(DATE_PATTERN, value):
              raise ValueError("Ngày phải có dạng dd/mm/yyyy")
        self._date = value
      

    @property
    def weight_kg(self):
        return self._weight_kg

    @weight_kg.setter
    def weight_kg(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Cân nặng phải là số")
        if value < BodyMetric.MIN_WEIGHT or value > BodyMetric.MAX_WEIGHT:
            raise ValueError(f"Cân nặng phải từ {BodyMetric.MIN_WEIGHT} đến {BodyMetric.MAX_WEIGHT} kg")
        self._weight_kg = value

    @property
    def height_cm(self):
        return self._height_cm

    @height_cm.setter
    def height_cm(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Chiều cao phải là số")
        if value < BodyMetric.MIN_HEIGHT or value > BodyMetric.MAX_HEIGHT:
            raise ValueError(f"Chiều cao phải từ {BodyMetric.MIN_HEIGHT} đến {BodyMetric.MAX_HEIGHT} cm")
        self._height_cm = value

    # ---------- (3) Tính toán ----------
    @property
    def bmi(self):
        """BMI = cân nặng (kg) / chiều cao (m) bình phương."""
        meters = self.height_cm / 100
        return round(self.weight_kg / (meters * meters), 1)

    def get_bmi_category(self):
        """Phân loại theo thang WHO (dựa trên BMI đã làm tròn 1 chữ số)."""
        b = self.bmi
        if b < 18.5:
            return "Gầy"
        if b < 25:
            return "Bình thường"
        if b < 30:
            return "Thừa cân"
        return "Béo phì"

    # ---------- (4) Chuyển đổi JSON ----------
    def to_dict(self):
        return {"metric_id": self.metric_id, "user_id": self.user_id, "date": self.date,
                "weight_kg": self.weight_kg, "height_cm": self.height_cm, "bmi": self.bmi}

    @staticmethod
    def from_dict(d):
        return BodyMetric(d["metric_id"], d["user_id"], d["date"],
                          d["weight_kg"], d["height_cm"])
