# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 01:04:16 2026

@author: this pc
"""
from abc import ABC, abstractmethod
import re

class Account(ABC):
    def __init__(self, username, password, fullname, email):
      
        self._username = username
        self._password = password       
        self._fullname = fullname
        self.email = email
        self._access_level = ""
        
    @property 
    def email(self) :
       return self._email
   
    @email.setter
    def email(self, value):
     pattern =r"^[\w\.-]+@[\w\.-]+\.\w+$"
     if not re.match(pattern, value):   #Regular Expression
      raise ValueError("Email không hợp lệ")
     self._email= value
     
    def Sign_In(self, password_input):
        return self._password == password_input

    @abstractmethod
    def Access_Level(self):
        "Lớp con tự ovveride phương thức này"

    def to_dict(self):
        return self.__dict__  # đơn giản hóa việc chuyển sang JSON

class Admin(Account):
    def __init__(self, username, password, fullname, email):
        super().__init__(username, password, fullname, email)
        self.access_level = "admin"

    def Access_Level(self):
        return "admin"
    
class User(Account):
    def __init__(self, username, password, fullname, email, UserCalories_Aim=2000):
        super().__init__(username, password, fullname, email)
        self._access_level = "user"
        self._UserCalories_Aim = UserCalories_Aim

    def Access_Level(self):
        return "user"
