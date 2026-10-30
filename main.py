import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading
import config
from datetime import datetime


from theme import apply_style, BG, ACCENT, FONT_BOLD
from login_sign_in_screen import LoginFrame, ChangePasswordDialog
from filter_search import FilterBar, filter_sessions
from treeview import SessionTable
from session_form import SessionForm
from bodymetric_dialog import BodyMetricDialog
from plan_tab import PlanTab  


from data_manager import DataManager
from account import Account, Admin, User 
from sports import Exercise
from workout_manager import WorkoutManager
from crawler import update_exercises, CrawlError
import data # Dùng cho tính năng nhắc lịch


from custom_widgets import CircularProgress, BarChart

class FitnessApp:
    def __init__(self, root):
       self.root = root
       self.root.title(config.APP_TITLE)
       apply_style(self.root)
       
       screen_width = self.root.winfo_screenwidth()
       screen_height = self.root.winfo_screenheight()
       
       w = int(screen_width * 0.85)
       h = int(screen_height * 0.85)
       
       w = min(w, 1250)
       h = min(h, 850)
       
       
       x = (screen_width // 2) - (w // 2)
       y = (screen_height // 2) - (h // 2)
       
       self.root.geometry(f"{w}x{h}+{x}+{y}")
       
       self.root.minsize(1000, 650) 
       
       self.current_user = None
       
       try:
           
            self.exercises = [Exercise.from_dict(d) for d in DataManager(config.EXERCISES_FILE).load_data()]
            self.wm = WorkoutManager(DataManager(config.ACTIVITIES_FILE), self.exercises)
            self.accounts_db = DataManager(config.ACCOUNTS_FILE)
            self.check_default_admin()
       except Exception as e:
           messagebox.showerror("Lỗi Hệ Thống", f"Không thể khởi tạo dữ liệu: {e}")
           self.root.destroy()
           return

       self.show_login()
    
    def clear_screen(self):
        """Xóa toàn bộ widget trên màn hình hiện tại để chuyển màn hình"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def check_default_admin(self):
        """Tự động tạo tài khoản admin nếu file JSON trống"""
        raw_data = self.accounts_db.load_data()
        if not raw_data:
            try:
                hashed_pw = Account.hash_password("123")
                admin_acc = Admin("admin", hashed_pw, "Quản trị viên", "admin@gmail.com")
                self.accounts_db.create(admin_acc.to_dict())
                print("Đã tạo tài khoản admin mặc định (admin/123)")
            except Exception as e:
                print("Lỗi tạo admin mặc định:", e)

    # ================= MÀN HÌNH ĐĂNG NHẬP =================
    def show_login(self):
        self.clear_screen()
        self.root.geometry(config.WINDOW_LOGIN_SIZE)
        login_frame = LoginFrame(self.root, on_success=self.on_login_success)
        login_frame.pack(fill="both", expand=True)

    def on_login_success(self, account_obj):
        self.current_user = account_obj
        
        # --- TÍNH NĂNG NHẮC LỊCH (REMINDER) ---
        if account_obj.Access_Level() == "user":
            try:
                due_plans = data.plans_due_soon(account_obj._username, days=3)
                if due_plans:
                    msg = "Bạn có kế hoạch sắp hết hạn chưa hoàn thành:\n\n"
                    for p in due_plans:
                        msg += f"- {p['name']} (Hạn chót: {p['end']})\n"
                    messagebox.showwarning("Nhắc nhở lịch tập", msg)
            except Exception:
                pass 

        self.show_main_dashboard()

    # ================= MÀN HÌNH CHÍNH =================
    def show_main_dashboard(self):
     self.clear_screen()
     self.root.geometry(config.WINDOW_SIZE)

    # --- 1. HEADER ---
     header = tk.Frame(self.root, bg=ACCENT, height=50)
     header.pack(fill="x")
    
     tk.Label(header, text=f"Xin chào, {self.current_user._fullname} ({self.current_user.Access_Level()})", 
             font=FONT_BOLD, bg=ACCENT, fg="white").pack(side="left", padx=20, pady=10)
    
     tk.Button(header, text="Đăng xuất", command=self.handle_logout, 
              bg="white", fg="red", font=FONT_BOLD).pack(side="right", padx=20, pady=10)
    
     tk.Button(header, text="Đổi mật khẩu", command=self.open_change_password, 
              bg="lightblue", fg="black").pack(side="right", padx=10, pady=10)
              
     tk.Button(header, text="Chỉ số cơ thể (BMI)", command=self.open_bodymetric, 
              bg="lightgreen", fg="black").pack(side="right", padx=10, pady=10)

    # Nút Crawl (Chỉ Admin)
     if self.current_user.Access_Level() == "admin":
        tk.Button(header, text="Crawl dữ liệu (Admin)", command=self.run_crawler, 
                  bg="orange", fg="white", font=FONT_BOLD).pack(side="right", padx=10, pady=10)

    # --- 2. TẠO THANH TAB (NOTEBOOK) ---
     notebook = ttk.Notebook(self.root)
     notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # ================= TAB 1: QUẢN LÝ BUỔI TẬP =================
     body = tk.Frame(notebook, bg=BG)
     notebook.add(body, text="📝 Quản lý buổi tập")

    # === 1.FORM VÀ NÚT BẤM  ===
   
     bottom_frame = tk.Frame(body, bg=BG)
     bottom_frame.pack(side="bottom", fill="x", pady=5)

    # Nút thao tác 
     btn_action = tk.Frame(bottom_frame, bg=BG)
     btn_action.pack(side="bottom", fill="x", pady=(5, 0))
     tk.Button(btn_action, text="Xóa buổi tập đang chọn", command=self.delete_activity, 
              bg="red", fg="white").pack(side="left")
     tk.Button(btn_action, text="Xuất nhật ký (TXT)", command=self.export_journal, 
              bg="green", fg="white", font=FONT_BOLD).pack(side="right")

     # Form nhập liệu 
     self.form = SessionForm(bottom_frame, user_id=self.current_user._username, on_save=self.save_activity)
     self.form.pack(side="bottom", fill="x", pady=(5, 0))

    # === 2. PHẦN THỐNG KÊ (BIỂU ĐỒ & VÒNG TRÒN) ===
     stats_frame = tk.Frame(body, bg="white", bd=1, relief="solid")
     stats_frame.pack(side="top", fill="x", pady=(0, 5), ipady=5)

     self.progress_widget = CircularProgress(stats_frame, size=100, bg="white")
     self.progress_widget.pack(side="left", padx=20)
    
     goal_frame = tk.Frame(stats_frame, bg="white")
     goal_frame.pack(side="left", padx=(0, 20))
    
     tk.Label(goal_frame, text="Mục tiêu Calo\n(kcal)", bg="white", font=("Segoe UI", 10, "bold")).pack()
    
     current_aim = getattr(self.current_user, '_UserCalories_Aim', 1000)
     self.var_calo_goal = tk.StringVar(value=str(current_aim))
    
     entry_goal = tk.Entry(goal_frame, textvariable=self.var_calo_goal, width=8, justify="center", font=("Segoe UI", 10))
     entry_goal.pack(pady=2)
    
     tk.Button(goal_frame, text="Lưu", command=self.save_calorie_goal, bg="#2e9d5b", fg="white", font=("Segoe UI", 8)).pack()

     self.chart_widget = BarChart(stats_frame, height=120, bg="white") # Giảm chiều cao để không chiếm chỗ
     self.chart_widget.pack(side="right", fill="x", expand=True, padx=10)

    # === 3. THANH LỌC & BẢNG  ===
     self.filter_bar = FilterBar(body, on_change=self.refresh_table)
     self.filter_bar.pack(side="top", fill="x", pady=(0, 5))
 
   
     self.table = SessionTable(body, on_double_click=self.load_to_form)
     self.table.pack(side="top", fill="both", expand=True)

    # ================= TAB 2: KẾ HOẠCH & TIẾN ĐỘ =================
     tab2 = tk.Frame(notebook, bg=BG)
     notebook.add(tab2, text="🎯 Kế hoạch & Tiến độ")
    
     self.plan_tab = PlanTab(tab2, self.wm)
     self.plan_tab.pack(fill="both", expand=True)
     self.plan_tab.set_user(self.current_user._username, self.current_user.Access_Level())

     self.refresh_table()

    # ================= XỬ LÝ DỮ LIỆU =================
    def refresh_table(self):
        try:
            data_for_filter = []
            for a in self.wm.activities_list:
                if self.current_user.Access_Level() != "admin" and a.user_id != self.current_user._username:
                    continue
                    
                data_for_filter.append({
                    "id": a.activity_id,
                    "date": a.date,
                    "sport": a.activity_type,
                    "exercise": a.exercise.name if a.exercise else "",
                    "minutes": a.duration,
                    "intensity": a.intensity,
                    "cal": a.calories 
                })

            criteria = self.filter_bar.criteria()
            filtered_data = filter_sessions(data_for_filter, **criteria)
            self.table.load(filtered_data)
            
           
            self.update_charts(filtered_data)
            
  
            if hasattr(self, 'plan_tab'):
                self.plan_tab.refresh()
                
        except Exception as e:
            messagebox.showerror("Lỗi Hiển Thị", f"Không thể hiển thị danh sách: {e}")

    def update_charts(self, rows):
        """Cập nhật Vòng tròn tiến độ và Biểu đồ cột dựa trên dữ liệu đã lọc"""
     
        total_cal = sum(item["cal"] for item in rows)
        
   
        target_cal = getattr(self.current_user, '_UserCalories_Aim', 1000)
        
        percent = (total_cal / target_cal) * 100 if target_cal > 0 else 0
        self.progress_widget.set(percent, f"Calo đã đốt")

     
        daily_min = {}
        for item in rows:
            date_str = item["date"][:5]
            daily_min[date_str] = daily_min.get(date_str, 0) + item["minutes"]
            
        if not daily_min:
            daily_min[datetime.now().strftime("%d/%m")] = 0
            
        labels = list(daily_min.keys())
        values = list(daily_min.values())
        self.chart_widget.set_data(labels, values, "Thời gian tập (Phút)")
        
    def save_calorie_goal(self):
        """Lưu mục tiêu calo mới của người dùng"""
        try:
            new_aim = int(self.var_calo_goal.get())
            if new_aim <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Lỗi", "Mục tiêu calo phải là số nguyên dương!")
        
            self.var_calo_goal.set(str(getattr(self.current_user, '_UserCalories_Aim', 2000)))
            return

        
        if hasattr(self.current_user, '_UserCalories_Aim'):
            self.current_user._UserCalories_Aim = new_aim
            
         
            raw_data = self.accounts_db.load_data()
            updated = False
            for d in raw_data:
                u_name = d.get("username", d.get("_username"))
                if u_name == self.current_user._username:
                    d["calories_aim"] = new_aim
                    updated = True
                    break
            
            if updated:
                self.accounts_db.save_data(raw_data)
                messagebox.showinfo("Thành công", f"Đã đổi mục tiêu thành {new_aim} kcal!")
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy tài khoản trong file JSON.")
        else:
            messagebox.showerror("Lỗi", "Tài khoản Admin không có mục tiêu calo.")

        #
        self.refresh_table()

    def save_activity(self, act_obj):
        try:
            if self.form.editing_id:
                if self.wm.update_activity(self.form.editing_id, act_obj):
                    messagebox.showinfo("Thành công", "Đã cập nhật buổi tập!")
                else:
                    messagebox.showerror("Lỗi", "Không thể cập nhật dữ liệu.")
            else:
                if self.wm.add_activity(act_obj):
                    messagebox.showinfo("Thành công", "Đã thêm buổi tập mới!")
                else:
                    messagebox.showerror("Lỗi", "Trùng mã ID hoặc lỗi lưu file.")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Lỗi Lưu Dữ Liệu", f"Đã xảy ra lỗi khi lưu: {e}")

    def load_to_form(self):
        act_id = self.table.selected_id()
        if not act_id: return
        
        act = next((a for a in self.wm.activities_list if a.activity_id == act_id), None)
        if act:
            self.form.fill(act)
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu buổi tập này.")

    def delete_activity(self):
        """Xóa buổi tập đang chọn"""
        act_id = self.table.selected_id()
        if not act_id:
            messagebox.showwarning("Chú ý", "Vui lòng chọn một buổi tập trên bảng để xóa.")
            return
            
        try:
            if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa buổi tập {act_id}?"):
                if self.wm.delete_activity(act_id):
                    messagebox.showinfo("Thành công", "Đã xóa buổi tập.")
                    self.refresh_table()
                    self.form.clear()
                else:
                    messagebox.showerror("Lỗi", "Không thể xóa dữ liệu này.")
        except Exception as e:
            messagebox.showerror("Lỗi Xóa Dữ Liệu", f"Đã xảy ra lỗi: {e}")

    def export_journal(self):
        """Xuất danh sách buổi tập ra file văn bản (.txt)"""
        activities_to_export = []
        for a in self.wm.activities_list:
            if self.current_user.Access_Level() != "admin" and a.user_id != self.current_user._username:
                continue
            activities_to_export.append(a)

        if not activities_to_export:
            messagebox.showwarning("Chú ý", "Không có dữ liệu buổi tập nào để xuất!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Lưu nhật ký luyện tập",
            initialfile=f"nhat_ky_{self.current_user._username}.txt"
        )

        if not file_path: return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("=" * 65 + "\n")
                f.write(f"{'NHẬT KÝ LUYỆN TẬP THỂ THAO':^65}\n")
                f.write(f"{'Người dùng: ' + self.current_user._fullname:^65}\n")
                f.write(f"{'Ngày xuất: ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'):^65}\n")
                f.write("=" * 65 + "\n\n")

                f.write(f"{'Ngày':<12} | {'Môn':<10} | {'Bài tập':<18} | {'Phút':<5} | {'Calo':<6}\n")
                f.write("-" * 65 + "\n")

                total_cal = 0
                total_min = 0
                for a in activities_to_export:
                    ex_name = a.exercise.name if a.exercise else "N/A"
                    if len(ex_name) > 16: ex_name = ex_name[:15] + "."
                    
                    f.write(f"{a.date:<12} | {a.activity_type:<10} | {ex_name:<18} | {a.duration:<5} | {a.calories:<6}\n")
                    
                    total_cal += a.calories
                    total_min += a.duration

                f.write("-" * 65 + "\n")
                f.write(f"{'TỔNG CỘNG:':<45} | {total_min:<5} | {total_cal:<6}\n")
                f.write("=" * 65 + "\n")

            messagebox.showinfo("Thành công", f"Đã xuất nhật ký thành công ra file:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi Ghi File", f"Không thể ghi file nhật ký:\n{e}")

    # ================= CÁC CHỨC NĂNG KHÁC =================
    def handle_logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn đăng xuất?"):
            self.current_user = None
            self.show_login()

    def open_change_password(self):
        try:
            ChangePasswordDialog(self.root, username=self.current_user._username)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở form đổi mật khẩu: {e}")

    def open_bodymetric(self):
        """Mở cửa sổ nhập chỉ số cơ thể (BMI)"""
        try:
            BodyMetricDialog(self.root, username=self.current_user._username)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở form BMI: {e}")

    def run_crawler(self):
        """Chạy crawler ngầm để không treo giao diện (Đã bỏ lambda)"""
        def task():
            try:
                dm = DataManager(config.EXERCISES_FILE)
                res = update_exercises(dm, max_per_sport=config.CRAWLER_MAX_PER_SPORT)
                
                print("KẾT QUẢ CÀO:", res)
                
                self.exercises = [Exercise.from_dict(d) for d in dm.load_data()]
                self.wm.exercises = {e.exercise_id: e for e in self.exercises}
                self.form.exercises = self.exercises
                
                msg = f"Đã thêm {len(res['added'])} bài tập mới từ web!"
                
                def show_success():
                    messagebox.showinfo("Crawl thành công", msg)
                    self.form.clear() 
                    
                self.root.after(0, show_success)
                
            except CrawlError as e:
                print("LỖI CRAWL:", e)
                err_msg = str(e)
                
                def show_crawl_error():
                    messagebox.showerror("Lỗi Crawl", err_msg)
                    
                self.root.after(0, show_crawl_error)
                
            except Exception as e:
                print("LỖI KHÁC:", e)
                err_msg = str(e)
                
                def show_general_error():
                    messagebox.showerror("Lỗi Không Xác Định", err_msg)
                    
                self.root.after(0, show_general_error)
                
        messagebox.showinfo("Thông báo", "Bắt đầu crawl dữ liệu, vui lòng đợi trong giây lát...")
        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessApp(root)
    root.mainloop()