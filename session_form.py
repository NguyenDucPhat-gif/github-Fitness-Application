"""Form ghi nhận buổi tập (Sử dụng hệ thống OOP của Sports.py)"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import config

from date_entry import create_date_entry
from data_manager import DataManager
from sports import Exercise, Running, Swimming, Cycling
from theme import apply_style

class SessionForm(ttk.LabelFrame):
    def __init__(self, master, user_id, on_save=None, on_edit=None, on_delete=None):
        super().__init__(master, text="Ghi nhận buổi tập")
        self.user_id = user_id
        self.on_save = on_save
        self.editing_id = None
        
    
        self.exercises = [Exercise.from_dict(d) for d in DataManager("exercises.json").load_data()]
        
        for c in range(4):
            self.columnconfigure(c, weight=1 if c % 2 else 0)
        pad = {"padx": 6, "pady": 2}

        ttk.Label(self, text="Ngày").grid(row=0, column=0, sticky="w", **pad)
        self.date = create_date_entry(self)
        self.date.grid(row=0, column=1, sticky="w", **pad)

        ttk.Label(self, text="Môn").grid(row=0, column=2, sticky="w", **pad)
        self.cb_sport = ttk.Combobox(self, values=list(config.SPORT_VI.values()), state="readonly")
        self.cb_sport.grid(row=0, column=3, sticky="ew", **pad)
        self.cb_sport.bind("<<ComboboxSelected>>", self._on_sport_change)

        ttk.Label(self, text="Bài tập").grid(row=1, column=0, sticky="w", **pad)
        self.cb_ex = ttk.Combobox(self, state="readonly")
        self.cb_ex.grid(row=1, column=1, columnspan=3, sticky="ew", **pad)

        ttk.Label(self, text="Thời lượng (phút)").grid(row=2, column=0, sticky="w", **pad)
        self.var_min = tk.StringVar()
        ttk.Entry(self, textvariable=self.var_min).grid(row=2, column=1, sticky="ew", **pad)

        ttk.Label(self, text="Quãng đường (km)").grid(row=2, column=2, sticky="w", **pad)
        self.var_dist = tk.StringVar()
        ttk.Entry(self, textvariable=self.var_dist).grid(row=2, column=3, sticky="ew", **pad)

        ttk.Label(self, text="Cường độ").grid(row=3, column=0, sticky="w", **pad)
        rb = ttk.Frame(self)
        rb.grid(row=3, column=1, columnspan=3, sticky="w", **pad)
        self.var_int = tk.StringVar(value="Vừa")
        for i, name in enumerate(["Nhẹ", "Vừa", "Cao"]):
            ttk.Radiobutton(rb, text=name, value=name, variable=self.var_int).grid(row=0, column=i, padx=8)

        bt = ttk.Frame(self)
        bt.grid(row=4, column=0, columnspan=4, sticky="e", padx=6, pady=6)
        self.btn_save = ttk.Button(bt, text="Lưu buổi tập", command=self._submit)
        self.btn_save.grid(row=0, column=0, padx=3)
        ttk.Button(bt, text="Làm mới form", command=self.clear).grid(row=0, column=1, padx=3)

    def _on_sport_change(self, _=None):
        sport_vi = self.cb_sport.get()
        sport_en = config.SPORT_EN.get(sport_vi, sport_vi) 
        filtered = [ex.name for ex in self.exercises if ex.sport == sport_en]
        self.cb_ex["values"] = filtered
        if filtered: self.cb_ex.current(0)

    def _submit(self):
        sport_vi = self.cb_sport.get()
        sport_en = config.SPORT_EN.get(sport_vi, sport_vi) 
        ex_name = self.cb_ex.get()
        
        if not sport_en or not ex_name:
            messagebox.showwarning("Lỗi", "Hãy chọn môn và bài tập.")
            return

     
        try:
            minutes = float(self.var_min.get())
            if minutes <= 0: 
                raise ValueError
            dist = float(self.var_dist.get()) if self.var_dist.get().strip() else 0
        except ValueError:
            messagebox.showwarning("Lỗi", "Thời lượng/Quãng đường phải là số dương.")
            return

        ex_obj = next((e for e in self.exercises if e.name == ex_name), None)
        act_id = self.editing_id if self.editing_id else f"A{int(datetime.now().timestamp())}"
        
       
        if sport_en == "Running":
            act = Running(act_id, self.user_id, self.date.get(), minutes, dist, ex_obj, self.var_int.get())
        elif sport_en == "Swimming":
            act = Swimming(act_id, self.user_id, self.date.get(), minutes, dist, ex_obj, self.var_int.get())
        else:
            act = Cycling(act_id, self.user_id, self.date.get(), minutes, dist, ex_obj, self.var_int.get())

        
        if self.on_save:
            self.on_save(act)
            
        self.clear()

    def fill(self, act):
        self.editing_id = act.activity_id
        self.date.set_date(act.date)
        
        self.cb_sport.set(config.SPORT_VI.get(act.activity_type, act.activity_type))
        self._on_sport_change()
        self.cb_ex.set(act.exercise.name if act.exercise else "")
        self.var_min.set(str(act.duration))
        self.var_dist.set(str(act.distance))
        self.var_int.set(act.intensity)
        self.btn_save.config(text="Cập nhật")

    def clear(self):
        self.editing_id = None
        self.cb_sport.set("")
        self.cb_ex.set("")
        self.cb_ex["values"] = []
        self.var_min.set("")
        self.var_dist.set("")
        self.var_int.set("Vừa")
        self.btn_save.config(text="Lưu buổi tập")