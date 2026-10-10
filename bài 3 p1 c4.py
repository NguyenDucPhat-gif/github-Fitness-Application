import tkinter as tk

def handle_sunmit():
    input = entry.get()
    result_label.config(text = f'You wrote: {input}')

root = tk.Tk()
root.title("Welcome to ?")
root.geometry("500x200")

entry = tk.Entry(root, width = 30)
entry.pack(pady = 15)

submit_button = tk.Button(root, text = "submit",fg = "teal", command = handle_sunmit)
submit_button.pack(pady = 5)

result_label = tk.Label(root, text = "")
result_label.pack(pady = 15)

root.mainloop()