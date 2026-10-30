"""Nguon thu vien (ghi vao bao cao): tkcalendar - https://github.com/j4321/tkcalendar
Cai dat: pip install tkcalendar
"""
import tkinter as tk
from tkinter import messagebox

from tkcalendar import DateEntry

from theme import DATE_FMT, apply_style


def create_date_entry(parent, width=12):
    """Tao o chon ngay dinh dang dd/mm/yyyy. Doc: .get() ; gan: .set_date('dd/mm/yyyy')."""
    return DateEntry(parent, width=width, date_pattern=DATE_FMT,
                     background="darkblue", foreground="white", borderwidth=2)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Demo DateEntry")
    apply_style(root)
    cal = create_date_entry(root)
    cal.pack(padx=10, pady=10)
    tk.Button(root, text="Lấy ngày",
              command=lambda: messagebox.showinfo("Thông báo", f"Ngày được chọn: {cal.get()}")
              ).pack(pady=5)
    root.mainloop()