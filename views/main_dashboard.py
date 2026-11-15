import tkinter as tk
from tkinter import ttk
from datetime import datetime

from views.theme import BG, ACCENT, FONT_BOLD
from views.filter_search import FilterBar
from views.treeview import SessionTable
from views.session_form import SessionForm
from views.plan_tab import PlanTab  
from views.custom_widgets import CircularProgress, BarChart
from views.login_sign_in_screen import ChangePasswordDialog
from views.bodymetric_dialog import BodyMetricDialog

class MainDashboard(tk.Frame):
    """Giao diện Màn hình chính (View). Chỉ nhận dữ liệu và hiển thị."""
    def __init__(self, master, controller):
        super().__init__(master, bg=BG)
        self.controller = controller # Tham chiếu đến Backend (FitnessApp)
        self.user = controller.current_user
        self.wm = controller.wm
        
        self._build_header()
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._build_tab_session()
        self._build_tab_plan()

    def _build_header(self):
        header = tk.Frame(self, bg=ACCENT, height=50)
        header.pack(fill="x")
        
        tk.Label(header, text=f"Xin chào, {self.user._fullname} ({self.user.Access_Level()})", 
                 font=FONT_BOLD, bg=ACCENT, fg="white").pack(side="left", padx=20, pady=10)
        
        # Gọi các hàm xử lý từ Controller
        tk.Button(header, text="Đăng xuất", command=self.controller.handle_logout, bg="white", fg="red").pack(side="right", padx=20)
        tk.Button(header, text="Đổi mật khẩu", command=lambda: ChangePasswordDialog(self.winfo_toplevel(), self.user._username), bg="lightblue").pack(side="right", padx=10)
        tk.Button(header, text="Chỉ số cơ thể (BMI)", command=lambda: BodyMetricDialog(self.winfo_toplevel(), self.user._username), bg="lightgreen").pack(side="right", padx=10)

        if self.user.Access_Level() == "admin":
            tk.Button(header, text="Crawl dữ liệu", command=self.controller.run_crawler, bg="orange", fg="white").pack(side="right", padx=10)

    def _build_tab_session(self):
        body = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(body, text="📝 Quản lý buổi tập")

        # 1. Form và Nút bấm
        bottom_frame = tk.Frame(body, bg=BG)
        bottom_frame.pack(side="bottom", fill="x", pady=5)

        btn_action = tk.Frame(bottom_frame, bg=BG)
        btn_action.pack(side="bottom", fill="x", pady=(5, 0))
        tk.Button(btn_action, text="Xóa buổi tập đang chọn", command=self.controller.delete_activity, bg="red", fg="white").pack(side="left")
        tk.Button(btn_action, text="Xuất nhật ký (TXT)", command=self.controller.export_journal, bg="green", fg="white").pack(side="right")

        self.form = SessionForm(bottom_frame, user_id=self.user._username, on_save=self.controller.save_activity)
        self.form.pack(side="bottom", fill="x", pady=(5, 0))

        # 2. Thống kê
        stats_frame = tk.Frame(body, bg="white", bd=1, relief="solid")
        stats_frame.pack(side="top", fill="x", pady=(0, 5), ipady=5)

        self.progress_widget = CircularProgress(stats_frame, size=100, bg="white")
        self.progress_widget.pack(side="left", padx=20)
        
        goal_frame = tk.Frame(stats_frame, bg="white")
        goal_frame.pack(side="left", padx=(0, 20))
        tk.Label(goal_frame, text="Mục tiêu Calo\n(kcal)", bg="white").pack()
        
        self.var_calo_goal = tk.StringVar(value=str(getattr(self.user, '_UserCalories_Aim', 1000)))
        tk.Entry(goal_frame, textvariable=self.var_calo_goal, width=8, justify="center").pack(pady=2)
        tk.Button(goal_frame, text="Lưu", command=self.controller.save_calorie_goal, bg="#2e9d5b", fg="white").pack()

        self.chart_widget = BarChart(stats_frame, height=120, bg="white")
        self.chart_widget.pack(side="right", fill="x", expand=True, padx=10)

        # 3. Lọc và Bảng
        self.filter_bar = FilterBar(body, on_change=self.controller.refresh_table)
        self.filter_bar.pack(side="top", fill="x", pady=(0, 5))

        self.table = SessionTable(body, on_double_click=self.controller.load_to_form)
        self.table.pack(side="top", fill="both", expand=True)

    def _build_tab_plan(self):
        tab2 = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab2, text="🎯 Kế hoạch & Tiến độ")
        
        self.plan_tab = PlanTab(tab2, self.wm)
        self.plan_tab.pack(fill="both", expand=True)
        self.plan_tab.set_user(self.user._username, self.user.Access_Level())