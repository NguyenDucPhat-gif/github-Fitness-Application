# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 21:06:28 2026

@author: this pc
"""
import re

# LỚP CHA
class SportActivity:
    def __init__(self, activity_id, user_id, date, duration):
        self.activity_id = activity_id
        self.user_id = user_id
        self.date = date  #  gọi setter để check RegEx
        self.duration = duration
        self.activity_type = "General" # Mặc định
        
    

    @property
    def date(self):
        return self._date
    
    @date.setter
    def date(self, value):
        # Sử dụng RegEx kiểm tra ngày tháng (dd/mm/yyyy)
        pattern = r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/\d{4}$"
        if not re.match(pattern, value):
            raise ValueError("Ngày tháng phải có định dạng dd/mm/yyyy")
        self._date = value

    @property
    def duration(self):
        return self._duration
        
    @duration.setter
    def duration(self, value):
        if not isinstance(value, (int, float)) or value <= 0: #kiểm tra xem một biến có thuộc về một kiểu dữ liệu cụ thể nào không
            raise ValueError("Thời lượng phải là số lớn hơn 0")
        self._duration = value

    # Đa hình: Hàm này sẽ được các lớp con ghi đè (Override)
    def get_summary(self):
        pass
    
    @property
    def calorie(self):
        return self.calculate_calories()

    def calculate_calories(self):
        return 0;

    def to_dict(self):
        return {
            "activity_id": self.activity_id,
            "user_id": self.user_id,
            "date": self.date,
            "duration": self.duration,
            "calories": self.calories,
            "type": self.activity_type
        }

class Running(SportActivity):
    def __init__(self, activity_id, user_id, date, duration, distance):
        super().__init__(activity_id, user_id, date, duration)
        self.activity_type = "Running"
        self.distance = distance

    # Ghi đè (Override): Chạy bộ tính calo theo quãng đường
    def calculate_calories(self):
        # Trung bình 1km chạy bộ đốt khoảng 65 calo
        return round(self.distance * 65, 1)
    
    def get_summary(self):
        speed= round(self.distance/(self.duration/60),1) if self.duration >0 else 0
        return f"Quãng đường chạy bộ: {self.distance}km. Tốc độ: {speed} km/h. Đã đốt được {self.calories}."
    
class Swimming(SportActivity):
    def __init__(self, activity_id, user_id, date, duration, distance, swim_style):
        super().__init__(activity_id, user_id, date, duration)
        self.activity_type = "Swimming"
        self.distance = distance
        self.swim_style = swim_style

    # Ghi đè (Override): Bơi lội tính calo theo thời gian và kiểu bơi
    def calculate_calories(self):
        # Hệ số đốt calo mỗi phút tùy kiểu bơi
        calo_per_min = {
            "Bơi bướm": 11,
            "Bơi ếch": 10,
            "Bơi sải": 8,
            "Bơi ngửa": 7
        }
        # Nếu nhập sai kiểu bơi, mặc định lấy hệ số 8
        factor = calo_per_min.get(self.swim_style, 8) 
        return round(self.duration * factor, 1)
    def get_summary(self):
        return f"Bơi kiểu {self.swim_style}. Đã đốt được {self.calories}. "
class Cycling(SportActivity):
    def __init__(self, activity_id, user_id, date, duration, distance, terrain):
        super().__init__(activity_id, user_id, date, duration)
        self.activity_type = "Cycling"
        self.distance = distance  # Đo bằng km
        self.terrain = terrain    # Ví dụ: "Đường bằng", "Đường dốc", "Trong nhà"

    # Ghi đè (Override): Đạp xe tính calo theo địa hình
    def calculate_calories(self):
        # Hệ số đốt calo mỗi phút tùy thuộc vào độ khó của địa hình
        calo_per_min = {
            "Trong nhà": 7,      
            "Đường bằng": 8,     
            "Đường dốc": 12      
        }
        # Nếu không có trong danh sách, mặc định lấy hệ số 8
        factor = calo_per_min.get(self.terrain, 8)
        return round(self.duration * factor, 1)

    # Ghi đè phương thức tóm tắt
    def get_summary(self):
        # Tính tốc độ trung bình (km/h) = Quãng đường / Thời gian (giờ)
        speed = round(self.distance / (self.duration / 60), 1) if self.duration > 0 else 0
        return f"Đạp xe ({self.terrain}): {self.distance}km. Tốc độ: {speed} km/h. Đã đốt được {self.calories}."