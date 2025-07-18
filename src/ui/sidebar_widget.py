import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from typing import Dict, Any, Optional, Callable, List
import threading
import traceback
from datetime import datetime

from src.utils.logger import logger

class SidebarWidget(tb.Frame):
    """Sidebar widget with navigation and project info"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.app_controller = main_window.app_controller
        
        # Navigation state
        self.current_section = "chat"
        self.sections = {
            "chat": "💬 Chat",
            "boards": "📋 Boards",
            "work_items": "📝 Work Items",
            "search": "🔍 Busca",
            "settings": "⚙️ Configurações"
        }
        
        # Project info
        self.project_info = {}
        self.connection_status = {
            'azure_devops': False,
            'llm': False
        }
        
        # UI elements
        self.navigation_frame = None
        self.project_frame = None
        self.status_frame = None
        self.nav_buttons = {}
        
        self.setup_widget()
        # Não chamar load_project_info aqui - será chamado depois do mainloop estar ativo
        logger.info("Sidebar widget initialized")
    
    def setup_widget(self):
        """Setup sidebar layout"""
        print("DEBUG: Configurando sidebar layout")

        # Obter configurações do usuário
        settings = {}
        if hasattr(self.main_window.app_controller, 'get_ui_settings'):
            settings = self.main_window.app_controller.get_ui_settings()
        elif hasattr(self.main_window.app_controller, 'settings'):
            settings = getattr(self.main_window.app_controller, 'settings', {})

        # Garantir que a fonte seja sempre válida
        font_family = str(settings.get('chat_font', 'Segoe UI')).strip()
        # Lista de fontes seguras/fallback
        safe_fonts = ['Arial', 'Helvetica', 'Segoe UI', 'Tahoma', 'Verdana']
        # Se a fonte não for válida, usar Segoe UI
        if not font_family or font_family.lower() in ['ui', ''] or font_family not in safe_fonts:
            font_family = 'Segoe UI'
            print(f"DEBUG: Fonte inválida detectada, usando fallback: {font_family}")

        # Garantir que o tamanho da fonte seja sempre um inteiro válido
        try:
            font_size = int(settings.get('chat_font_size', 12))
            if font_size < 8:  # Muito pequeno
                font_size = 8
            elif font_size > 32:  # Muito grande
                font_size = 32
        except (ValueError, TypeError):
            font_size = 12  # Fallback seguro
            print("DEBUG: Tamanho de fonte inválido detectado, usando fallback: 12")

        print(f"DEBUG: Usando fonte: {font_family}, tamanho: {font_size}")

        # Configure grid
        self.grid_rowconfigure(1, weight=1)  # Project info takes most space
        self.grid_columnconfigure(0, weight=1)

        # Create navigation
        print("DEBUG: Criando navegação")
        self.create_navigation(font_family, font_size)

        # Create project info
        print("DEBUG: Criando informações do projeto")
        self.create_project_info(font_family, font_size)

        # Create status section
        print("DEBUG: Criando seção de status")
        self.create_status_section(font_family, font_size)

        print("DEBUG: Sidebar layout configurado com sucesso")
    
    def create_navigation(self, font_family, font_size):
        """Create navigation section"""
        print("DEBUG: Criando frame de navegação")
        # Navigation frame
        self.navigation_frame = tb.Frame(self, style='Card.TFrame')
        self.navigation_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        self.navigation_frame.grid_columnconfigure(0, weight=1)
        print("DEBUG: Frame de navegação criado")

        # Navigation label
        nav_label = tb.Label(
            self.navigation_frame,
            text="🧭 Navegação",
            style='Title.TLabel'
        )
        nav_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

        # Navigation buttons
        for i, (section_id, section_name) in enumerate(self.sections.items()):
            button = tb.Button(
                self.navigation_frame,
                text=section_name,
                bootstyle="secondary",
                style='Nav.TButton',
                command=lambda sid=section_id: self.navigate_to_section(sid)
            )
            button.grid(row=i+1, column=0, sticky='ew', pady=4, padx=2, ipadx=4, ipady=4)
            self.nav_buttons[section_id] = button

        # Highlight current section
        self.highlight_current_section()
    
    def create_project_info(self, font_family, font_size):
        """Create project info section"""
        self.project_frame = tb.Frame(self, style='Card.TFrame')
        self.project_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        self.project_frame.grid_columnconfigure(0, weight=1)

        project_label = tb.Label(
            self.project_frame,
            text="📁 Projeto",
            style='Subtitle.TLabel'
        )
        project_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Project details
        self.create_project_details(font_family, font_size)
        
        # Quick actions
        self.create_quick_actions(font_family, font_size)
    
    def create_project_details(self, font_family, font_size):
        """Create project details section"""
        # Project details frame
        details_frame = tb.Frame(self.project_frame)
        details_frame.grid(row=1, column=0, sticky='ew')
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Organization
        org_label = tb.Label(
            details_frame,
            text="Organização:",
            font=(font_family, int(font_size)-1, "bold")
        )
        org_label.grid(row=0, column=0, sticky='w', pady=2)
        
        self.org_value = tb.Label(
            details_frame,
            text="Não configurado",
            font=(font_family, int(font_size)-1)
        )
        self.org_value.grid(row=0, column=1, sticky='w', padx=(5, 0), pady=2)
        
        # Project
        project_label = tb.Label(
            details_frame,
            text="Projeto:",
            font=(font_family, int(font_size)-1, "bold")
        )
        project_label.grid(row=1, column=0, sticky='w', pady=2)
        
        self.project_value = tb.Label(
            details_frame,
            text="Não configurado",
            font=(font_family, int(font_size)-1)
        )
        self.project_value.grid(row=1, column=1, sticky='w', padx=(5, 0), pady=2)
        
        # Team
        team_label = tb.Label(
            details_frame,
            text="Equipe:",
            font=(font_family, int(font_size)-1, "bold")
        )
        team_label.grid(row=2, column=0, sticky='w', pady=2)
        
        self.team_value = tb.Label(
            details_frame,
            text="Não configurado",
            font=(font_family, int(font_size)-1)
        )
        self.team_value.grid(row=2, column=1, sticky='w', padx=(5, 0), pady=2)
    
    def create_quick_actions(self, font_family, font_size):
        """Create quick actions section"""
        # Quick actions frame
        actions_frame = tb.Frame(self.project_frame)
        actions_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        actions_frame.grid_columnconfigure(0, weight=1)
        
        # Quick actions label
        actions_label = tb.Label(
            actions_frame,
            text="⚡ Ações Rápidas",
            font=(font_family, int(font_size)-1, "bold")
        )
        actions_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Quick action buttons
        quick_actions = [
            ("🔄 Atualizar", self.refresh_project),
            ("📊 Boards", lambda: self.navigate_to_section("boards")),
            ("📝 Work Items", lambda: self.navigate_to_section("work_items")),
            ("🔍 Buscar", lambda: self.navigate_to_section("search"))
        ]
        
        for i, (text, command) in enumerate(quick_actions):
            button = tb.Button(
                actions_frame,
                text=text,
                bootstyle="success",
                command=command
            )
            button.grid(row=i+1, column=0, sticky='ew', pady=2)
    
    def create_status_section(self, font_family, font_size):
        """Create status section"""
        self.status_frame = tb.Frame(self, style='Card.TFrame')
        self.status_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=10)
        self.status_frame.grid_columnconfigure(0, weight=1)

        status_label = tb.Label(
            self.status_frame,
            text="🔗 Status",
            style='Subtitle.TLabel'
        )
        status_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Connection status
        self.create_connection_status(font_family, font_size)
        
        # Last update
        self.last_update_label = tb.Label(
            self.status_frame,
            text="Última atualização: Nunca",
            font=(font_family, int(font_size)-1)
        )
        self.last_update_label.grid(row=3, column=0, sticky='w', pady=5)
    
    def create_connection_status(self, font_family, font_size):
        """Create connection status indicators"""
        # Azure DevOps status
        azure_frame = tb.Frame(self.status_frame)
        azure_frame.grid(row=1, column=0, sticky='ew', pady=2)
        azure_frame.grid_columnconfigure(1, weight=1)
        
        azure_icon = tb.Label(
            azure_frame,
            text="🔴",
            font=(font_family, int(font_size))
        )
        azure_icon.grid(row=0, column=0, padx=(0, 5))
        
        azure_label = tb.Label(
            azure_frame,
            text="Azure DevOps",
            font=(font_family, int(font_size)-1)
        )
        azure_label.grid(row=0, column=1, sticky='w')
        
        self.azure_status_icon = azure_icon
        self.azure_status_label = azure_label
        
        # LLM status
        llm_frame = tb.Frame(self.status_frame)
        llm_frame.grid(row=2, column=0, sticky='ew', pady=2)
        llm_frame.grid_columnconfigure(1, weight=1)
        
        llm_icon = tb.Label(
            llm_frame,
            text="🔴",
            font=(font_family, int(font_size))
        )
        llm_icon.grid(row=0, column=0, padx=(0, 5))
        
        llm_label = tb.Label(
            llm_frame,
            text="LLM",
            font=(font_family, int(font_size)-1)
        )
        llm_label.grid(row=0, column=1, sticky='w')
        
        self.llm_status_icon = llm_icon
        self.llm_status_label = llm_label
    
    def navigate_to_section(self, section_id: str):
        """Navigate to a specific section"""
        if section_id not in self.sections:
            logger.warning(f"Unknown section: {section_id}")
            return
        
        # Update current section
        self.current_section = section_id
        
        # Highlight current section
        self.highlight_current_section()
        
        # Handle section-specific actions
        if section_id == "chat":
            # Focus on chat
            if hasattr(self.main_window, 'chat_widget'):
                self.main_window.chat_widget.focus_input()
        
        elif section_id == "boards":
            # Show boards in chat
            self.main_window.show_boards()
        
        elif section_id == "work_items":
            # Show work items in chat
            self.main_window.show_work_items()
        
        elif section_id == "search":
            # Show search in chat
            self.main_window.chat_widget.send_message("Busque itens com 'termo'")
        
        elif section_id == "settings":
            # Show settings dialog
            self.main_window.show_settings()
        
        logger.info(f"Navigated to section: {section_id}")
    
    def highlight_current_section(self):
        """Highlight the current section button"""
        for section_id, button in self.nav_buttons.items():
            if section_id == self.current_section:
                button.configure(style='NavActive.TButton')
            else:
                button.configure(style='Nav.TButton')
    
    def load_project_info(self):
        """Load project information"""
        def load_thread():
            try:
                # Get project info from app controller
                if hasattr(self.app_controller, 'get_project_info'):
                    project_info = self.app_controller.get_project_info()
                    # Atualize a UI na thread principal
                    self.after(0, lambda: self.update_project_info(project_info))
                # Test connections na thread principal
                self.after(0, self.test_connections)
            except Exception as e:
                logger.error(f"Error loading project info: {e}\n{traceback.format_exc()}")
        threading.Thread(target=load_thread, daemon=True).start()
    
    def update_project_info(self, project_info: Dict[str, Any]):
        logger.info(f"update_project_info called in thread: {threading.current_thread().name}")
        self.project_info = project_info
        
        # Update organization
        org = project_info.get('organization', 'Não configurado')
        self.org_value.config(text=org)
        
        # Update project
        project = project_info.get('project', 'Não configurado')
        self.project_value.config(text=project)
        
        # Update team
        team = project_info.get('team', 'Não configurado')
        self.team_value.config(text=team)
        
        # Update last update time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.config(text=f"Última atualização: {current_time}")
        
        logger.info("Project info updated")
    
    def test_connections(self):
        """Test Azure DevOps and LLM connections"""
        def test_thread():
            try:
                # Test Azure DevOps connection
                azure_connected = False
                if hasattr(self.app_controller, 'test_azure_devops_connection'):
                    azure_connected = self.app_controller.test_azure_devops_connection()
                self.after(0, lambda: self.update_azure_devops_status(azure_connected))

                # Test LLM connection
                llm_connected = False
                if hasattr(self.app_controller, 'test_llm_connection'):
                    llm_connected = self.app_controller.test_llm_connection()
                self.after(0, lambda: self.update_llm_status(llm_connected))
            except Exception as e:
                logger.error(f"Error testing connections: {e}")
        threading.Thread(target=test_thread, daemon=True).start()
    
    def update_azure_devops_status(self, connected: bool):
        logger.info(f"update_azure_devops_status called in thread: {threading.current_thread().name}")
        self.connection_status['azure_devops'] = connected
        
        if connected:
            self.azure_status_icon.config(text="🟢")
            self.azure_status_label.config(foreground='#27ae60')
        else:
            self.azure_status_icon.config(text="🔴")
            self.azure_status_label.config(foreground='#e74c3c')
    
    def update_llm_status(self, connected: bool):
        logger.info(f"update_llm_status called in thread: {threading.current_thread().name}")
        self.connection_status['llm'] = connected
        
        if connected:
            self.llm_status_icon.config(text="🟢")
            self.llm_status_label.config(foreground='#27ae60')
        else:
            self.llm_status_icon.config(text="🔴")
            self.llm_status_label.config(foreground='#e74c3c')
    
    def refresh_project(self):
        """Refresh project information"""
        self.main_window.update_status("Atualizando informações do projeto...", "info")
        def refresh_thread():
            try:
                self.after(0, self.load_project_info)
                self.after(0, lambda: self.main_window.update_status("Projeto atualizado", "success"))
            except Exception as e:
                logger.error(f"Error refreshing project: {e}")
                self.after(0, lambda: self.main_window.update_status("Erro ao atualizar projeto", "error"))
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def get_current_section(self) -> str:
        """Get current section"""
        return self.current_section
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get current project info"""
        return self.project_info.copy()
    
    def get_connection_status(self) -> Dict[str, bool]:
        """Get connection status"""
        return self.connection_status.copy()
    
    def show_project_details(self):
        """Show detailed project information"""
        if not self.project_info:
            messagebox.showinfo("Projeto", "Nenhuma informação do projeto disponível.")
            return
        
        details = f"""**Informações do Projeto**

**Organização:** {self.project_info.get('organization', 'N/A')}
**Projeto:** {self.project_info.get('project', 'N/A')}
**Equipe:** {self.project_info.get('team', 'N/A')}
**URL:** {self.project_info.get('url', 'N/A')}

**Status das Conexões:**
• Azure DevOps: {'🟢 Conectado' if self.connection_status['azure_devops'] else '🔴 Desconectado'}
• LLM: {'🟢 Conectado' if self.connection_status['llm'] else '🔴 Desconectado'}

**Última Atualização:** {self.last_update_label.cget('text')}"""
        
        # Create details window
        details_window = tk.Toplevel(self.main_window.root)
        details_window.title("Detalhes do Projeto")
        details_window.geometry("400x300")
        details_window.resizable(True, True)
        
        # Create text widget
        text_widget = tk.Text(details_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Insert details
        text_widget.insert(tk.END, details)
        text_widget.config(state=tk.DISABLED) 