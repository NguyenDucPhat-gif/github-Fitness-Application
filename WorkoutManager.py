# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 14:39:54 2026

@author: this pc
"""

class WorkoutManager:
    def __init__(self):
        # Danh sách chứa các object Running, Swimming, Cycling...
        self.activities_list = [] 

    def add_activity(self, activity):
        self.activities_list.append(activity)

    # Phương thức lấy tổng calo đã đốt trong 1 ngày
    def get_total_calories_by_date(self, target_date):
        total_calo = 0
        for act in self.activities_list:
            if act.date == target_date:
                total_calo += act.calories 
        return round(total_calo, 1)