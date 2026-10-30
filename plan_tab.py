"""Tab 'Ke hoach & Tien do' - Đã đồng bộ với WorkoutManager (activities.json)"""
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox

import config
from custom_widgets import BarChart, CircularProgress
from date_entry import create_date_entry
from dialogs import confirm_delete
from theme import ROW_DONE, ROW_LATE
from data_manager import DataManager

PLAN_COLS = [("id", "ID", 40), ("name", "Tên kế hoạch", 170), ("sport", "Môn", 80),
             ("target", "Mục tiêu (phút)", 100), ("done", "Đã tập (phút)", 95),
             ("pct", "Hoàn thành", 80), ("start", "Bắt đầu", 85), ("end", "Kết thúc", 85),
             ("owner", "Người tập", 85)]
ALL_COLS = [c[0] for c in PLAN_COLS]
USER_COLS = ALL_COLS[:-1]


class PlanTab(ttk.Frame):
    def __init__(self, master, wm):
        super().__init__(master)
        self.wm = wm 
        self.user, self.role = "", config.ROLE_USER
        self.db_plans = DataManager("plans.json") 
        
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self._build_form()
        self._build_table()
        self._build_charts()

    # ---------- Form tao ke hoach ----------
    def _build_form(self):
        f = ttk.LabelFrame(self, text="Tạo kế hoạch luyện tập")
        f.grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=6)
        for c in (1, 3):
            f.columnconfigure(c, weight=1)
        pad = {"padx": 6, "pady": 4}

        ttk.Label(f, text="Tên kế hoạch").grid(row=0, column=0, sticky="w", **pad)
        self.var_name = tk.StringVar()
        ttk.Entry(f, textvariable=self.var_name).grid(row=0, column=1, sticky="ew", **pad)

        ttk.Label(f, text="Môn").grid(row=0, column=2, sticky="w", **pad)
        self.cb_sport = ttk.Combobox(f, state="readonly",
                                     values=["Tất cả"] + list(config.SPORT_VI.values()))
        self.cb_sport.current(0)
        self.cb_sport.grid(row=0, column=3, sticky="ew", **pad)

        ttk.Label(f, text="Mục tiêu (phút)").grid(row=1, column=0, sticky="w", **pad)
        self.var_target = tk.StringVar()
        ttk.Entry(f, textvariable=self.var_target).grid(row=1, column=1, sticky="ew", **pad)

        dates = ttk.Frame(f)
        dates.grid(row=1, column=2, columnspan=2, sticky="w", **pad)
        ttk.Label(dates, text="Từ").grid(row=0, column=0)
        self.start = create_date_entry(dates, width=11)
        self.start.grid(row=0, column=1, padx=(4, 10))
        ttk.Label(dates, text="Đến").grid(row=0, column=2)
        self.end = create_date_entry(dates, width=11)
        self.end.grid(row=0, column=3, padx=4)

        bt = ttk.Frame(f)
        bt.grid(row=2, column=0, columnspan=4, sticky="e", padx=6, pady=6)
        ttk.Button(bt, text="Thêm kế hoạch", command=self.add_plan).grid(row=0, column=0, padx=3)
        ttk.Button(bt, text="Xóa kế hoạch chọn", command=self.delete_plan).grid(row=0, column=1, padx=3)

    # ---------- Bang ke hoach ----------
    def _build_table(self):
        wrap = ttk.LabelFrame(self, text="Kế hoạch và mức hoàn thành")
        wrap.grid(row=1, column=0, sticky="nsew", padx=(6, 3), pady=(0, 6))
        wrap.columnconfigure(0, weight=1)
        wrap.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(wrap, columns=ALL_COLS, displaycolumns=USER_COLS,
                                 show="headings", selectmode="browse")
        for key, title, w in PLAN_COLS:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=w, minwidth=40,
                             anchor="w" if key in ("name", "sport", "owner") else "center")
        self.tree.tag_configure("done", background=ROW_DONE)
        self.tree.tag_configure("late", background=ROW_LATE)
        ys = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ys.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        ys.grid(row=0, column=1, sticky="ns", padx=(0, 6), pady=6)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.update_widgets())

    # ---------- Vong tron + bieu do ----------
    def _build_charts(self):
        box = ttk.LabelFrame(self, text="Mức hoàn thành")
        box.grid(row=1, column=1, sticky="nsew", padx=(3, 6), pady=(0, 6))
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)
        self.circle = CircularProgress(box, size=150)
        self.circle.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        cbox = ttk.LabelFrame(self, text="Biểu đồ tiến độ")
        cbox.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=6, pady=(0, 6))
        cbox.columnconfigure(0, weight=1)
        cbox.rowconfigure(0, weight=1)
        self.chart = BarChart(cbox, height=170)
        self.chart.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

    # ---------- Logic Tính Toán Từ WorkoutManager ----------
    def _get_plans(self):
        """Lấy danh sách kế hoạch từ plans.json"""
        plans = self.db_plans.load_data()
        if self.role == config.ROLE_ADMIN:
            return plans
        return [p for p in plans if p["owner"] == self.user]

    def _calc_progress(self, plan):
        """Tính số phút đã tập và % hoàn thành từ wm.activities_list"""
        start = datetime.strptime(plan["start"], "%d/%m/%Y")
        end = datetime.strptime(plan["end"], "%d/%m/%Y")
        done = 0
        
        for a in self.wm.activities_list:
            if a.user_id != plan["owner"]: continue
            # Kiểm tra môn (Nếu plan chọn Tất cả thì bỏ qua)
            if plan["sport"] != "Tất cả":
                sport_en = config.SPORT_EN.get(plan["sport"], plan["sport"])
                if a.activity_type != sport_en: continue
                
            try:
                act_date = datetime.strptime(a.date, "%d/%m/%Y")
            except ValueError:
                continue
                
            if start <= act_date <= end:
                done += a.duration
                
        target = plan["target_minutes"]
        pct = min(100.0, (done / target) * 100) if target > 0 else 0.0
        return done, pct

    def _get_sessions_for_chart(self):
        """Lấy dữ liệu vẽ biểu đồ 7 ngày gần nhất"""
        days = config.CHART_DAYS
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        buckets = {(today - timedelta(days=i)).strftime("%d/%m"): 0 for i in range(days - 1, -1, -1)}
        
        for a in self.wm.activities_list:
            if self.role != config.ROLE_ADMIN and a.user_id != self.user:
                continue
            date_str = a.date[:5] 
            if date_str in buckets:
                buckets[date_str] += a.duration
                
        return list(buckets.keys()), list(buckets.values())

    # ---------- Cập nhật Giao diện ----------
    def set_user(self, username, role):
        self.user, self.role = username, role
        self.tree.configure(displaycolumns=ALL_COLS if role == config.ROLE_ADMIN else USER_COLS)
        self.refresh()

    def refresh(self):
        keep = self.tree.selection()
        self.tree.delete(*self.tree.get_children())
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for p in self._get_plans():
            done, pct = self._calc_progress(p)
            tag = ""
            if pct >= 100:
                tag = "done"
            else:
                try:
                    if datetime.strptime(p["end"], "%d/%m/%Y") < today:
                        tag = "late"
                except ValueError:
                    pass
            self.tree.insert("", "end", iid=str(p["id"]), tags=(tag,) if tag else (), values=(
                p["id"], p["name"], p["sport"], p["target_minutes"], done,
                f"{pct:.0f}%", p["start"], p["end"], p["owner"]))
                
        if keep and self.tree.exists(keep[0]):
            self.tree.selection_set(keep[0])
        self.update_widgets()

    def update_widgets(self):
        sel = self.tree.selection()
        plan = None
        if sel:
            plans = self._get_plans()
            plan = next((p for p in plans if str(p["id"]) == sel[0]), None)
            
        if plan:
            _, pct = self._calc_progress(plan)
            self.circle.set(pct, plan["name"])
        else:
            plans = self._get_plans()
            if plans:
                total_target = sum(p["target_minutes"] for p in plans)
                total_done = sum(self._calc_progress(p)[0] for p in plans)
                overall_pct = (total_done / total_target * 100) if total_target > 0 else 0
                self.circle.set(overall_pct, "Tổng quan")
            else:
                self.circle.set(0, "Chưa có kế hoạch")

        labels, values = self._get_sessions_for_chart()
        self.chart.set_data(labels, values, f"Số phút tập {config.CHART_DAYS} ngày gần nhất")

    # ---------- Thêm / Xóa Kế hoạch ----------
    def _read_plan(self):
        name = self.var_name.get().strip()
        if not name or len(name) > 60:
            messagebox.showwarning("Sai dữ liệu", "Tên kế hoạch bắt buộc, tối đa 60 ký tự.")
            return None
            
        try:
            target = int(self.var_target.get())
            if not 0 < target <= 100000:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Sai dữ liệu", "Mục tiêu phải là số nguyên dương (phút).")
            return None
            
        s, e = self.start.get(), self.end.get()
        
        try:
            date_s = datetime.strptime(s, "%d/%m/%Y")
            date_e = datetime.strptime(e, "%d/%m/%Y")
        except ValueError:
            messagebox.showwarning("Sai ngày", "Ngày phải đúng dạng dd/mm/yyyy và có thật.")
            return None
            
        if date_e < date_s:
            messagebox.showwarning("Sai ngày", "Ngày kết thúc phải sau hoặc bằng ngày bắt đầu.")
            return None
            
        return {"name": name, "sport": self.cb_sport.get(), "target_minutes": target,
                "start": s, "end": e, "owner": self.user}

    def add_plan(self):
        plan_info = self._read_plan()
        if not plan_info:
            return
            
        plans = self.db_plans.load_data()
        new_id = max([p["id"] for p in plans], default=0) + 1
        plan_info["id"] = new_id
        
        plans.append(plan_info)
        if self.db_plans.save_data(plans):
            self.var_name.set("")
            self.var_target.set("")
            self.refresh()
        else:
            messagebox.showerror("Lỗi", "Không thể lưu kế hoạch.")

    def delete_plan(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Chưa chọn", "Hãy chọn một kế hoạch trong bảng.")
            return
            
        plan_id = int(sel[0])
        plans = self.db_plans.load_data()
        p = next((x for x in plans if x["id"] == plan_id), None)
        
        if not p:
            return
            
        if self.role != config.ROLE_ADMIN and p["owner"] != self.user:
            messagebox.showerror("Không có quyền", "Bạn không được xóa kế hoạch này.")
            return
            
        if confirm_delete(f"kế hoạch \"{p['name']}\""):
            plans = [x for x in plans if x["id"] != plan_id]
            self.db_plans.save_data(plans)
            self.refresh()