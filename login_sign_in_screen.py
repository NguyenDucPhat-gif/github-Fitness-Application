import tkinter as tk
from tkinter import ttk, messagebox
from data_manager import DataManager
from account import Account, User
from theme import BG, ACCENT, FONT, FONT_BOLD, FONT_TITLE, apply_style
 
class ChangePasswordDialog(tk.Toplevel):
    """Hộp thoại Đổi mật khẩu (Dùng chung cho cả ở màn hình Login và trong App)"""
    def __init__(self, master, username=None, prefill=""):
        super().__init__(master, bg=BG)
        self.fixed_user = username
        self.title("Đổi mật khẩu")
        self.resizable(False, False)
        self.transient(master)
        self.columnconfigure(1, weight=1)
        
        self.db = DataManager("accounts.json")

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

        # --- LOGIC ĐỔI MẬT KHẨU BẰNG JSON ---
        raw_data = self.db.load_data()
        updated = False
        for d in raw_data:
            # Lấy username (hỗ trợ cả 2 chuẩn key)
            u_name = d.get("username", d.get("_username"))
            if u_name == user:
                # Lấy pass cũ trong file
                p_old = d.get("password", d.get("_password"))
                if p_old != Account.hash_password(old):
                    messagebox.showerror("Lỗi", "Mật khẩu hiện tại không đúng.", parent=self)
                    return
                hashed_new_pw = Account.hash_password(new)
                
                if "password" in d: d["password"] = hashed_new_pw
                if "_password" in d: d["_password"] = hashed_new_pw
                updated = True
                break

        if updated and self.db.save_data(raw_data):
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!", parent=self)
            self.destroy()
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy tài khoản hoặc lỗi lưu file.", parent=self)


class LoginFrame(tk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, bg=BG)
        self.on_success = on_success
        
       
        self.db = DataManager("accounts.json")
 
       
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
        self.entry_user = tk.Entry(box, textvariable=self.var_user, font=FONT, width=24)
        self.entry_user.grid(row=1, column=1, pady=5, padx=(10, 0))
 
        tk.Label(box, text="Mật khẩu", font=FONT, bg="white").grid(
            row=2, column=0, sticky="w", pady=5)
        self.var_pw = tk.StringVar()
        pw = tk.Entry(box, textvariable=self.var_pw, font=FONT, width=24, show="*")
        pw.grid(row=2, column=1, pady=5, padx=(10, 0))
        pw.bind("<Return>", lambda e: self.login())
        self.entry_user.bind("<Return>", lambda e: pw.focus_set())
        
    
        tk.Label(box, text="Email", font=FONT, bg="white").grid(
            row=3, column=0, sticky="w", pady=5)
        self.var_email = tk.StringVar()
        tk.Entry(box, textvariable=self.var_email, font=FONT, width=24).grid(
            row=3, column=1, pady=5, padx=(10, 0))
 
        btns = tk.Frame(box, bg="white")
        btns.grid(row=4, column=0, columnspan=2, pady=(15, 0))
        tk.Button(btns, text="Đăng nhập", font=FONT_BOLD, bg=ACCENT, fg="white",
                  width=12, command=self.login).grid(row=0, column=0, padx=5)
        tk.Button(btns, text="Đăng ký", font=FONT, width=12,
                  command=self.register).grid(row=0, column=1, padx=5)
                  
   
        tk.Button(box, text="Đổi mật khẩu", font=FONT, fg=ACCENT, bg="white",
                  relief="flat", cursor="hand2", activeforeground=ACCENT,
                  command=self.change_password).grid(row=5, column=0, columnspan=2, pady=(10, 0))
 
    def _read(self):
        return self.var_user.get().strip(), self.var_pw.get()
    
    
    def login(self):
       u, p = self._read()
       if not u or not p:
           messagebox.showwarning("Lỗi", "Vui lòng nhập tên và mật khẩu.")
           return

       raw_data = self.db.load_data()
       for d in raw_data:
           try:
               acc = Account.from_dict(d)
               if acc._username == u:
                   if acc.Sign_In(p):
                       self.var_pw.set("")
                       self.on_success(acc) 
                       return
                   else:
                       messagebox.showerror("Lỗi", "Mật khẩu không đúng.")
                       return
           except Exception as e:
          
               print(f"Lỗi khi tải tài khoản: {e}") 
               continue
               
       messagebox.showerror("Lỗi", "Tên đăng nhập không tồn tại.")
       

    def change_password(self):
        """Gọi hộp thoại đổi mật khẩu ngay từ màn hình Login"""
        ChangePasswordDialog(self.winfo_toplevel(), prefill=self.var_user.get().strip())
        self.var_pw.set("")
 
    def register(self):
       u = self.var_user.get().strip()
       p = self.var_pw.get()
       email = self.var_email.get().strip()

       if not u or len(p) < 4 or not email:
           messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ Tên, Mật khẩu (>=4 ký tự) và Email.")
           return

       raw_data = self.db.load_data()

       if any(d.get("username", d.get("_username")) == u for d in raw_data):
           messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại.")
           return

       try:
          
           hashed_pw = Account.hash_password(p)
           new_user = User(u, hashed_pw, u, email) 
           if self.db.create(new_user.to_dict()):
               messagebox.showinfo("Thành công", "Đăng ký xong, hãy đăng nhập.")
               self.var_pw.set("")
               self.var_email.set("")
       except ValueError as e:
           messagebox.showerror("Lỗi dữ liệu", str(e))
 
 
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Demo đăng nhập")
    root.geometry("500x450")
    apply_style(root)
    
    def test_login(account):
        messagebox.showinfo("OK", f"Xin chào {account._fullname}\nQuyền: {account.Access_Level()}")
        
    LoginFrame(root, on_success=test_login).pack(fill="both", expand=True)
    root.mainloop()