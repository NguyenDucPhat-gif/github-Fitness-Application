"""Combobox mon + bai tap (loc theo mon), Radiobutton cuong do, Entry thoi luong.
(Phan chon ngay dung muc28_date_entry.py - muc 28)."""
import tkinter as tk
from tkinter import ttk, messagebox

import data

from date_entry import create_date_entry
from theme import apply_style


class SessionForm(ttk.LabelFrame):
    def __init__(self, master, on_save=None, on_edit=None, on_delete=None):
        super().__init__(master, text="Buổi tập")
        self.editing_id = None
        for c in range(4):
            self.columnconfigure(c, weight=1 if c % 2 else 0)
        pad = {"padx": 6, "pady": 4}

        ttk.Label(self, text="Ngày").grid(row=0, column=0, sticky="w", **pad)
        self.date = create_date_entry(self)
        self.date.grid(row=0, column=1, sticky="w", **pad)

        ttk.Label(self, text="Môn").grid(row=0, column=2, sticky="w", **pad)
        self.cb_sport = ttk.Combobox(self, values=list(data.EXERCISES),
                                     state="readonly")
        self.cb_sport.grid(row=0, column=3, sticky="ew", **pad)
        self.cb_sport.bind("<<ComboboxSelected>>", self._on_sport_change)

        ttk.Label(self, text="Bài tập").grid(row=1, column=0, sticky="w", **pad)
        self.cb_ex = ttk.Combobox(self, state="readonly")
        self.cb_ex.grid(row=1, column=1, sticky="ew", **pad)

        ttk.Label(self, text="Thời lượng (phút)").grid(row=1, column=2, sticky="w", **pad)
        self.var_min = tk.StringVar()
        ttk.Entry(self, textvariable=self.var_min).grid(row=1, column=3, sticky="ew", **pad)

        ttk.Label(self, text="Cường độ").grid(row=2, column=0, sticky="w", **pad)
        rb = ttk.Frame(self)
        rb.grid(row=2, column=1, columnspan=3, sticky="w", **pad)
        self.var_int = tk.StringVar(value="Vừa")
        for i, name in enumerate(data.INTENSITY):
            ttk.Radiobutton(rb, text=name, value=name, variable=self.var_int
                            ).grid(row=0, column=i, padx=8)

        bt = ttk.Frame(self)
        bt.grid(row=3, column=0, columnspan=4, sticky="e", padx=6, pady=6)
        self.btn_save = ttk.Button(bt, text="Thêm", command=on_save)
        self.btn_save.grid(row=0, column=0, padx=3)
        ttk.Button(bt, text="Sửa dòng chọn", command=on_edit).grid(row=0, column=1, padx=3)
        ttk.Button(bt, text="Xóa", command=on_delete).grid(row=0, column=2, padx=3)
        ttk.Button(bt, text="Làm mới form", command=self.clear).grid(row=0, column=3, padx=3)

    def _on_sport_change(self, _=None):
        """Loc bai tap theo mon da chon."""
        self.cb_ex["values"] = data.EXERCISES.get(self.cb_sport.get(), [])
        self.cb_ex.set("")

    def read(self):
        """Tra ve dict du lieu hop le, hoac None neu thieu/sai (da bao loi)."""
        sport, ex = self.cb_sport.get(), self.cb_ex.get()
        if not sport or not ex:
            messagebox.showwarning("Thiếu dữ liệu", "Hãy chọn môn và bài tập.")
            return None
        try:
            minutes = int(self.var_min.get())
            if minutes <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Thời lượng phải là số nguyên dương.")
            return None
        inten = self.var_int.get()
        return {"date": self.date.get(), "sport": sport, "exercise": ex,
                "minutes": minutes, "intensity": inten,
                "cal": data.calc_calories(sport, minutes, inten)}

    def fill(self, s):
        """Nap 1 buoi tap vao form de sua."""
        self.editing_id = s["id"]
        self.date.set_date(s["date"])
        self.cb_sport.set(s["sport"])
        self._on_sport_change()
        self.cb_ex.set(s["exercise"])
        self.var_min.set(str(s["minutes"]))
        self.var_int.set(s["intensity"])
        self.btn_save.config(text="Cập nhật")

    def clear(self):
        self.editing_id = None
        self.cb_sport.set("")
        self.cb_ex.set("")
        self.cb_ex["values"] = []
        self.var_min.set("")
        self.var_int.set("Vừa")
        self.btn_save.config(text="Thêm")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Demo form")
    apply_style(root)

    def show():
        d = form.read()
        if d:
            messagebox.showinfo("Dữ liệu form", str(d))

    form = SessionForm(root, on_save=show)
    form.pack(fill="x", padx=10, pady=10)
    root.mainloop()