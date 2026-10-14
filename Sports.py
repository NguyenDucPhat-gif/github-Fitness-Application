# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 21:06:28 2026

@author: this pc
"""
import re

INTENSITY_FACTOR={"Nhẹ": 0.8, "Vừa": 1.0, "Cao": 1.3}

class Exercise:
    def __init__(self, exercise_id, name, sport, calo_rate):
        self.exercise_id=exercise_id
        self.name = name
        self.sport= sport
        self.calo_rate= calo_rate
        
    @staticmethod
    def from_dict(d):
        return Exercise(d["exercise_id"], d["name"], d["sport"], d["calo_rate"])
        
class SportActivity:
    """Lớp cha: một buổi tập."""
    def __init__(self, activity_id, user_id, date, duration, distance=0,
                 exercise=None, intensity="Vừa"):
        self.activity_id = activity_id
        self.user_id = user_id
        self.date = date              # qua setter -> kiểm tra regex
        self.duration = duration      # qua setter -> kiểm tra > 0
        self.distance = distance
        self.exercise = exercise      # đối tượng Exercise (has-a)
        self.intensity = intensity
        self.activity_type = "General"

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if not re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/\d{4}$", value):
            raise ValueError("Ngày phải có dạng dd/mm/yyyy")
        self._date = value

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Thời lượng phải là số lớn hơn 0")
        self._duration = value

    @property
    def intensity_factor(self):
        return INTENSITY_FACTOR.get(self.intensity, 1.0)

    @property
    def calories(self):
        return self.calculate_calories()

    def calculate_calories(self):      # lớp con ghi đè
        return 0

    def get_summary(self):             # lớp con ghi đè
        return ""

    def to_dict(self):
        return {
            "activity_id": self.activity_id,
            "user_id": self.user_id,
            "type": self.activity_type,
            "exercise_id": self.exercise.exercise_id if self.exercise else None,
            "date": self.date,
            "duration": self.duration,
            "distance": self.distance,
            "intensity": self.intensity,
            "calories": self.calories,
        }
    
class Running(SportActivity):
    def __init__(self, activity_id, user_id, date, duration, distance=0,
                 exercise=None, intensity="Vừa"):
        super().__init__(activity_id, user_id, date, duration, distance,
                         exercise, intensity)
        self.activity_type = "Running"

    def calculate_calories(self):      # theo QUÃNG ĐƯỜNG
        rate = self.exercise.calo_rate if self.exercise else 65
        return round(self.distance * rate * self.intensity_factor, 1)

    def get_summary(self):
        speed = round(self.distance / (self.duration / 60), 1)
        return f"Chạy {self.distance}km, {speed} km/h, đốt {self.calories} calo"


class Swimming(SportActivity):
    def __init__(self, activity_id, user_id, date, duration, distance=0,
                 exercise=None, intensity="Vừa"):
        super().__init__(activity_id, user_id, date, duration, distance,
                         exercise, intensity)
        self.activity_type = "Swimming"

    def calculate_calories(self):      # theo THỜI GIAN
        rate = self.exercise.calo_rate if self.exercise else 8
        return round(self.duration * rate * self.intensity_factor, 1)

    def get_summary(self):
        return f"Bơi {self.duration} phút, đốt {self.calories} calo"


class Cycling(SportActivity):
    def __init__(self, activity_id, user_id, date, duration, distance=0,
                 exercise=None, intensity="Vừa"):
        super().__init__(activity_id, user_id, date, duration, distance,
                         exercise, intensity)
        self.activity_type = "Cycling"

    def calculate_calories(self):      # theo THỜI GIAN
        rate = self.exercise.calo_rate if self.exercise else 8
        return round(self.duration * rate * self.intensity_factor, 1)

    def get_summary(self):
        return f"Đạp xe {self.distance}km, đốt {self.calories} calo"


ACTIVITY_CLASSES = {"Running": Running, "Swimming": Swimming, "Cycling": Cycling}


def activity_from_dict(d, exercises):
    """Dựng lại object từ dict JSON. exercises = {exercise_id: Exercise}"""
    cls = ACTIVITY_CLASSES[d["type"]]
    return cls(d["activity_id"], d["user_id"], d["date"], d["duration"],
               d.get("distance", 0), exercises.get(d.get("exercise_id")),
               d.get("intensity", "Vừa"))