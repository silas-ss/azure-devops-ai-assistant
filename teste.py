import ttkbootstrap as tb

root = tb.Window(themename='flatly')
tb.Label(root, text="Tema Claro (flatly)", font=("Arial", 18)).pack(pady=20)
tb.Button(root, text="Mudar para escuro", command=lambda: root.style.theme_use('darkly')).pack()
tb.Button(root, text="Mudar para claro", command=lambda: root.style.theme_use('flatly')).pack()
root.mainloop()