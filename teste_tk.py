import tkinter as tk

root = tk.Tk()
root.title("Teste Tkinter")
root.geometry("400x200")
label = tk.Label(root, text="Janela Tkinter funcionando!")
label.pack(padx=20, pady=20)
root.mainloop()
