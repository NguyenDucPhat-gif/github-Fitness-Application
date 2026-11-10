# -*- coding: utf-8 -*-
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
        pass

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
     username = d.get("username", "")
     password = d.get("password", "")
     fullname = d.get("fullname", "")
     email = d.get("email", "")
     role = d.get("role", "user")
     
     if role == "admin":
         return Admin(username, password, fullname, email)
     else:
         cal_aim = d.get("calories_aim", 2000)
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
    
    
