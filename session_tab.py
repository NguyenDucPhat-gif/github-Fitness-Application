"""Tab 'Buoi tap': ghep form (form_buoi_tap) + bo loc (loc_timkiem) + bang (treeview).
Chi dung grid trong vung chua nay."""
import csv
from tkinter import ttk, messagebox, filedialog

import config
import data
from treeview import SessionTable
from session_form import SessionForm
from filter_search import FilterBar, filter_sessions
from dialogs import confirm_delete


class SessionTab(ttk.Frame):
    def __init__(self, master, on_data_changed):
        super().__init__(master)
        self.on_data_changed = on_data_changed
        self.user, self.role = "", config.ROLE_USER
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.form = SessionForm(self, on_save=self.save, on_edit=self.edit,
                                on_delete=self.delete)
        self.form.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        self.filter = FilterBar(self, on_change=self.refresh)
        self.filter.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 6))
        self.table = SessionTable(self, on_double_click=self.edit)
        self.table.grid(row=2, column=0, sticky="nsew", padx=6, pady=(0, 6))

    def set_user(self, username, role):
        self.user, self.role = username, role
        self.table.set_admin_mode(role == config.ROLE_ADMIN)
        self.form.clear()
        self.filter.reset()          
    def rows(self):
        return filter_sessions(data.sessions_for(self.user, self.role),
                               **self.filter.criteria())

    def refresh(self):
        self.table.load(self.rows())

    def _can_touch(self, s):
        return self.role == config.ROLE_ADMIN or s["owner"] == self.user

    def _after_change(self):
        if data.last_error:
            messagebox.showwarning("Lưu dữ liệu", data.last_error)
        self.refresh()
        self.on_data_changed()

    def save(self):
        record = self.form.read()
        if not record:
            return
        if self.form.editing_id is None:
            data.add_session(record, self.user)
        else:
            s = data.get_session(self.form.editing_id)
            if s is None or not self._can_touch(s):
                messagebox.showerror("Không có quyền", "Bạn không được sửa buổi tập này.")
                return
            data.update_session(s["id"], record)
        self.form.clear()
        self._after_change()

    def _selected(self):
        sid = self.table.selected_id()
        s = data.get_session(sid) if sid is not None else None
        if s is None:
            messagebox.showinfo("Chưa chọn", "Hãy chọn một dòng trong bảng.")
        return s

    def edit(self):
        s = self._selected()
        if s:
            self.form.fill(s)

    def delete(self):
        s = self._selected()
        if not s:
            return
        if not self._can_touch(s):
            messagebox.showerror("Không có quyền", "Bạn không được xóa buổi tập này.")
            return
        if confirm_delete(f"buổi tập #{s['id']} ({s['sport']} - {s['exercise']})"):
            data.delete_session(s["id"])
            self.form.clear()
            self._after_change()

    def export_csv(self):
        """Xuat nhat ky (danh sach dang hien thi) ra CSV."""
        rows = self.rows()
        if not rows:
            messagebox.showinfo("Xuất nhật ký", "Không có buổi tập nào để xuất.")
            return
        path = filedialog.asksaveasfilename(
            title="Xuất nhật ký tập luyện", defaultextension=".csv",
            initialfile="training_log.csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["ID", "Ngày", "Môn", "Bài tập", "Phút", "Cường độ", "Calo", "Người tập"])
                for s in rows:
                    w.writerow([s["id"], s["date"], s["sport"], s["exercise"],
                                s["minutes"], s["intensity"], s["cal"], s["owner"]])
        except OSError as exc:
            messagebox.showerror("Lỗi ghi file", f"Không ghi được file:\n{exc}")
        else:
            messagebox.showinfo("Xuất nhật ký", f"Đã xuất {len(rows)} buổi tập.")