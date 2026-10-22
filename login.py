"""Part 25 - Man hinh dang nhap / dang ky / doi mat khau (Entry, Button, Label, show='*').
Dang ky tao tai khoan vai tro 'Nguoi dung'; quan tri vien do he thong tao san."""
import tkinter as tk
from tkinter import ttk, messagebox

import data
from theme import BG, ACCENT, BORDER, FONT, FONT_BOLD, FONT_TITLE, apply_style


class ChangePasswordDialog(tk.Toplevel):
    """Doi mat khau. username=None -> hien o nhap ten dang nhap (dung ngay tren
    man hinh dang nhap); co username -> dung cho nguoi dang dang nhap."""
    def __init__(self, master, username=None, prefill=""):
        super().__init__(master, bg=BG)
        self.fixed_user = username
        self.title("Đổi mật khẩu")
        self.resizable(False, False)
        self.transient(master)
        self.columnconfigure(1, weight=1)

        self.var_user = tk.StringVar(value=prefill)
        self.vars = []
        labels = ["Mật khẩu hiện tại", "Mật khẩu mới", "Nhập lại mật khẩu mới"]
        row = 0
        first = None
        if username is None:
            ttk.Label(self, text="Tên đăng nhập", background=BG).grid(
                row=row, column=0, sticky="w", padx=10, pady=6)
            first = ttk.Entry(self, textvariable=self.var_user, width=26)
            first.grid(row=row, column=1, padx=10, pady=6)
            row += 1
        for label in labels:
            ttk.Label(self, text=label, background=BG).grid(
                row=row, column=0, sticky="w", padx=10, pady=6)
            var = tk.StringVar()
            entry = ttk.Entry(self, textvariable=var, show="*", width=26)
            entry.grid(row=row, column=1, padx=10, pady=6)
            entry.bind("<Return>", lambda e: self.submit())
            first = first or entry
            self.vars.append(var)
            row += 1
        bt = ttk.Frame(self)
        bt.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(bt, text="Lưu", command=self.submit).grid(row=0, column=0, padx=4)
        ttk.Button(bt, text="Hủy", command=self.destroy).grid(row=0, column=1, padx=4)
        self.grab_set()
        first.focus_set()

    def submit(self):
        user = self.fixed_user if self.fixed_user is not None else self.var_user.get().strip()
        old, new, again = (v.get() for v in self.vars)
        if not user:
            messagebox.showwarning("Thiếu thông tin", "Hãy nhập tên đăng nhập.", parent=self)
            return
        if new != again:
            messagebox.showwarning("Không khớp", "Hai lần nhập mật khẩu mới chưa giống nhau.", parent=self)
            return
        ok, msg = data.change_password(user, old, new)
        (messagebox.showinfo if ok else messagebox.showwarning)("Đổi mật khẩu", msg, parent=self)
        if ok:
            if data.last_error:
                messagebox.showwarning("Lưu dữ liệu", data.last_error, parent=self)
            self.destroy()


class LoginFrame(tk.Frame):
    def __init__(self, master, on_success):
        """on_success(username, role) duoc goi khi dang nhap dung."""
        super().__init__(master, bg=BG)
        self.on_success = on_success

        # Khung o giua, luon giua khi cua so co gian
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        box = tk.Frame(self, bg="white", padx=30, pady=25,
                       highlightbackground=BORDER, highlightthickness=1)
        box.grid(row=0, column=0)

        tk.Label(box, text="THEO DÕI LUYỆN TẬP", font=FONT_TITLE, fg=ACCENT,
                 bg="white").grid(row=0, column=0, columnspan=2, pady=(0, 15))

        tk.Label(box, text="Tên đăng nhập", font=FONT, bg="white").grid(
            row=1, column=0, sticky="w", pady=5)
        self.var_user = tk.StringVar()
        self.entry_user = tk.Entry(box, textvariable=self.var_user, font=FONT, width=24)
        self.entry_user.grid(row=1, column=1, pady=5, padx=(10, 0))

        tk.Label(box, text="Mật khẩu", font=FONT, bg="white").grid(
            row=2, column=0, sticky="w", pady=5)
        self.var_pw = tk.StringVar()
        pw = tk.Entry(box, textvariable=self.var_pw, font=FONT, width=24, show="*")
        pw.grid(row=2, column=1, pady=5, padx=(10, 0))
        pw.bind("<Return>", lambda e: self.login())
        self.entry_user.bind("<Return>", lambda e: pw.focus_set())

        btns = tk.Frame(box, bg="white")
        btns.grid(row=3, column=0, columnspan=2, pady=(15, 0))
        tk.Button(btns, text="Đăng nhập", font=FONT_BOLD, bg=ACCENT, fg="white",
                  width=12, command=self.login).grid(row=0, column=0, padx=5)
        tk.Button(btns, text="Đăng ký", font=FONT, width=12,
                  command=self.register).grid(row=0, column=1, padx=5)
        # Quen/muon doi mat khau ngay tai man hinh dang nhap
        tk.Button(box, text="Đổi mật khẩu", font=FONT, fg=ACCENT, bg="white",
                  relief="flat", cursor="hand2", activeforeground=ACCENT,
                  command=self.change_password).grid(row=4, column=0, columnspan=2, pady=(10, 0))

    def _read(self):
        return self.var_user.get().strip(), self.var_pw.get()

    def reset(self):
        self.var_user.set("")
        self.var_pw.set("")
        self.entry_user.focus_set()

    def login(self):
        u, p = self._read()
        role = data.authenticate(u, p) if u else None
        if role is None:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu.")
            return
        self.reset()
        self.on_success(u, role)

    def change_password(self):
        """Mo hop thoai doi mat khau (can ten dang nhap + mat khau cu)."""
        ChangePasswordDialog(self.winfo_toplevel(), prefill=self.var_user.get().strip())
        self.var_pw.set("")

    def register(self):
        ok, msg = data.register(*self._read())
        if ok:
            self.var_pw.set("")
            messagebox.showinfo("Thành công", msg)
        else:
            messagebox.showwarning("Không đăng ký được", msg)
        if data.last_error:
            messagebox.showwarning("Lưu dữ liệu", data.last_error)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Demo đăng nhập")
    root.geometry("500x350")
    apply_style(root)
    data.load()
    LoginFrame(root, on_success=lambda u, r: messagebox.showinfo("OK", f"Xin chào {u} ({r})")
               ).pack(fill="both", expand=True)
    root.mainloop()