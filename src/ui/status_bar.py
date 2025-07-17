import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
from datetime import datetime
import threading

from src.utils.logger import logger

class StatusBar(ttk.Frame):
    """Status bar with connection indicators and system info"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Status variables
        self.azure_devops_status = "disconnected"
        self.llm_status = "disconnected"
        self.current_status = "Pronto"
        self.status_type = "info"
        
        # UI elements
        self.status_label = None
        self.azure_devops_indicator = None
        self.llm_indicator = None
        self.time_label = None
        self.progress_bar = None
        
        # Status colors
        self.status_colors = {
            'info': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'error': '#e74c3c'
        }
        
        # Status icons
        self.status_icons = {
            'connected': '🟢',
            'disconnected': '🔴',
            'connecting': '🟡',
            'error': '🔴'
        }
        
        self.setup_widget()
        self.start_time_update()
        
        logger.info("Status bar initialized")
    
    def setup_widget(self):
        """Setup status bar layout"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)  # Status label takes most space
        
        # Azure DevOps status indicator
        self.azure_devops_indicator = ttk.Label(
            self,
            text=f"{self.status_icons['disconnected']} Azure DevOps",
            font=('Segoe UI', 9),
            foreground=self.status_colors['error']
        )
        self.azure_devops_indicator.grid(row=0, column=0, padx=(5, 10), pady=2)
        
        # LLM status indicator
        self.llm_indicator = ttk.Label(
            self,
            text=f"{self.status_icons['disconnected']} LLM",
            font=('Segoe UI', 9),
            foreground=self.status_colors['error']
        )
        self.llm_indicator.grid(row=0, column=2, padx=(0, 10), pady=2)
        
        # Main status label
        self.status_label = ttk.Label(
            self,
            text=self.current_status,
            font=('Segoe UI', 9),
            foreground=self.status_colors[self.status_type]
        )
        self.status_label.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        
        # Time label
        self.time_label = ttk.Label(
            self,
            text="",
            font=('Segoe UI', 9),
            foreground='#95a5a6'
        )
        self.time_label.grid(row=0, column=3, padx=(0, 5), pady=2)
        
        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(
            self,
            mode='indeterminate',
            length=100
        )
        self.progress_bar.grid(row=0, column=4, padx=(0, 5), pady=2)
        self.progress_bar.grid_remove()  # Hidden by default
    
    def set_azure_devops_status(self, status: str, message: str = ""):
        """Set Azure DevOps connection status"""
        self.azure_devops_status = status
        
        # Update indicator
        icon = self.status_icons.get(status, self.status_icons['error'])
        color = self.get_status_color(status)
        
        self.azure_devops_indicator.config(
            text=f"{icon} Azure DevOps",
            foreground=color
        )
        
        # Update main status if needed
        if message:
            self.set_status(message, self.get_status_type(status))
        
        logger.info(f"Azure DevOps status: {status} - {message}")
    
    def set_llm_status(self, status: str, message: str = ""):
        """Set LLM connection status"""
        self.llm_status = status
        
        # Update indicator
        icon = self.status_icons.get(status, self.status_icons['error'])
        color = self.get_status_color(status)
        
        self.llm_indicator.config(
            text=f"{icon} LLM",
            foreground=color
        )
        
        # Update main status if needed
        if message:
            self.set_status(message, self.get_status_type(status))
        
        logger.info(f"LLM status: {status} - {message}")
    
    def set_status(self, message: str, status_type: str = "info"):
        """Set main status message"""
        self.current_status = message
        self.status_type = status_type
        
        # Update label
        color = self.status_colors.get(status_type, self.status_colors['info'])
        self.status_label.config(
            text=message,
            foreground=color
        )
        
        logger.debug(f"Status: {message} ({status_type})")
    
    def get_status_color(self, status: str) -> str:
        """Get color for status"""
        color_map = {
            'connected': self.status_colors['success'],
            'disconnected': self.status_colors['error'],
            'connecting': self.status_colors['warning'],
            'error': self.status_colors['error']
        }
        return color_map.get(status, self.status_colors['error'])
    
    def get_status_type(self, status: str) -> str:
        """Get status type for main status"""
        type_map = {
            'connected': 'success',
            'disconnected': 'error',
            'connecting': 'warning',
            'error': 'error'
        }
        return type_map.get(status, 'info')
    
    def show_progress(self, show: bool = True):
        """Show or hide progress bar"""
        if show:
            self.progress_bar.grid()
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
    
    def start_time_update(self):
        """Start time update thread"""
        def update_time():
            while True:
                try:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    self.time_label.config(text=current_time)
                    self.after(1000, update_time)  # Update every second
                    break
                except Exception as e:
                    logger.error(f"Error updating time: {e}")
                    break
        
        # Start time update
        self.after(1000, update_time)
    
    def show_connection_test(self):
        """Show connection test in progress"""
        self.show_progress(True)
        self.set_status("Testando conexões...", "warning")
    
    def hide_connection_test(self):
        """Hide connection test progress"""
        self.show_progress(False)
        self.set_status("Pronto", "info")
    
    def update_connection_status(self, azure_devops_connected: bool, llm_connected: bool):
        """Update connection status based on test results"""
        # Update Azure DevOps status
        if azure_devops_connected:
            self.set_azure_devops_status('connected', "Azure DevOps conectado")
        else:
            self.set_azure_devops_status('error', "Azure DevOps desconectado")
        
        # Update LLM status
        if llm_connected:
            self.set_llm_status('connected', "LLM conectado")
        else:
            self.set_llm_status('error', "LLM desconectado")
        
        # Update main status
        if azure_devops_connected and llm_connected:
            self.set_status("Todas as conexões ativas", "success")
        elif azure_devops_connected or llm_connected:
            self.set_status("Conexão parcial", "warning")
        else:
            self.set_status("Nenhuma conexão ativa", "error")
    
    def show_error(self, error_message: str):
        """Show error in status bar"""
        self.set_status(f"Erro: {error_message}", "error")
    
    def show_success(self, message: str):
        """Show success message in status bar"""
        self.set_status(message, "success")
    
    def show_warning(self, message: str):
        """Show warning message in status bar"""
        self.set_status(message, "warning")
    
    def show_info(self, message: str):
        """Show info message in status bar"""
        self.set_status(message, "info")
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get current status information"""
        return {
            'azure_devops_status': self.azure_devops_status,
            'llm_status': self.llm_status,
            'current_status': self.current_status,
            'status_type': self.status_type,
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_status(self):
        """Reset status to default"""
        self.set_azure_devops_status('disconnected')
        self.set_llm_status('disconnected')
        self.set_status("Pronto", "info")
        self.show_progress(False)

class ConnectionIndicator(ttk.Frame):
    """Individual connection indicator widget"""
    
    def __init__(self, parent, name: str, on_click: Optional[callable] = None):
        super().__init__(parent)
        self.name = name
        self.on_click = on_click
        self.status = "disconnected"
        
        # UI elements
        self.indicator_label = None
        self.status_label = None
        
        self.setup_widget()
    
    def setup_widget(self):
        """Setup indicator widget"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Indicator label
        self.indicator_label = ttk.Label(
            self,
            text="🔴",
            font=('Segoe UI', 12)
        )
        self.indicator_label.grid(row=0, column=0, padx=2)
        
        # Status label
        self.status_label = ttk.Label(
            self,
            text=self.name,
            font=('Segoe UI', 9)
        )
        self.status_label.grid(row=0, column=1, padx=2)
        
        # Bind click event if callback provided
        if self.on_click:
            self.indicator_label.bind('<Button-1>', lambda e: self.on_click())
            self.status_label.bind('<Button-1>', lambda e: self.on_click())
    
    def set_status(self, status: str, message: str = ""):
        """Set connection status"""
        self.status = status
        
        # Update indicator
        icons = {
            'connected': '🟢',
            'disconnected': '🔴',
            'connecting': '🟡',
            'error': '🔴'
        }
        
        colors = {
            'connected': '#27ae60',
            'disconnected': '#e74c3c',
            'connecting': '#f39c12',
            'error': '#e74c3c'
        }
        
        icon = icons.get(status, icons['error'])
        color = colors.get(status, colors['error'])
        
        self.indicator_label.config(text=icon)
        self.status_label.config(
            text=message if message else self.name,
            foreground=color
        )
    
    def get_status(self) -> str:
        """Get current status"""
        return self.status 