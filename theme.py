"""Quy uoc chung:
- Moi font/mau lay tu file nay, khong tu y viet o file khac.
- Trong MOT vung chua (Frame) chi dung pack() HOAC grid(), khong tron.
- Dung grid + columnconfigure/rowconfigure(weight=1) de cua so co gian.
"""
from tkinter import ttk

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")
BG = "#f4f6fa"
ACCENT = "#2f5fd0"
DATE_FMT = "dd/mm/yyyy"


def apply_style(root):
    """Goi 1 lan sau khi tao root."""
    root.configure(bg=BG)
    st = ttk.Style()
    st.configure("Treeview", font=FONT, rowheight=24)
    st.configure("Treeview.Heading", font=FONT_BOLD)
    for name in ("TLabel", "TButton", "TCheckbutton", "TRadiobutton"):
        st.configure(name, font=FONT)


if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    root.title("Demo theme")
    apply_style(root)
    tk.Label(root, text="Tieu de", font=FONT_TITLE, fg=ACCENT, bg=BG).pack(padx=20, pady=10)
    ttk.Button(root, text="Nut mau").pack(pady=10)
    root.mainloop()