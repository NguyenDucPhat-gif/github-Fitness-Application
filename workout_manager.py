# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 14:39:54 2026

@author: this pc
"""

from sports import activity_from_dict


class WorkoutManager:
    def __init__(self, data_manager, exercises):
        self.db = data_manager                        
        self.exercises = {e.exercise_id: e for e in exercises}
        self.activities_list = []
        for d in self.db.load_data():                
            self.activities_list.append(activity_from_dict(d, self.exercises))

    def add_activity(self, act):
        for act_in_list in self.activities_list:
           if act_in_list.activity_id == act.activity_id:     
            return False
        if self.db.create(act.to_dict()):       
             self.activities_list.append(act)                   
             return True
        return False

    def delete_activity(self, activity_id):           
        self.activities_list = [a for a in self.activities_list if a.activity_id != activity_id]
        return self.db.delete("activity_id", activity_id)

    def filter(self, sport=None, date=None):          
        return [a for a in self.activities_list
                if (sport is None or a.activity_type == sport)
                and (date is None or a.date == date)]

    def get_total_calories_by_date(self, date):
        return round(sum(a.calories for a in self.filter(date=date)), 1)

    def get_total_duration(self, sport=None, date=None):
        return sum(a.duration for a in self.filter(sport, date))
    
    def update_activity(self, activity_id, new_act):
        if new_act.activity_id!= activity_id:return False
        for i, act in enumerate(self.activities_list):
            if act.activity_id== activity_id:
                if self.db.update("activity_id", activity_id, new_act.to_dict()):
                   self.activities_list[i]= new_act
                   return True
                return False
        return False         