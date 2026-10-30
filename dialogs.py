import tkinter as tk
from tkinter import messagebox
from theme import apply_style

def confirm(title, message, warning=False):
    """True neu nguoi dung chon Yes."""
    return messagebox.askquestion(title, message, icon="warning" if warning else "question") == "yes"


def confirm_delete(description):
    return confirm("Xác nhận xóa", f"Xóa {description}?", warning=True)

def confirm_exit(root):
    """Hoi truoc khi thoat; dong cua so neu dong y."""
    if confirm("Thoát", "Bạn có chắc muốn thoát?"):
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Demo hộp thoại")
    apply_style(root)
    root.protocol("WM_DELETE_WINDOW", lambda: confirm_exit(root))
    tk.Button(root, text="Xóa thử", command=lambda: print("Xóa?", confirm_delete("buổi tập #1"))).pack(padx=20, pady=10)
    tk.Button(root, text="Thoát", command=lambda: confirm_exit(root)).pack(pady=10)
    root.mainloop()