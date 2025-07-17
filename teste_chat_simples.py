#!/usr/bin/env python3
"""
Teste simples do ChatWidget
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

class ChatWidgetSimples(ttk.Frame):
    """Versão simplificada do ChatWidget para teste"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_widget()
    
    def setup_widget(self):
        """Setup simplificado"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            state=tk.NORMAL,
            font=('Arial', 10),
            bg='white',
            fg='black',
            width=50,
            height=20
        )
        self.chat_display.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Input frame
        input_frame = ttk.Frame(self)
        input_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Input entry
        self.input_entry = ttk.Entry(input_frame)
        self.input_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        # Send button
        self.send_button = ttk.Button(input_frame, text="Enviar", command=self.send_message)
        self.send_button.grid(row=0, column=1)
        
        # Add test message
        self.chat_display.insert(tk.END, "Teste do ChatWidget - Se você vê esta mensagem, o widget está funcionando!\n")
    
    def send_message(self):
        """Send message"""
        message = self.input_entry.get().strip()
        if message:
            self.chat_display.insert(tk.END, f"Você: {message}\n")
            self.input_entry.delete(0, tk.END)

def main():
    """Teste principal"""
    root = tk.Tk()
    root.title("Teste ChatWidget")
    root.geometry("600x400")
    
    # Configure grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Create chat widget
    chat = ChatWidgetSimples(root)
    chat.grid(row=0, column=0, sticky='nsew')
    
    print("Iniciando teste do ChatWidget...")
    root.mainloop()
    print("Teste concluído.")

if __name__ == "__main__":
    main() 