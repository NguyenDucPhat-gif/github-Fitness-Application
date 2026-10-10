import tkinter as tk

root = tk.Tk()
root.title("Login Form")
root.geometry("500x200")

label_username = tk.Label(root, text = "Username:", fg = "blue")
label_username.grid(row = 0, column = 0, padx = 50, pady = 5, sticky = "w")
entry_username = tk.Entry(root)
entry_username.grid(row = 0, column = 1, padx = 0, pady = 0)

label_password = tk.Label(root, text = "Passwork", fg = "olive")
label_password.grid(row = 1, column = 0, padx = 50, pady = 5, sticky = "w")
entry_password = tk.Entry(root, show = "*")
entry_password.grid(row = 1, column = 1, padx = 0, pady = 0)

label_status = tk.Label(root, text = "", font = 13)
label_status.grid(row = 3, column = 0, columnspan = 2, pady = 5)

btn_login = tk.Button(root, text = "Login",command = lambda:(is_correct := (entry_username.get() == "user1" and entry_password.get() == "123456"), label_status.config(text = "Login successful." if is_correct else "Login failed. Try again.", fg = "green" if is_correct else "red")))
btn_login.grid(row = 2, column =1, padx = 15, pady = 5, sticky = "nesw")

root.mainloop() 