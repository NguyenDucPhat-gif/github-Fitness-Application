import tkinter as tk

root = tk.Tk()
root.title("su dung phuong thuc ...")

# tao cac widget
label1 = tk.Label(root, text = "Label 1", bg = "red", fg = "white")
label2 = tk.Label(root, text = "Label 2", bg = "green", fg = "white")
label3 = tk.Label(root, text = "Label 3", bg = "blue", fg = "white")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# # sắp xếp các widget bằng Pack
# label1.pack(side = "top", fill = "x")
# label2.pack(side = "left", fill = "y")
# label3.pack(side = "right", fill = "both", expand = True)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# # sap xep cac widget bang Grid
# label1.grid(row=0, column=0, sticky='nsew')
# label2.grid(row=1, column=0, sticky='nsew')
# label3.grid(row=0, column=1, rowspan=2, sticky='nsew')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# # đặt trọng số cho cột và hàng để widget mở rộng
# root.columnconfigure(0, weight = 1)
# root.columnconfigure(1, weight = 2)
# root.rowconfigure(0, weight = 1)
# root.rowconfigure(1, weight = 1)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# label1 = tk.Label(root, text = "duc")
# label2 = tk.Label(root, text = "phat")
# label3 = tk.Label(root, text = "BEO")
# label1.place(x = 100, y = 0) # Đặt label ở tọa độ (12,2)
# label2.place(x = 120, y = 20)
# label3.place(x = 140, y = 40)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# # vi du ve cac tuy chon place
# label = tk.Label(root, text = "hello", bg = "teal", fg = "black")
# # sử dụng các tùy chọn place
# label.place(anchor = "nw", relx = 0.5, rely = 0.5, relwidth = 0.75, relheight = 0.5, bordermode = "inside")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
label1.place(x = 50, y = 50, width = 100, height = 50, anchor = "nw")
label2.place(relx = 0.5, rely = 0.5, relwidth = 0.6, relheight = 0.3, anchor = "center")
label3.place(x = 200, y = 200, width = 150, height = 100, anchor = "se")

root.mainloop()