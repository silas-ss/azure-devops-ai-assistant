import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, Any, Optional, Callable
import threading
from datetime import datetime

from src.ui.chat_widget import ChatWidget
from src.ui.sidebar_widget import SidebarWidget
from src.ui.status_bar import StatusBar
from src.ui.settings_dialog import SettingsDialog
from src.utils.logger import logger

class MainWindow:
    """Main application window"""
    
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()
        
        logger.info("Main window initialized")
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Azure DevOps AI Assistant")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 600)
        
        # macOS specific settings
        if hasattr(self.root, 'tk') and hasattr(self.root.tk, 'call'):
            try:
                # Set window to be visible
                self.root.tk.call('wm', 'attributes', '.', '-topmost', '1')
                self.root.tk.call('wm', 'attributes', '.', '-topmost', '0')
                # Force window to be visible
                self.root.deiconify()
            except:
                pass
        
        # Set window icon if available
        try:
            # You can add an icon file later
            # self.root.iconbitmap("assets/icon.ico")
            pass
        except:
            pass
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)  # Sidebar - fixed width
        self.root.grid_columnconfigure(1, weight=1)  # Chat area - expandable
        
        # Style configuration
        self.setup_styles()
    
    def setup_styles(self):
        """Configure application styles"""
        style = ttk.Style()
        
        # Configure theme
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Configure colors
        style.configure('Main.TFrame', background='#f0f0f0')
        style.configure('Sidebar.TFrame', background='#2c3e50')
        style.configure('Chat.TFrame', background='#ffffff')
        
        # Configure buttons
        style.configure('Primary.TButton', 
                      background='#3498db', 
                      foreground='white',
                      padding=(10, 5))
        
        style.configure('Success.TButton',
                      background='#27ae60',
                      foreground='white',
                      padding=(10, 5))
        
        style.configure('Warning.TButton',
                      background='#f39c12',
                      foreground='white',
                      padding=(10, 5))
        
        # Configure labels
        style.configure('Title.TLabel',
                      font=('Segoe UI', 16, 'bold'),
                      foreground='#2c3e50')
        
        style.configure('Subtitle.TLabel',
                      font=('Segoe UI', 12),
                      foreground='#34495e')
        
        # Configure sidebar styles
        style.configure('Nav.TButton',
                      background='#34495e',
                      foreground='white',
                      padding=(10, 8),
                      font=('Segoe UI', 10))
        
        style.configure('NavActive.TButton',
                      background='#3498db',
                      foreground='white',
                      padding=(10, 8),
                      font=('Segoe UI', 10, 'bold'))
        
        style.configure('QuickAction.TButton',
                      background='#27ae60',
                      foreground='white',
                      padding=(8, 6),
                      font=('Segoe UI', 9))
        
        style.configure('Info.TLabel',
                      font=('Segoe UI', 9),
                      foreground='#95a5a6')
    
    def create_widgets(self):
        """Create main application widgets"""
        print("DEBUG: Iniciando criação dos widgets")
        
        # Create main container
        print("DEBUG: Criando main_frame")
        self.main_frame = ttk.Frame(self.root, style='Main.TFrame')
        self.main_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=0)  # Sidebar - fixed width
        self.main_frame.grid_columnconfigure(1, weight=1)  # Chat area - expandable
        
        # Force update to ensure proper layout
        self.main_frame.update_idletasks()
        
        # Create sidebar
        print("DEBUG: Criando sidebar")
        self.sidebar = SidebarWidget(self.main_frame, self)
        self.sidebar.grid(row=0, column=0, sticky='nsew', padx=(0, 2))
        self.sidebar.configure(width=300)  # Set minimum width for sidebar
        print("DEBUG: Sidebar criada com sucesso")
        
        # Create chat area
        print("DEBUG: Criando chat_widget")
        self.chat_widget = ChatWidget(self.main_frame, self)
        self.chat_widget.grid(row=0, column=1, sticky='nsew', padx=(2, 0))
        print("DEBUG: Chat_widget criado com sucesso")
        
        # Create status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        # Create menu bar
        self.create_menu()
        
        # Force update to ensure proper layout
        self.root.update_idletasks()
        
        # Verify chat widget is properly configured
        if hasattr(self, 'chat_widget') and self.chat_widget:
            logger.info("Chat widget created successfully")
            logger.info(f"Chat widget grid info: {self.chat_widget.grid_info()}")
            logger.info(f"Main frame grid info: {self.main_frame.grid_info()}")
            # logger.info(f"Root window grid info: {self.root.grid_info()}")
        else:
            logger.error("Chat widget not created properly")
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Configurações", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.quit_app)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizar", menu=view_menu)
        view_menu.add_command(label="Boards", command=self.show_boards)
        view_menu.add_command(label="Work Items", command=self.show_work_items)
        view_menu.add_separator()
        view_menu.add_command(label="Limpar Chat", command=self.clear_chat)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Comandos", command=self.show_help)
        help_menu.add_command(label="Sobre", command=self.show_about)
    
    def setup_bindings(self):
        """Setup keyboard and event bindings"""
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.show_settings())
        self.root.bind('<Control-h>', lambda e: self.show_help())
        self.root.bind('<Control-l>', lambda e: self.clear_chat())
        self.root.bind('<F5>', lambda e: self.refresh_data())
    
    def show_settings(self):
        """Show settings dialog"""
        try:
            dialog = SettingsDialog(self.root, self.app_controller)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            logger.error(f"Error showing settings: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir configurações: {e}")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """🤖 Assistente Azure DevOps - Ajuda

📋 Comandos Disponíveis

Boards:
- "Liste os boards" - Mostra todos os boards do projeto
- "Mostre os quadros disponíveis" - Lista boards disponíveis

Work Items:
- "Liste os work items" - Mostra todos os work items
- "Mostre os bugs" - Lista apenas bugs
- "Liste as features" - Lista apenas features

Work Item Específico:
- "Mostre o item #123" - Exibe detalhes do work item 123

Busca:
- "Busque itens com 'login'" - Procura work items contendo 'login'

💡 Dicas
- Use comandos em português ou inglês
- Para ver detalhes completos, use o ID do work item
- Use aspas para termos de busca com espaços
- Digite "ajuda" a qualquer momento para ver esta lista

🔧 Atalhos de Teclado
- Ctrl+S: Configurações
- Ctrl+H: Ajuda
- Ctrl+L: Limpar chat
- F5: Atualizar dados"""
        
        try:
            messagebox.showinfo("Ajuda - Azure DevOps AI Assistant", help_text)
        except Exception as e:
            logger.error(f"Error showing help: {e}")
            messagebox.showerror("Erro", f"Erro ao mostrar ajuda: {e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Azure DevOps AI Assistant v1.0.0

Um assistente inteligente para interagir com Azure DevOps
através de chat natural.

Desenvolvido com Python e Tkinter.

Funcionalidades:
• Chat natural com LLM
• Integração com Azure DevOps API
• Visualização de boards e work items
• Busca inteligente de itens
• Interface gráfica moderna

Para suporte, consulte a documentação."""
        
        messagebox.showinfo("Sobre", about_text)
    
    def show_boards(self):
        """Show boards in chat"""
        self.chat_widget.send_message("Liste os boards")
    
    def show_work_items(self):
        """Show work items in chat"""
        self.chat_widget.send_message("Liste os work items")
    
    def clear_chat(self):
        """Clear chat history"""
        if messagebox.askyesno("Limpar Chat", "Deseja limpar todo o histórico do chat?"):
            self.chat_widget.clear_chat()
    
    def refresh_data(self):
        """Refresh application data"""
        self.status_bar.set_status("Atualizando dados...", "info")
        
        def refresh_thread():
            try:
                # Refresh Azure DevOps connection
                if self.app_controller.test_azure_devops_connection():
                    self.status_bar.set_status("Dados atualizados com sucesso", "success")
                else:
                    self.status_bar.set_status("Erro ao atualizar dados", "error")
            except Exception as e:
                logger.error(f"Error refreshing data: {e}")
                self.status_bar.set_status("Erro ao atualizar dados", "error")
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def quit_app(self):
        """Quit application"""
        if messagebox.askyesno("Sair", "Deseja realmente sair da aplicação?"):
            self.on_closing()
    
    def on_closing(self):
        """Handle window closing"""
        try:
            # Save any pending data
            self.app_controller.save_session()
            
            # Close window
            self.root.destroy()
            
            logger.info("Application closed")
        except Exception as e:
            logger.error(f"Error closing application: {e}")
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update status bar"""
        self.status_bar.set_status(message, status_type)
    
    def show_error(self, title: str, message: str):
        """Show error dialog"""
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str):
        """Show info dialog"""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title: str, message: str):
        """Show warning dialog"""
        messagebox.showwarning(title, message)
    
    def bring_to_front(self):
        """Bring main window to front"""
        try:
            print("DEBUG: Trazendo janela principal para o fronto")
            self.root.lift()
            self.root.focus_force()
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            
            # Ensure window is visible
            self.root.deiconify()
            self.root.state('normal')
            
            print("DEBUG: Janela principal deve estar visível agora")
        except Exception as e:
            print(f"DEBUG: Erro ao trazer janela para o fronto: {e}")
            logger.error(f"Error bringing window to front: {e}")
    
    def load_sidebar_info(self):
        """Load sidebar information after mainloop is active"""
        try:
            if hasattr(self, 'sidebar') and self.sidebar:
                self.sidebar.load_project_info()
                print("DEBUG: Informações da sidebar carregadas")
        except Exception as e:
            print(f"DEBUG: Erro ao carregar informações da sidebar: {e}")
            logger.error(f"Error loading sidebar info: {e}")
    
    def run(self):
        """Start the application"""
        try:
            print("DEBUG: Iniciando método run da MainWindow")
            
            # Show welcome message
            print("DEBUG: Adicionando mensagem de boas-vindas")
            self.chat_widget.add_system_message("Bem-vindo ao Azure DevOps AI Assistant!")
            
            # Force final layout update
            print("DEBUG: Forçando atualização do layout")
            self.root.update_idletasks()
            
            print("DEBUG: Iniciando mainloop")
            
            # Force window to appear on top (macOS fix)
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after_idle(lambda: self.root.attributes('-topmost', False))
            
            # Force focus and deiconify
            self.root.focus_force()
            self.root.deiconify()
            
            # Ensure window is not minimized
            try:
                self.root.state('normal')
            except:
                pass
            
            # Bring main window to front after a longer delay to ensure notifications are shown first
            self.root.after(500, self.bring_to_front)
            
            # Load project info after mainloop is active
            self.root.after(1000, self.load_sidebar_info)
            
            # Start the main loop
            self.root.mainloop()
            print("DEBUG: Mainloop finalizado")
        except Exception as e:
            print(f"DEBUG: Erro no método run: {e}")
            logger.error(f"Error running application: {e}")
            raise 