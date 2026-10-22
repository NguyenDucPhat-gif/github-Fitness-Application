""""Sap xep nam o muc26_treeview.py (bam vao tieu de cot)."""
import difflib
import tkinter as tk
from tkinter import ttk

from date_entry import create_date_entry

def filter_sessions(sessions, sport="Tất cả", day=None, keyword=""):
    """Loc danh sach dict theo mon, ngay va tu khoa."""
    kw = keyword.strip().lower()
    out = []
    for s in sessions:
        if sport != "Tất cả" and s.get("sport") != sport:
            continue
        if day and s.get("date") != day:
            continue
        if kw:
            text = f"{s.get('sport')} {s.get('exercise')} {s.get('intensity')}".lower()
            if kw not in text and not any(
                    difflib.SequenceMatcher(None, kw, w).ratio() >= 0.75
                    for w in text.split()): #tim gan dung
                continue
        out.append(s)
    return out


class FilterBar(ttk.Frame):
    def __init__(self, master, on_change):
        super().__init__(master)
        self.on_change = on_change

        ttk.Label(self, text="Môn").grid(row=0, column=0)
        # Đồng bộ môn với Sports.py
        self.cb_sport = ttk.Combobox(self, values=["Tất cả", "Running", "Swimming", "Cycling"], state="readonly", width=12)
        self.cb_sport.current(0)
        self.cb_sport.grid(row=0, column=1, padx=4)

        self.var_use_date = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Ngày", variable=self.var_use_date,
                        command=lambda: self.on_change()).grid(row=0, column=2, padx=(10, 0))
        self.date = create_date_entry(self, width=11)
        self.date.grid(row=0, column=3, padx=4)

        ttk.Label(self, text="Tìm").grid(row=0, column=4, padx=(10, 0))
        self.var_search = tk.StringVar()
        ttk.Entry(self, textvariable=self.var_search, width=18).grid(row=0, column=5, padx=4)
        ttk.Button(self, text="Bỏ lọc", command=self.reset).grid(row=0, column=6, padx=4)

        self.cb_sport.bind("<<ComboboxSelected>>", lambda e: self.on_change())
        self.date.bind("<<DateEntrySelected>>", lambda e: self.on_change())
        self.var_search.trace_add("write", lambda *a: self.on_change())

    def criteria(self):
        return {"sport": self.cb_sport.get(),
                "day": self.date.get() if self.var_use_date.get() else None,
                "keyword": self.var_search.get()}

    def reset(self):
        self.cb_sport.current(0)
        self.var_use_date.set(False)
        self.var_search.set("")
        self.on_change()