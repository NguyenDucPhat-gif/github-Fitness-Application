"""Cot: ID, ngay, mon, bai tap, phut, cuong do, calo."""
import tkinter as tk
from tkinter import ttk

from theme import apply_style

COLS = [("id", "ID", 50), ("date", "Ngày", 90), ("sport", "Môn", 100),
        ("exercise", "Bài tập", 140), ("minutes", "Phút", 60),
        ("intensity", "Cường độ", 80), ("cal", "Calo", 70)]


class SessionTable(ttk.LabelFrame):
    def __init__(self, master, on_double_click=None):
        super().__init__(master, text="Danh sách")
        self.sort_state = {}
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(self, columns=[c[0] for c in COLS],
                                 show="headings", selectmode="browse")
        for key, title, w in COLS:
            self.tree.heading(key, text=title, command=lambda k=key: self.sort_by(k))
            self.tree.column(key, width=w, minwidth=40,
                             anchor="w" if key in ("sport", "exercise") else "center")
        ys = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ys.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        ys.grid(row=0, column=1, sticky="ns", padx=(0, 6), pady=6)

        self.lbl_total = ttk.Label(self, text="")
        self.lbl_total.grid(row=1, column=0, columnspan=2, sticky="e", padx=8, pady=(0, 6))

        if on_double_click:
            self.tree.bind("<Double-1>", lambda e: on_double_click())

    def load(self, rows):
        """Do danh sach dict vao bang."""
        self.tree.delete(*self.tree.get_children())
        for s in rows:
            self.tree.insert("", "end", iid=str(s["id"]), values=(
                s["id"], s["date"], s["sport"], s["exercise"],
                s["minutes"], s["intensity"], s["cal"]))
        self.lbl_total.config(
            text=f"{len(rows)} buổi - tổng {sum(s['cal'] for s in rows)} calo")

    def selected_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def sort_by(self, key):
        desc = self.sort_state.get(key, False)

        def conv(v):
            if key == "date":                  # dd/mm/yyyy -> yyyymmdd
                d, m, y = v.split("/")
                return y + m + d
            return float(v) if key in ("id", "minutes", "cal") else v.lower()

        rows = [(self.tree.set(i, key), i) for i in self.tree.get_children("")]
        rows.sort(key=lambda r: conv(r[0]), reverse=desc)
        for idx, (_, iid) in enumerate(rows):
            self.tree.move(iid, "", idx)
        self.sort_state[key] = not desc


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Demo Treeview")
    root.geometry("650x350")
    apply_style(root)
    t = SessionTable(root)
    t.pack(fill="both", expand=True, padx=10, pady=10)
    t.load([
        {"id": 1, "date": "10/10/2026", "sport": "Gym", "exercise": "Squat",
         "minutes": 45, "intensity": "Nặng", "cal": 410},
        {"id": 2, "date": "12/10/2026", "sport": "Chạy bộ", "exercise": "Chạy chậm",
         "minutes": 30, "intensity": "Vừa", "cal": 300},
    ])
    root.mainloop()