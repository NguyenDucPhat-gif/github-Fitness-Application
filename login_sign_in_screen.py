import tkinter as tk
from tkinter import messagebox
from DataManager import DataManager
from Account import Account, User
from theme import BG, ACCENT, FONT, FONT_BOLD, FONT_TITLE, apply_style
 
 
class LoginFrame(tk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, bg=BG)
        self.on_success = on_success
        
        # Khởi tạo kết nối tới file accounts.json
        self.db = DataManager("accounts.json")
 
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
 
    # --- SỬA LOGIC BÊN TRONG HÀM LOGIN ---
    def login(self):
        u, p = self._read()
        if not u or not p:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên và mật khẩu.")
            return

        # Đọc dữ liệu từ file accounts.json
        raw_data = self.db.load_data()
        for d in raw_data:
            try:
                acc = Account.from_dict(d)
                # Kiểm tra đăng nhập
                if acc._username == u and acc.Sign_In(p):
                    self.var_pw.set("")
                    # Trả về nguyên object Account để main.py biết quyền (Admin/User)
                    self.on_success(acc) 
                    return
            except Exception:
                pass # Bỏ qua các dòng dữ liệu lỗi trong file JSON
                
        messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu.")
 
    # --- SỬA LOGIC BÊN TRONG HÀM REGISTER ---
    def register(self):
       u = self.var_user.get().strip()
       p = self.var_pw.get()
       email = self.var_email.get().strip()

       if not u or len(p) < 4 or not email:
           messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ Tên, Mật khẩu và Email.")
           return

       raw_data = self.db.load_data()
       # Kiểm tra trùng username
       if any(d.get("username", d.get("_username")) == u for d in raw_data):
           messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại.")
           return

       try:
           # Khởi tạo User (Hàm setter trong Account.py sẽ tự động dùng Regex bắt lỗi nếu email sai)
           new_user = User(u, p, u, email) 
           if self.db.create(new_user.to_dict()):
               messagebox.showinfo("Thành công", "Đăng ký xong, hãy đăng nhập.")
       except ValueError as e:
           # Nếu email sai định dạng, class Account sẽ ném lỗi ValueError và hiện lên đây
           messagebox.showerror("Lỗi dữ liệu", str(e))
 
 
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Demo đăng nhập")
    root.geometry("500x350")
    apply_style(root)
    
    # Hàm nhận kết quả khi đăng nhập thành công
    def test_login(account):
        messagebox.showinfo("OK", f"Xin chào {account._fullname}\nQuyền: {account.Access_Level()}")
        
    LoginFrame(root, on_success=test_login).pack(fill="both", expand=True)
    root.mainloop()