"""Custom Widget (ke thua tk.Canvas):
- CircularProgress: vong tron hien thi % hoan thanh
- BarChart: bieu do cot ve bang Canvas (tu ve lai khi doi kich thuoc)
"""
import math
import tkinter as tk

from theme import (ACCENT, BORDER, COLOR_HIGH, COLOR_LOW, COLOR_MID, FONT, FONT_BOLD, FONT_SMALL)

def progress_color(pct):
    if pct < 40:
        return COLOR_LOW
    if pct < 80:
        return COLOR_MID
    return COLOR_HIGH

class CircularProgress(tk.Canvas):
    """Vong tron tien do. Dung: widget.set(75, "Ten ke hoach")."""
    def __init__(self, master, size=150, thickness=14, bg="white", **kw):
        super().__init__(master, width=size, height=size, bg=bg,
                         highlightthickness=0, **kw)
        self.thickness = thickness
        self.value = 0.0
        self.caption = ""
        self.bind("<Configure>", lambda e: self.redraw())
    def set(self, value, caption=""):
        try:
            v = float(value)
        except (TypeError, ValueError):
            v = 0.0
        self.value = max(0.0, min(100.0, v))
        self.caption = caption
        self.redraw()
    def redraw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        cap_h = 24 if self.caption else 0
        side = min(w, h - cap_h)
        if side < 40:
            return
        pad = self.thickness / 2 + 4
        x0 = (w - side) / 2 + pad
        y0 = pad
        x1 = x0 + side - 2 * pad
        y1 = y0 + side - 2 * pad
        self.create_oval(x0, y0, x1, y1, outline="#e3e7ef", width=self.thickness)
        if self.value > 0:
            extent = -min(359.9, 3.6 * self.value)      # 360 se khong ve duoc
            self.create_arc(x0, y0, x1, y1, start=90, extent=extent, style="arc",
                            outline=progress_color(self.value), width=self.thickness)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.create_text(cx, cy, text=f"{self.value:.0f}%",
                         font=("Segoe UI", max(10, int(side / 6)), "bold"),
                         fill=progress_color(self.value))
        if self.caption:
            self.create_text(w / 2, h - cap_h / 2, text=self.caption,
                             font=FONT, fill="#444", width=max(w - 8, 20))

def _nice_max(v):
    """Lam tron tran truc Y de chia duoc 4 khoang deu."""
    raw = max(v, 4) / 4.0                    # toi thieu 4 de nhan truc Y la so nguyen
    p = 10 ** math.floor(math.log10(raw))
    for m in (1, 1.5, 2, 2.5, 3, 4, 5, 8, 10):
        if m * p >= raw:
            return m * p * 4
    return 10 * p * 4

class BarChart(tk.Canvas):
    """Bieu do cot. Dung: chart.set_data(["01/10", ...], [30, 45, ...], "Tieu de")."""
    def __init__(self, master, bg="white", **kw):
        super().__init__(master, bg=bg, highlightthickness=1, highlightbackground=BORDER, **kw)
        self.labels, self.values, self.title = [], [], ""
        self.bind("<Configure>", lambda e: self.redraw())

    def set_data(self, labels, values, title=""):
        self.labels, self.values, self.title = list(labels), list(values), title
        self.redraw()

    def redraw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 140 or h < 110:
            return
        left, right, top, bottom = 48, 16, 32, 28
        if self.title:
            self.create_text(w / 2, 16, text=self.title, font=FONT_BOLD, fill=ACCENT)
        if not self.values or max(self.values) <= 0:
            self.create_text(w / 2, h / 2, text="Chưa có dữ liệu", font=FONT, fill="#888")
            return
        vmax = _nice_max(max(self.values))
        plot_w, plot_h = w - left - right, h - top - bottom
        for i in range(5):                                  # luoi ngang + nhan truc Y
            y = top + plot_h - plot_h * i / 4
            self.create_line(left, y, w - right, y, fill="#e6e9f0")
            self.create_text(left - 6, y, text=f"{vmax * i / 4:g}", anchor="e",
                             font=FONT_SMALL, fill="#666")
        slot = plot_w / len(self.values)
        bar_w = slot * 0.6
        for i, (lab, val) in enumerate(zip(self.labels, self.values)):
            cx = left + slot * (i + 0.5)
            bh = plot_h * val / vmax
            self.create_rectangle(cx - bar_w / 2, top + plot_h - bh,
                                  cx + bar_w / 2, top + plot_h, fill=ACCENT, outline="")
            if val > 0:
                self.create_text(cx, top + plot_h - bh - 8, text=f"{val:g}",
                                 font=FONT_SMALL, fill="#333")
            self.create_text(cx, top + plot_h + 12, text=lab, font=FONT_SMALL, fill="#444")


if __name__ == "__main__":
    from tkinter import ttk
    from theme import apply_style
    root = tk.Tk()
    root.title("Demo custom widgets")
    apply_style(root)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)
    cp = CircularProgress(root)
    cp.grid(row=0, column=0, padx=10, pady=10)
    cp.set(72, "Kế hoạch demo")
    chart = BarChart(root, height=200)
    chart.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    chart.set_data(["T2", "T3", "T4", "T5", "T6"], [30, 0, 45, 60, 20], "Phút tập")
    root.mainloop()