import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from bodymetric import BodyMetric
from data_manager import DataManager
from date_entry import create_date_entry
from theme import BG

class BodyMetricDialog(tk.Toplevel):
    def __init__(self, master, username):
        super().__init__(master, bg=BG)
        self.title("Chỉ số cơ thể (BMI)")
        self.geometry("350x300")
        self.resizable(False, False)
        self.transient(master)
        self.username = username
        self.db = DataManager("bodymetrics.json")

        self.columnconfigure(1, weight=1)
        pad = {"padx": 10, "pady": 10}

        ttk.Label(self, text="Ngày đo:", background=BG).grid(row=0, column=0, sticky="w", **pad)
        self.date_entry = create_date_entry(self)
        self.date_entry.grid(row=0, column=1, sticky="w", **pad)

        ttk.Label(self, text="Cân nặng (kg):", background=BG).grid(row=1, column=0, sticky="w", **pad)
        self.var_weight = tk.StringVar()
        ttk.Entry(self, textvariable=self.var_weight, width=15).grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(self, text="Chiều cao (cm):", background=BG).grid(row=2, column=0, sticky="w", **pad)
        self.var_height = tk.StringVar()
        ttk.Entry(self, textvariable=self.var_height, width=15).grid(row=2, column=1, sticky="w", **pad)

        # Khu vực hiển thị kết quả
        self.lbl_result = tk.Label(self, text="", bg=BG, font=("Segoe UI", 11, "bold"), fg="#2f5fd0")
        self.lbl_result.grid(row=3, column=0, columnspan=2, pady=15)

        btns = ttk.Frame(self)
        btns.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Tính BMI & Lưu", command=self.save_metric).grid(row=0, column=0, padx=5)
        ttk.Button(btns, text="Đóng", command=self.destroy).grid(row=0, column=1, padx=5)

    def save_metric(self):
        try:
            w = float(self.var_weight.get())
            h = float(self.var_height.get())
            date_str = self.date_entry.get()

 
            metric = BodyMetric(
                metric_id=f"M{int(datetime.now().timestamp())}",
                user_id=self.username,
                date=date_str,
                weight_kg=w,
                height_cm=h
            )
            
            if self.db.create(metric.to_dict()):
                category = metric.get_bmi_category()
                self.lbl_result.config(text=f"BMI: {metric.bmi} - {category}")
                messagebox.showinfo("Thành công", "Đã lưu chỉ số cơ thể!", parent=self)
            else:
                messagebox.showerror("Lỗi", "Không thể lưu dữ liệu.", parent=self)

        except ValueError as e:
            messagebox.showwarning("Sai dữ liệu", str(e), parent=self)
