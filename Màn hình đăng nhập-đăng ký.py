import tkinter as tk
from tkinter import messagebox
 
import data
from theme import BG, ACCENT, FONT, FONT_BOLD, FONT_TITLE, apply_style
 
 
class LoginFrame(tk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, bg=BG)
        self.on_success = on_success
 
        # Dat khung o giua, luon giua khi cua so co gian
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        box = tk.Frame(self, bg="white", padx=30, pady=25,
                       highlightbackground="#d0d6e2", highlightthickness=1)
        box.grid(row=0, column=0)
 
        tk.Label(box, text="QUẢN LÝ BUỔI TẬP", font=FONT_TITLE, fg=ACCENT,
                 bg="white").grid(row=0, column=0, columnspan=2, pady=(0, 15))
 
        tk.Label(box, text="Tên đăng nhập", font=FONT, bg="white").grid(
            row=1, column=0, sticky="w", pady=5)
        self.var_user = tk.StringVar()
        tk.Entry(box, textvariable=self.var_user, font=FONT, width=24).grid(
            row=1, column=1, pady=5, padx=(10, 0))
 
        tk.Label(box, text="Mật khẩu", font=FONT, bg="white").grid(
            row=2, column=0, sticky="w", pady=5)
        self.var_pw = tk.StringVar()
        pw = tk.Entry(box, textvariable=self.var_pw, font=FONT, width=24, show="*")
        pw.grid(row=2, column=1, pady=5, padx=(10, 0))
        pw.bind("<Return>", lambda e: self.login())
 
        btns = tk.Frame(box, bg="white")
        btns.grid(row=3, column=0, columnspan=2, pady=(15, 0))
        tk.Button(btns, text="Đăng nhập", font=FONT_BOLD, bg=ACCENT, fg="white",
                  width=12, command=self.login).grid(row=0, column=0, padx=5)
        tk.Button(btns, text="Đăng ký", font=FONT, width=12,
                  command=self.register).grid(row=0, column=1, padx=5)
 
    def _read(self):
        return self.var_user.get().strip(), self.var_pw.get()
 
    def login(self):
        u, p = self._read()
        if u and data.users.get(u) == p:
            self.var_pw.set("")
            self.on_success(u)
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu.")
 
    def register(self):
        u, p = self._read()
        if not u or len(p) < 4:
            messagebox.showwarning("Thiếu thông tin",
                                   "Tên không được trống, mật khẩu >= 4 ký tự.")
        elif u in data.users:
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại.")
        else:
            data.users[u] = p
            messagebox.showinfo("Thành công", "Đăng ký xong, hãy đăng nhập.")
 
 
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Demo đăng nhập")
    root.geometry("500x350")
    apply_style(root)
    LoginFrame(root, on_success=lambda u: messagebox.showinfo("OK", f"Xin chào {u}")
               ).pack(fill="both", expand=True)
    root.mainloop()
 