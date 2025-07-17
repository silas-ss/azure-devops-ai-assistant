#!/usr/bin/env python3
"""
Teste de cores e fontes do Tkinter
"""

import tkinter as tk
from tkinter import ttk

def main():
    print("Iniciando teste de cores e fontes...")
    
    root = tk.Tk()
    root.title("Teste Cores e Fontes")
    root.geometry("500x400")
    root.configure(bg='white')
    
    # Frame principal
    main_frame = tk.Frame(root, bg='white')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Teste 1: Label com cores explícitas
    print("Criando label com cores explícitas...")
    label1 = tk.Label(main_frame, 
                     text="TESTE 1: Label com cores explícitas",
                     bg='red', fg='white', font=('Arial', 12, 'bold'))
    label1.pack(pady=5)
    
    # Teste 2: Label com fundo branco e texto preto
    print("Criando label com fundo branco...")
    label2 = tk.Label(main_frame, 
                     text="TESTE 2: Fundo branco, texto preto",
                     bg='white', fg='black', font=('Arial', 12))
    label2.pack(pady=5)
    
    # Teste 3: Label com fundo amarelo
    print("Criando label com fundo amarelo...")
    label3 = tk.Label(main_frame, 
                     text="TESTE 3: Fundo amarelo, texto preto",
                     bg='yellow', fg='black', font=('Arial', 12))
    label3.pack(pady=5)
    
    # Teste 4: Text widget simples
    print("Criando text widget...")
    text = tk.Text(main_frame, height=4, width=40, bg='lightblue', fg='black')
    text.pack(pady=10)
    text.insert(tk.END, "TESTE 4: Text widget com fundo azul claro")
    
    # Teste 5: Entry com cores
    print("Criando entry com cores...")
    entry = tk.Entry(main_frame, bg='lightgreen', fg='black', font=('Arial', 10))
    entry.pack(pady=5)
    entry.insert(0, "TESTE 5: Entry com fundo verde claro")
    
    # Teste 6: Button com cores
    print("Criando botão com cores...")
    button = tk.Button(main_frame, 
                      text="TESTE 6: Botão colorido",
                      bg='orange', fg='black', font=('Arial', 10))
    button.pack(pady=5)
    
    # Teste 7: Label sem cores (padrão)
    print("Criando label padrão...")
    label_default = tk.Label(main_frame, text="TESTE 7: Label padrão (sem cores)")
    label_default.pack(pady=5)
    
    print("Todos os widgets criados. Iniciando mainloop...")
    root.mainloop()
    print("Teste finalizado.")

if __name__ == "__main__":
    main() 