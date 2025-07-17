#!/usr/bin/env python3
"""
Teste simplificado da aplicação principal
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

class ChatWidgetSimples(ttk.Frame):
    """Versão simplificada do ChatWidget"""
    
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
        self.chat_display.insert(tk.END, "Teste da aplicação - Chat funcionando!\n")
    
    def send_message(self):
        """Send message"""
        message = self.input_entry.get().strip()
        if message:
            self.chat_display.insert(tk.END, f"Você: {message}\n")
            self.input_entry.delete(0, tk.END)

class SidebarSimples(ttk.Frame):
    """Versão simplificada da sidebar"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_widget()
    
    def setup_widget(self):
        """Setup simplificado"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Simple label
        label = ttk.Label(self, text="Sidebar\nSimples", font=('Arial', 12))
        label.grid(row=0, column=0, padx=10, pady=10)

class MainWindowSimples:
    """Versão simplificada da MainWindow"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
    
    def setup_window(self):
        """Setup window"""
        self.root.title("Teste App Simples")
        self.root.geometry("1000x600")
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)  # Sidebar
        self.root.grid_columnconfigure(1, weight=1)  # Chat
    
    def create_widgets(self):
        """Create widgets"""
        print("Criando widgets...")
        
        # Create sidebar
        print("Criando sidebar...")
        self.sidebar = SidebarSimples(self.root)
        self.sidebar.grid(row=0, column=0, sticky='nsew', padx=(0, 2))
        print("Sidebar criada")
        
        # Create chat
        print("Criando chat...")
        self.chat = ChatWidgetSimples(self.root)
        self.chat.grid(row=0, column=1, sticky='nsew', padx=(2, 0))
        print("Chat criado")
        
        # Create status bar
        print("Criando status bar...")
        self.status_bar = ttk.Label(self.root, text="Status: Pronto", relief=tk.SUNKEN)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky='ew')
        print("Status bar criada")
        
        print("Todos os widgets criados com sucesso!")
    
    def run(self):
        """Run application"""
        print("Iniciando aplicação...")
        self.root.mainloop()
        print("Aplicação finalizada.")

def main():
    """Main function"""
    print("Iniciando teste da aplicação simplificada...")
    app = MainWindowSimples()
    app.run()

if __name__ == "__main__":
    main() 