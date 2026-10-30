"""Hop thoai danh sach tai khoan (chi quan tri vien). Toplevel chi dung grid.
(Doi mat khau nam trong login.py)"""
import tkinter as tk
from tkinter import ttk

import config
import data
from theme import BG


class AccountListDialog(tk.Toplevel):
    """Danh sach tai khoan (khong hien mat khau) - chi quan tri vien."""
    def __init__(self, master):
        super().__init__(master, bg=BG)
        self.title("Danh sách tài khoản")
        self.transient(master)
        self.geometry("420x280")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        tree = ttk.Treeview(self, columns=("name", "role", "n"), show="headings")
        for key, title, w in (("name", "Tài khoản", 140), ("role", "Vai trò", 120), ("n", "Số buổi tập", 90)):
            tree.heading(key, text=title)
            tree.column(key, width=w, anchor="w" if key != "n" else "center")
        for name, role, n in data.list_users():
            tree.insert("", "end", values=(name, config.ROLE_LABEL.get(role, role), n))
        tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ttk.Button(self, text="Đóng", command=self.destroy).grid(row=1, column=0, pady=(0, 10))