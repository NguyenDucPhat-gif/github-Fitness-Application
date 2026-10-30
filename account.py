# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 01:04:16 2026

@author: this pc
"""
from abc import ABC, abstractmethod
import re
import hashlib

class Account(ABC):
    def __init__(self, username, password, fullname, email):
        self._username = username
   
        self._password = password
        self._fullname = fullname
        self.email = email
        self._access_level = ""
        
    @staticmethod
    def hash_password(password):
        """Chuyển mật khẩu thành chuỗi băm SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
        
    def Sign_In(self, password_input):
        return self._password == self.hash_password(password_input)
    @property 
    def email(self) :
       return self._email
   
    @email.setter
    def email(self, value):
     pattern =r"^[\w\.-]+@[\w\.-]+\.\w+$"
     if not re.match(pattern, value):  
      raise ValueError("Email không hợp lệ")
     self._email= value
     
    

    @abstractmethod
    def Access_Level(self):
        "Lớp con tự ovveride phương thức này"

    def to_dict(self):
        return {
        "username": self._username,
        "password": self._password,
        "fullname": self._fullname,
        "email": self.email,
        "role": self._access_level,
    }
    @staticmethod
    def from_dict(d):
     """Đọc dữ liệu từ JSON, hỗ trợ cả key cũ (_username) và key mới (username)"""
     username = d.get("username", d.get("_username", ""))
     password = d.get("password", d.get("_password", ""))
     fullname = d.get("fullname", d.get("_fullname", ""))
     email = d.get("email", d.get("_email", ""))
     role = d.get("role", d.get("_access_level", "user"))
     
     if role == "admin":
         return Admin(username, password, fullname, email)
     else:
         cal_aim = d.get("calories_aim", d.get("_UserCalories_Aim", 2000))
         return User(username, password, fullname, email, cal_aim)

class Admin(Account):
    def __init__(self, username, password, fullname, email):
        super().__init__(username, password, fullname, email)
        self._access_level = "admin"

    def Access_Level(self):
        return "admin"
    
class User(Account):
    def __init__(self, username, password, fullname, email, UserCalories_Aim=2000):
        super().__init__(username, password, fullname, email)
        self._access_level = "user"
        self._UserCalories_Aim = UserCalories_Aim

    def Access_Level(self):
        return "user"
    def to_dict(self):
      return {**super().to_dict(), "calories_aim": self._UserCalories_Aim}
    
    
