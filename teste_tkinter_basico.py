#!/usr/bin/env python3
"""
Teste básico do Tkinter
"""

import tkinter as tk
from tkinter import ttk

def main():
    print("Iniciando teste básico do Tkinter...")
    
    # Criar janela
    root = tk.Tk()
    root.title("Teste Tkinter Básico")
    root.geometry("400x300")
    
    print("Janela criada")
    
    # Criar label
    label = tk.Label(root, text="Se você vê este texto, o Tkinter está funcionando!", 
                    font=('Arial', 14), bg='yellow', fg='black')
    label.pack(padx=20, pady=20)
    
    print("Label criado")
    
    # Criar botão
    button = tk.Button(root, text="Clique aqui", command=lambda: print("Botão clicado!"))
    button.pack(pady=10)
    
    print("Botão criado")
    
    # Criar entry
    entry = tk.Entry(root, width=30)
    entry.pack(pady=10)
    entry.insert(0, "Digite algo aqui...")
    
    print("Entry criado")
    
    # Criar text widget simples
    text = tk.Text(root, height=5, width=40)
    text.pack(pady=10)
    text.insert(tk.END, "Este é um widget Text simples.\nSe você vê este texto, o Text widget funciona!")
    
    print("Text widget criado")
    
    print("Iniciando mainloop...")
    root.mainloop()
    print("Mainloop finalizado.")

if __name__ == "__main__":
    main() 