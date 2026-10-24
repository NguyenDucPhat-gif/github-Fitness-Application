import tkinter as tk
from tkinter import messagebox
import threading
import config

from theme import apply_style, BG, ACCENT, FONT_BOLD
from login_sign_in_screen import LoginFrame, ChangePasswordDialog
from filter_search import FilterBar, filter_sessions
from treeview import SessionTable
from session_form import SessionForm

from data_manager import DataManager
from account import Account, Admin, User 
from sports import Exercise
from workout_manager import WorkoutManager
from crawler import update_exercises, CrawlError

from tkinter import filedialog
from datetime import datetime

class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title(config.APP_TITLE)
        self.root.geometry(config.WINDOW_SIZE)
        apply_style(self.root)
        
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
       """Xóa toàn bộ widget trên màn hình hiện tại để chuyển  màn hình"""
       for widget in self.root.winfo_children():
           widget.destroy()
    def check_default_admin(self):
        """Tự động tạo tài khoản admin nếu file JSON trống"""
        raw_data = self.accounts_db.load_data()
        if not raw_data:
            try:
                # Khởi tạo Admin. Nếu account.py đã sửa để băm pass, pass "123" sẽ tự động biến thành hash.
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

        if self.current_user.Access_Level() == "admin":
            tk.Button(header, text="Crawl dữ liệu (Admin)", command=self.run_crawler, 
                      bg="orange", fg="white", font=FONT_BOLD).pack(side="right", padx=10, pady=10)

        # --- 2. BODY ---
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        self.filter_bar = FilterBar(body, on_change=self.refresh_table)
        self.filter_bar.pack(fill="x", pady=(0, 10))

        self.table = SessionTable(body, on_double_click=self.load_to_form)
        self.table.pack(fill="both", expand=True)

        self.form = SessionForm(body, user_id=self.current_user._username, on_save=self.save_activity)
        self.form.pack(fill="x", pady=10)

        btn_action = tk.Frame(body)
        btn_action.pack(fill="x", pady=5)
        tk.Button(btn_action, text="Xóa buổi tập đang chọn", command=self.delete_activity, 
                  bg="red", fg="white").pack(side="left")

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
            
        except Exception as e:
            messagebox.showerror("Lỗi Hiển Thị", f"Không thể hiển thị danh sách: {e}")

    def save_activity(self, act_obj):
        """Xử lý khi Form bấm nút Lưu"""
        try:
            if self.form.editing_id:
                # Đang sửa
                if self.wm.update_activity(self.form.editing_id, act_obj):
                    messagebox.showinfo("Thành công", "Đã cập nhật buổi tập!")
                else:
                    messagebox.showerror("Lỗi", "Không thể cập nhật dữ liệu.")
            else:
                # Thêm mới
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
        # 1. Lấy dữ liệu (tương tự như hàm refresh_table nhưng lấy toàn bộ)
        activities_to_export = []
        for a in self.wm.activities_list:
            # Nếu là user thường thì chỉ xuất bài của mình, admin xuất hết
            if self.current_user.Access_Level() != "admin" and a.user_id != self.current_user._username:
                continue
            activities_to_export.append(a)

        if not activities_to_export:
            messagebox.showwarning("Chú ý", "Không có dữ liệu buổi tập nào để xuất!")
            return

        # 2. Mở hộp thoại chọn nơi lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Lưu nhật ký luyện tập",
            initialfile=f"nhat_ky_{self.current_user._username}.txt"
        )

        # Nếu người dùng bấm Cancel (Hủy) thì thoát
        if not file_path:
            return

        # 3. Ghi dữ liệu ra file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Ghi phần Header
                f.write("=" * 65 + "\n")
                f.write(f"{'NHẬT KÝ LUYỆN TẬP THỂ THAO':^65}\n")
                f.write(f"{'Người dùng: ' + self.current_user._fullname:^65}\n")
                f.write(f"{'Ngày xuất: ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'):^65}\n")
                f.write("=" * 65 + "\n\n")

                # Ghi tiêu đề bảng
                f.write(f"{'Ngày':<12} | {'Môn':<10} | {'Bài tập':<18} | {'Phút':<5} | {'Calo':<6}\n")
                f.write("-" * 65 + "\n")

                # Ghi từng dòng dữ liệu
                total_cal = 0
                total_min = 0
                for a in activities_to_export:
                    ex_name = a.exercise.name if a.exercise else "N/A"
                    # Cắt chuỗi nếu tên bài tập quá dài để bảng không bị lệch
                    if len(ex_name) > 16: ex_name = ex_name[:15] + "."
                    
                    f.write(f"{a.date:<12} | {a.activity_type:<10} | {ex_name:<18} | {a.duration:<5} | {a.calories:<6}\n")
                    
                    total_cal += a.calories
                    total_min += a.duration

                # Ghi phần tổng kết
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

    def run_crawler(self):
        """Chạy crawler ngầm để không treo giao diện"""
        def task():
            try:
                dm = DataManager(config.EXERCISES_FILE)
                res = update_exercises(dm, max_per_sport=config.CRAWLER_MAX_PER_SPORT, max_pages=config.CRAWLER_MAX_PAGES) 
                
                self.exercises = [Exercise.froam_dict(d) for d in dm.load_data()]
                self.wm.exercises = {e.exercise_id: e for e in self.exercises}
                
                msg = f"Đã thêm {len(res['added'])} bài tập mới từ web!"
                
                # Tạo hàm con để hiển thị thông báo
                def show_success():
                    messagebox.showinfo("Crawl thành công", msg)
                    
                self.root.after(0, show_success)
                
            except CrawlError as e:
                # Tạo hàm con để hiển thị lỗi Crawl
                def show_crawl_error(err=e):
                    messagebox.showerror("Lỗi Crawl", str(err))
                    
                self.root.after(0, show_crawl_error)
                
            except Exception as e:
                # Tạo hàm con để hiển thị lỗi chung
                def show_general_error(err=e):
                    messagebox.showerror("Lỗi Không Xác Định", str(err))
                    
                self.root.after(0, show_general_error)
                
        messagebox.showinfo("Thông báo", "Bắt đầu crawl dữ liệu, vui lòng đợi trong giây lát...")
        threading.Thread(target=task, daemon=True).start()
if __name__ == "__main__":
    root = tk.Tk()
    app = FitnessApp(root)
    root.mainloop()