import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, font
from typing import Dict, Any, Optional, Callable
import json
from pathlib import Path

from src.utils.logger import logger

class SettingsDialog:
    """Settings dialog for UI customization"""
    
    def __init__(self, parent, app_controller):
        self.parent = parent
        self.app_controller = app_controller
        self.dialog = tk.Toplevel(parent)
        
        # Settings data
        self.current_settings = self.load_settings()
        self.original_settings = self.current_settings.copy()
        
        # UI elements
        self.notebook = None
        self.apply_button = None
        self.cancel_button = None
        self.ok_button = None
        
        self.setup_dialog()
        self.create_widgets()
        self.load_current_settings()
        
        logger.info("Settings dialog initialized")
    
    def setup_dialog(self):
        """Setup dialog properties"""
        self.dialog.title("Configurações")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog on parent
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
    
    def create_widgets(self):
        """Create settings widgets"""
        # Configure grid
        self.dialog.grid_rowconfigure(0, weight=1)
        self.dialog.grid_columnconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # Create tabs
        self.create_appearance_tab()
        self.create_chat_tab()
        self.create_connections_tab()
        self.create_advanced_tab()
        
        # Create buttons
        self.create_buttons()
    
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        appearance_frame = ttk.Frame(self.notebook)
        self.notebook.add(appearance_frame, text="Aparência")
        
        # Configure grid
        appearance_frame.grid_columnconfigure(1, weight=1)
        
        # Theme settings
        theme_label = ttk.Label(appearance_frame, text="Tema:", font=('Segoe UI', 10, 'bold'))
        theme_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.theme_var = tk.StringVar(value=self.current_settings.get('theme', 'light'))
        theme_combo = ttk.Combobox(
            appearance_frame,
            textvariable=self.theme_var,
            values=['light', 'dark', 'system'],
            state='readonly',
            width=20
        )
        theme_combo.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        
        # Font settings
        font_label = ttk.Label(appearance_frame, text="Fonte:", font=('Segoe UI', 10, 'bold'))
        font_label.grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        self.font_var = tk.StringVar(value=self.current_settings.get('font_family', 'Segoe UI'))
        font_combo = ttk.Combobox(
            appearance_frame,
            textvariable=self.font_var,
            values=['Segoe UI', 'Arial', 'Helvetica', 'Times New Roman', 'Courier New'],
            state='readonly',
            width=20
        )
        font_combo.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        
        # Font size settings
        font_size_label = ttk.Label(appearance_frame, text="Tamanho da fonte:", font=('Segoe UI', 10, 'bold'))
        font_size_label.grid(row=2, column=0, sticky='w', padx=10, pady=5)
        
        self.font_size_var = tk.IntVar(value=self.current_settings.get('font_size', 10))
        font_size_spin = ttk.Spinbox(
            appearance_frame,
            from_=8,
            to=16,
            textvariable=self.font_size_var,
            width=10
        )
        font_size_spin.grid(row=2, column=1, sticky='w', padx=10, pady=5)
        
        # Window size settings
        window_size_label = ttk.Label(appearance_frame, text="Tamanho da janela:", font=('Segoe UI', 10, 'bold'))
        window_size_label.grid(row=3, column=0, sticky='w', padx=10, pady=5)
        
        window_size_frame = ttk.Frame(appearance_frame)
        window_size_frame.grid(row=3, column=1, sticky='w', padx=10, pady=5)
        
        self.width_var = tk.IntVar(value=self.current_settings.get('window_width', 1400))
        self.height_var = tk.IntVar(value=self.current_settings.get('window_height', 900))
        
        ttk.Label(window_size_frame, text="Largura:").grid(row=0, column=0, padx=(0, 5))
        ttk.Spinbox(window_size_frame, from_=800, to=2000, textvariable=self.width_var, width=8).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(window_size_frame, text="Altura:").grid(row=0, column=2, padx=(0, 5))
        ttk.Spinbox(window_size_frame, from_=600, to=1500, textvariable=self.height_var, width=8).grid(row=0, column=3)
    
    def create_chat_tab(self):
        """Create chat settings tab"""
        chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(chat_frame, text="Chat")
        
        # Configure grid
        chat_frame.grid_columnconfigure(1, weight=1)
        
        # Chat history limit
        history_label = ttk.Label(chat_frame, text="Limite do histórico:", font=('Segoe UI', 10, 'bold'))
        history_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.history_limit_var = tk.IntVar(value=self.current_settings.get('chat_history_limit', 100))
        history_spin = ttk.Spinbox(
            chat_frame,
            from_=10,
            to=1000,
            textvariable=self.history_limit_var,
            width=10
        )
        history_spin.grid(row=0, column=1, sticky='w', padx=10, pady=5)
        
        # Auto-scroll
        self.auto_scroll_var = tk.BooleanVar(value=self.current_settings.get('auto_scroll', True))
        auto_scroll_check = ttk.Checkbutton(
            chat_frame,
            text="Rolagem automática",
            variable=self.auto_scroll_var
        )
        auto_scroll_check.grid(row=1, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Show timestamps
        self.show_timestamps_var = tk.BooleanVar(value=self.current_settings.get('show_timestamps', True))
        timestamps_check = ttk.Checkbutton(
            chat_frame,
            text="Mostrar timestamps",
            variable=self.show_timestamps_var
        )
        timestamps_check.grid(row=2, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Message grouping
        self.group_messages_var = tk.BooleanVar(value=self.current_settings.get('group_messages', False))
        group_check = ttk.Checkbutton(
            chat_frame,
            text="Agrupar mensagens",
            variable=self.group_messages_var
        )
        group_check.grid(row=3, column=0, columnspan=2, sticky='w', padx=10, pady=5)
    
    def create_connections_tab(self):
        """Create connections settings tab"""
        connections_frame = ttk.Frame(self.notebook)
        self.notebook.add(connections_frame, text="Conexões")
        
        # Configure grid
        connections_frame.grid_columnconfigure(1, weight=1)
        
        # Azure DevOps settings
        azure_label = ttk.Label(connections_frame, text="Azure DevOps:", font=('Segoe UI', 10, 'bold'))
        azure_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        # Organization
        org_label = ttk.Label(connections_frame, text="Organização:")
        org_label.grid(row=1, column=0, sticky='w', padx=20, pady=2)
        
        self.org_var = tk.StringVar(value=self.current_settings.get('azure_devops_org', ''))
        org_entry = ttk.Entry(connections_frame, textvariable=self.org_var, width=30)
        org_entry.grid(row=1, column=1, sticky='ew', padx=10, pady=2)
        
        # Project
        project_label = ttk.Label(connections_frame, text="Projeto:")
        project_label.grid(row=2, column=0, sticky='w', padx=20, pady=2)
        
        self.project_var = tk.StringVar(value=self.current_settings.get('azure_devops_project', ''))
        project_entry = ttk.Entry(connections_frame, textvariable=self.project_var, width=30)
        project_entry.grid(row=2, column=1, sticky='ew', padx=10, pady=2)
        
        # LLM settings
        llm_label = ttk.Label(connections_frame, text="LLM:", font=('Segoe UI', 10, 'bold'))
        llm_label.grid(row=3, column=0, sticky='w', padx=10, pady=5)
        
        # Default provider
        provider_label = ttk.Label(connections_frame, text="Provider padrão:")
        provider_label.grid(row=4, column=0, sticky='w', padx=20, pady=2)
        
        self.provider_var = tk.StringVar(value=self.current_settings.get('default_llm_provider', 'openai'))
        provider_combo = ttk.Combobox(
            connections_frame,
            textvariable=self.provider_var,
            values=['openai', 'anthropic', 'google', 'deepseek'],
            state='readonly',
            width=20
        )
        provider_combo.grid(row=4, column=1, sticky='w', padx=10, pady=2)
        
        # Timeout settings
        timeout_label = ttk.Label(connections_frame, text="Timeout (segundos):", font=('Segoe UI', 10, 'bold'))
        timeout_label.grid(row=5, column=0, sticky='w', padx=10, pady=5)
        
        self.timeout_var = tk.IntVar(value=self.current_settings.get('timeout', 30))
        timeout_spin = ttk.Spinbox(
            connections_frame,
            from_=10,
            to=120,
            textvariable=self.timeout_var,
            width=10
        )
        timeout_spin.grid(row=5, column=1, sticky='w', padx=10, pady=5)
    
    def create_advanced_tab(self):
        """Create advanced settings tab"""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Avançado")
        
        # Configure grid
        advanced_frame.grid_columnconfigure(1, weight=1)
        
        # Logging settings
        logging_label = ttk.Label(advanced_frame, text="Logging:", font=('Segoe UI', 10, 'bold'))
        logging_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        # Log level
        log_level_label = ttk.Label(advanced_frame, text="Nível de log:")
        log_level_label.grid(row=1, column=0, sticky='w', padx=20, pady=2)
        
        self.log_level_var = tk.StringVar(value=self.current_settings.get('log_level', 'INFO'))
        log_level_combo = ttk.Combobox(
            advanced_frame,
            textvariable=self.log_level_var,
            values=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            state='readonly',
            width=15
        )
        log_level_combo.grid(row=1, column=1, sticky='w', padx=10, pady=2)
        
        # Enable file logging
        self.file_logging_var = tk.BooleanVar(value=self.current_settings.get('file_logging', True))
        file_logging_check = ttk.Checkbutton(
            advanced_frame,
            text="Log em arquivo",
            variable=self.file_logging_var
        )
        file_logging_check.grid(row=2, column=0, columnspan=2, sticky='w', padx=20, pady=2)
        
        # Cache settings
        cache_label = ttk.Label(advanced_frame, text="Cache:", font=('Segoe UI', 10, 'bold'))
        cache_label.grid(row=3, column=0, sticky='w', padx=10, pady=5)
        
        # Enable cache
        self.cache_enabled_var = tk.BooleanVar(value=self.current_settings.get('cache_enabled', True))
        cache_check = ttk.Checkbutton(
            advanced_frame,
            text="Habilitar cache",
            variable=self.cache_enabled_var
        )
        cache_check.grid(row=4, column=0, columnspan=2, sticky='w', padx=20, pady=2)
        
        # Cache TTL
        cache_ttl_label = ttk.Label(advanced_frame, text="TTL do cache (segundos):")
        cache_ttl_label.grid(row=5, column=0, sticky='w', padx=20, pady=2)
        
        self.cache_ttl_var = tk.IntVar(value=self.current_settings.get('cache_ttl', 300))
        cache_ttl_spin = ttk.Spinbox(
            advanced_frame,
            from_=60,
            to=3600,
            textvariable=self.cache_ttl_var,
            width=10
        )
        cache_ttl_spin.grid(row=5, column=1, sticky='w', padx=10, pady=2)
        
        # Performance settings
        perf_label = ttk.Label(advanced_frame, text="Performance:", font=('Segoe UI', 10, 'bold'))
        perf_label.grid(row=6, column=0, sticky='w', padx=10, pady=5)
        
        # Max concurrent requests
        max_requests_label = ttk.Label(advanced_frame, text="Máx. requisições simultâneas:")
        max_requests_label.grid(row=7, column=0, sticky='w', padx=20, pady=2)
        
        self.max_requests_var = tk.IntVar(value=self.current_settings.get('max_concurrent_requests', 5))
        max_requests_spin = ttk.Spinbox(
            advanced_frame,
            from_=1,
            to=20,
            textvariable=self.max_requests_var,
            width=10
        )
        max_requests_spin.grid(row=7, column=1, sticky='w', padx=10, pady=2)
    
    def create_buttons(self):
        """Create dialog buttons"""
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        button_frame.grid_columnconfigure(3, weight=1)
        
        # Apply button
        self.apply_button = ttk.Button(
            button_frame,
            text="Aplicar",
            style='Primary.TButton',
            command=self.apply_settings
        )
        self.apply_button.grid(row=0, column=0, padx=(0, 5))
        
        # Cancel button
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.cancel_settings
        )
        self.cancel_button.grid(row=0, column=1, padx=5)
        
        # OK button
        self.ok_button = ttk.Button(
            button_frame,
            text="OK",
            style='Success.TButton',
            command=self.ok_settings
        )
        self.ok_button.grid(row=0, column=2, padx=5)
    
    def load_current_settings(self):
        """Load current settings into UI"""
        # This is handled by the individual tab creation methods
        pass
    
    def apply_settings(self):
        """Apply current settings"""
        try:
            # Collect settings from UI
            settings = {
                # Appearance
                'theme': self.theme_var.get(),
                'font_family': self.font_var.get(),
                'font_size': self.font_size_var.get(),
                'window_width': self.width_var.get(),
                'window_height': self.height_var.get(),
                
                # Chat
                'chat_history_limit': self.history_limit_var.get(),
                'auto_scroll': self.auto_scroll_var.get(),
                'show_timestamps': self.show_timestamps_var.get(),
                'group_messages': self.group_messages_var.get(),
                
                # Connections
                'azure_devops_org': self.org_var.get(),
                'azure_devops_project': self.project_var.get(),
                'default_llm_provider': self.provider_var.get(),
                'timeout': self.timeout_var.get(),
                
                # Advanced
                'log_level': self.log_level_var.get(),
                'file_logging': self.file_logging_var.get(),
                'cache_enabled': self.cache_enabled_var.get(),
                'cache_ttl': self.cache_ttl_var.get(),
                'max_concurrent_requests': self.max_requests_var.get()
            }
            
            # Apply settings
            self.current_settings.update(settings)
            self.save_settings()
            
            # Notify app controller
            if hasattr(self.app_controller, 'apply_ui_settings'):
                self.app_controller.apply_ui_settings(settings)
            
            messagebox.showinfo("Configurações", "Configurações aplicadas com sucesso!")
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
            messagebox.showerror("Erro", f"Erro ao aplicar configurações: {e}")
    
    def cancel_settings(self):
        """Cancel settings changes"""
        self.dialog.destroy()
    
    def ok_settings(self):
        """Apply settings and close dialog"""
        self.apply_settings()
        self.dialog.destroy()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        try:
            settings_file = Path("config/ui_settings.json")
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
        
        # Return default settings
        return self.get_default_settings()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            settings_file = Path("config/ui_settings.json")
            settings_file.parent.mkdir(exist_ok=True)
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_settings, f, indent=2, ensure_ascii=False)
            
            logger.info("Settings saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
        return {
            # Appearance
            'theme': 'light',
            'font_family': 'Segoe UI',
            'font_size': 10,
            'window_width': 1400,
            'window_height': 900,
            
            # Chat
            'chat_history_limit': 100,
            'auto_scroll': True,
            'show_timestamps': True,
            'group_messages': False,
            
            # Connections
            'azure_devops_org': '',
            'azure_devops_project': '',
            'default_llm_provider': 'openai',
            'timeout': 30,
            
            # Advanced
            'log_level': 'INFO',
            'file_logging': True,
            'cache_enabled': True,
            'cache_ttl': 300,
            'max_concurrent_requests': 5
        }
    
    def reset_to_defaults(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Resetar", "Deseja resetar todas as configurações para os valores padrão?"):
            self.current_settings = self.get_default_settings()
            self.load_current_settings()
            self.save_settings()
            messagebox.showinfo("Reset", "Configurações resetadas para os valores padrão!") 