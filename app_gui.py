import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import config
from datetime import datetime

from views.theme import apply_style
from views.login_sign_in_screen import LoginFrame
from views.main_dashboard import MainDashboard
from views.filter_search import filter_sessions

from controllers.data_manager import DataManager
from controllers.workout_manager import WorkoutManager
from controllers.crawler import update_exercises

from models.account import Account, Admin
from models.sports import Exercise

class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.APP_TITLE)
        apply_style(self.root)
        self._setup_window_size()
        
        self.current_user = None
        self.dashboard = None 
        
        try:
            self.exercises = [Exercise.from_dict(d) for d in DataManager(config.EXERCISES_FILE).load_data()]
            self.wm = WorkoutManager(DataManager(config.ACTIVITIES_FILE), self.exercises)
            self.accounts_db = DataManager(config.ACCOUNTS_FILE)
            self._check_default_admin()
        except Exception as e:
            messagebox.showerror("Lỗi Hệ Thống", f"Không thể khởi tạo dữ liệu: {e}")
            self.root.destroy()
            return

        self.show_login()

    def _setup_window_size(self):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = min(int(sw * 0.85), 1250), min(int(sh * 0.85), 850)
        x, y = (sw // 2) - (w // 2), (sh // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(1000, 650)

    def _check_default_admin(self):
        if not self.accounts_db.load_data():
            try:
                admin_acc = Admin("admin", Account.hash_password("123"), "Quản trị viên", "admin@gmail.com")
                self.accounts_db.create(admin_acc.to_dict())
            except Exception as e:
                print("Lỗi tạo admin:", e)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    
    def show_login(self):
        self.clear_screen()
        self.root.geometry(config.WINDOW_LOGIN_SIZE)
        LoginFrame(self.root, on_success=self.on_login_success).pack(fill="both", expand=True)

    def on_login_success(self, account_obj):
        self.current_user = account_obj
        self.show_main_dashboard()

    def show_main_dashboard(self):
        self.clear_screen()
        self.root.geometry(config.WINDOW_SIZE)
        
        # Khởi tạo View (Giao diện) và truyền chính Controller (self) vào
        self.dashboard = MainDashboard(self.root, self)
        self.dashboard.pack(fill="both", expand=True)
        self.refresh_table() # Cập nhật dữ liệu lần đầu

    # ================= XỬ LÝ LOGIC (BACKEND) =================
    def refresh_table(self):
        if not self.dashboard: return
        
        try:
            data = []
            for a in self.wm.activities_list:
                if self.current_user.Access_Level() != "admin" and a.user_id != self.current_user._username:
                    continue
                data.append({
                    "id": a.activity_id, "date": a.date, "sport": a.activity_type,
                    "exercise": a.exercise.name if a.exercise else "",
                    "minutes": a.duration, "distance": a.distance,
                    "intensity": a.intensity, "cal": a.calories 
                })

            # Lấy tiêu chí lọc từ View
            filtered_data = filter_sessions(data, **self.dashboard.filter_bar.criteria())
            
            # Đẩy dữ liệu sang View để vẽ
            self.dashboard.table.load(filtered_data)
            self._update_charts(filtered_data)
            
            if hasattr(self.dashboard, 'plan_tab'):
                self.dashboard.plan_tab.refresh()
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hiển thị danh sách: {e}")

    def _update_charts(self, rows):
        if not self.dashboard: return
        
        total_cal = sum(item["cal"] for item in rows)
        target_cal = getattr(self.current_user, '_UserCalories_Aim', 1000)
        percent = (total_cal / target_cal) * 100 if target_cal > 0 else 0
        self.dashboard.progress_widget.set(percent, "Calo đã đốt")

        daily_min = {}
        for item in rows:
            date_str = item["date"][:5]
            daily_min[date_str] = daily_min.get(date_str, 0) + item["minutes"]
        if not daily_min:
            daily_min[datetime.now().strftime("%d/%m")] = 0
            
        self.dashboard.chart_widget.set_data(list(daily_min.keys()), list(daily_min.values()), "Thời gian tập (Phút)")

    def save_calorie_goal(self):
        try:
            new_aim = int(self.dashboard.var_calo_goal.get())
            if new_aim <= 0: raise ValueError
        except ValueError:
            return messagebox.showwarning("Lỗi", "Mục tiêu calo phải là số nguyên dương!")

        if hasattr(self.current_user, '_UserCalories_Aim'):
            self.current_user._UserCalories_Aim = new_aim
            raw_data = self.accounts_db.load_data()
            for d in raw_data:
                if d.get("username") == self.current_user._username:
                    d["calories_aim"] = new_aim
                    self.accounts_db.save_data(raw_data)
                    messagebox.showinfo("Thành công", f"Đã đổi mục tiêu thành {new_aim} kcal!")
                    break
        else:
            messagebox.showerror("Lỗi", "Tài khoản Admin không có mục tiêu calo.")
        self.refresh_table()

    def save_activity(self, act_obj):
        try:
            if self.dashboard.form.editing_id:
                success = self.wm.update_activity(self.dashboard.form.editing_id, act_obj)
                msg = "Đã cập nhật buổi tập!"
            else:
                success = self.wm.add_activity(act_obj)
                msg = "Đã thêm buổi tập mới!"
    
            if success:
                messagebox.showinfo("Thành công", msg)
                self.refresh_table()
                return True
            else:
                messagebox.showerror("Lỗi", "Trùng mã ID hoặc lỗi lưu file.")
                return False
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
        return False

    def load_to_form(self):
        act_id = self.dashboard.table.selected_id()
        if not act_id: return
        act = next((a for a in self.wm.activities_list if a.activity_id == act_id), None)
        if act: self.dashboard.form.fill(act)

    def delete_activity(self):
        act_id = self.dashboard.table.selected_id()
        if not act_id: return messagebox.showwarning("Chú ý", "Vui lòng chọn một buổi tập để xóa.")
            
        if messagebox.askyesno("Xác nhận", f"Xóa buổi tập {act_id}?"):
            if self.wm.delete_activity(act_id):
                messagebox.showinfo("Thành công", "Đã xóa buổi tập.")
                self.refresh_table()
                self.dashboard.form.clear()

    def handle_logout(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn đăng xuất?"):
            self.current_user = None
            self.show_login()

    def export_journal(self):
        acts = [a for a in self.wm.activities_list if self.current_user.Access_Level() == "admin" or a.user_id == self.current_user._username]
        if not acts: return messagebox.showwarning("Chú ý", "Không có dữ liệu để xuất!")

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], initialfile=f"nhat_ky_{self.current_user._username}.txt")
        if not file_path: return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("="*65 + "\n" + f"{'NHẬT KÝ LUYỆN TẬP THỂ THAO':^65}\n" + f"{'Người dùng: ' + self.current_user._fullname:^65}\n" + "="*65 + "\n\n")
                f.write(f"{'Ngày':<12} | {'Môn':<10} | {'Bài tập':<18} | {'Phút':<5} | {'Calo':<6}\n" + "-"*65 + "\n")
                total_cal = total_min = 0
                for a in acts:
                    ex_name = a.exercise.name if a.exercise else "N/A"
                    f.write(f"{a.date:<12} | {a.activity_type:<10} | {ex_name[:16]:<18} | {a.duration:<5} | {a.calories:<6}\n")
                    total_cal += a.calories
                    total_min += a.duration
                f.write("-"*65 + "\n" + f"{'TỔNG CỘNG:':<45} | {total_min:<5} | {total_cal:<6}\n" + "="*65 + "\n")
            messagebox.showinfo("Thành công", f"Đã xuất nhật ký ra file:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể ghi file: {e}")

    def run_crawler(self):
        def task():
            try:
                dm = DataManager(config.EXERCISES_FILE)
                added = update_exercises(dm, max_per_sport=config.CRAWLER_MAX_PER_SPORT)
                self.exercises = [Exercise.from_dict(d) for d in dm.load_data()]
                self.wm.exercises = {e.exercise_id: e for e in self.exercises}
                
                def show_success():
                    messagebox.showinfo("Crawl thành công", f"Đã thêm {len(added)} bài tập mới!")
                    self.dashboard.form.exercises = self.exercises # Cập nhật lại form
                    self.dashboard.form.clear()
                self.root.after(0, show_success)
            except Exception as e:
                self.root.after(0, lambda err=str(e): messagebox.showerror("Lỗi Crawl", err))
                
        messagebox.showinfo("Thông báo", "Bắt đầu crawl dữ liệu, vui lòng đợi...")
        threading.Thread(target=task, daemon=True).start()

