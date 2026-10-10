import tkinter as tk
import tkinter.messagebox as mb

root = tk.Tk()
root.title("Hello Tkinter")

def button_click():
    mb.showinfo("Thông báo", "Bạn đã nhấn vào nút")

label = tk.Label(root, text = "Chào mưng đến với tkinter!")
label.pack(pady =20)
button = tk.Button(root, text = "Nhấn vào đây", command = button_click)
button.pack(pady = 10)

root.mainloop()