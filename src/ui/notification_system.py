import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List, Callable
import threading
import time
from datetime import datetime
from enum import Enum

from src.utils.logger import logger

class NotificationType(Enum):
    """Notification types"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class Notification:
    """Individual notification"""
    
    def __init__(self, message: str, notification_type: NotificationType, 
                 title: str = "", duration: int = 5000, action: Optional[Callable] = None):
        self.message = message
        self.type = notification_type
        self.title = title
        self.duration = duration
        self.action = action
        self.timestamp = datetime.now()
        self.id = f"{self.timestamp.strftime('%Y%m%d%H%M%S%f')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'message': self.message,
            'type': self.type.value,
            'title': self.title,
            'timestamp': self.timestamp.isoformat(),
            'has_action': self.action is not None
        }

class NotificationSystem:
    """System for managing notifications"""
    
    def __init__(self, parent):
        self.parent = parent
        self.notifications: List[Notification] = []
        self.notification_widgets: Dict[str, tk.Toplevel] = {}
        
        # Notification settings
        self.max_notifications = 5
        self.default_duration = 5000  # 5 seconds
        self.notification_width = 350
        self.notification_height = 100
        
        # Position tracking
        self.current_position = 0
        self.notification_spacing = 10
        
        logger.info("Notification system initialized")
    
    def show_notification(self, message: str, notification_type: NotificationType = NotificationType.INFO,
                         title: str = "", duration: Optional[int] = None, 
                         action: Optional[Callable] = None):
        """Show a notification"""
        try:
            # Create notification
            notification = Notification(
                message=message,
                notification_type=notification_type,
                title=title,
                duration=duration or self.default_duration,
                action=action
            )
            
            # Add to list
            self.notifications.append(notification)
            
            # Limit notifications
            if len(self.notifications) > self.max_notifications:
                self.notifications.pop(0)
            
            # Create notification widget
            self.create_notification_widget(notification)
            
            # Auto-remove after duration
            if duration:
                threading.Timer(duration / 1000.0, 
                              lambda: self.remove_notification(notification.id)).start()
            
            logger.info(f"Notification shown: {message} ({notification_type.value})")
            
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
    
    def create_notification_widget(self, notification: Notification):
        """Create notification widget"""
        try:
            # Create toplevel window
            widget = tk.Toplevel(self.parent)
            widget.withdraw()  # Hide initially
            
            # Configure window
            widget.title("Notificação")
            widget.geometry(f"{self.notification_width}x{self.notification_height}")
            widget.resizable(False, False)
            widget.overrideredirect(True)  # Remove window decorations
            
            # Position window
            self.position_notification(widget)
            
            # Configure widget
            self.setup_notification_widget(widget, notification)
            
            # Store widget
            self.notification_widgets[notification.id] = widget
            
            # Show widget without stealing focus
            widget.deiconify()
            widget.lift()
            # Don't force focus to avoid stealing focus from main window
            # widget.focus_force()
            
        except Exception as e:
            logger.error(f"Error creating notification widget: {e}")
    
    def setup_notification_widget(self, widget: tk.Toplevel, notification: Notification):
        """Setup notification widget content"""
        # Configure grid
        widget.grid_rowconfigure(0, weight=1)
        widget.grid_columnconfigure(1, weight=1)
        
        # Get colors and icons
        colors = self.get_notification_colors(notification.type)
        icon = self.get_notification_icon(notification.type)
        
        # Icon label
        icon_label = ttk.Label(
            widget,
            text=icon,
            font=('Segoe UI', 16),
            foreground=colors['icon']
        )
        icon_label.grid(row=0, column=0, padx=10, pady=10, sticky='n')
        
        # Content frame
        content_frame = ttk.Frame(widget)
        content_frame.grid(row=0, column=1, sticky='nsew', padx=(0, 10), pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Title label
        if notification.title:
            title_label = ttk.Label(
                content_frame,
                text=notification.title,
                font=('Segoe UI', 10, 'bold'),
                foreground=colors['text']
            )
            title_label.grid(row=0, column=0, sticky='w', pady=(0, 2))
        
        # Message label
        message_label = ttk.Label(
            content_frame,
            text=notification.message,
            font=('Segoe UI', 9),
            foreground=colors['text'],
            wraplength=self.notification_width - 80
        )
        message_label.grid(row=1, column=0, sticky='w')
        
        # Close button
        close_button = ttk.Button(
            widget,
            text="✕",
            style='Close.TButton',
            command=lambda: self.remove_notification(notification.id)
        )
        close_button.grid(row=0, column=2, padx=(0, 5), pady=5, sticky='ne')
        
        # Action button (if provided)
        if notification.action:
            action_button = ttk.Button(
                content_frame,
                text="Ver",
                style='Action.TButton',
                command=lambda: self.execute_action(notification)
            )
            action_button.grid(row=2, column=0, sticky='w', pady=(5, 0))
        
        # Bind click events
        widget.bind('<Button-1>', lambda e: self.on_notification_click(notification))
        message_label.bind('<Button-1>', lambda e: self.on_notification_click(notification))
        
        # Bind close events
        widget.bind('<Escape>', lambda e: self.remove_notification(notification.id))
        widget.bind('<Button-3>', lambda e: self.remove_notification(notification.id))
    
    def position_notification(self, widget: tk.Toplevel):
        """Position notification widget"""
        # Get screen dimensions
        screen_width = widget.winfo_screenwidth()
        screen_height = widget.winfo_screenheight()
        
        # Calculate position (top-right corner)
        x = screen_width - self.notification_width - 20
        y = 20 + (self.current_position * (self.notification_height + self.notification_spacing))
        
        # Wrap to top if too many notifications
        if y + self.notification_height > screen_height - 100:
            self.current_position = 0
            y = 20
        
        widget.geometry(f"{self.notification_width}x{self.notification_height}+{x}+{y}")
        self.current_position += 1
    
    def get_notification_colors(self, notification_type: NotificationType) -> Dict[str, str]:
        """Get colors for notification type"""
        colors = {
            NotificationType.INFO: {
                'background': '#3498db',
                'text': '#ffffff',
                'icon': '#ffffff'
            },
            NotificationType.SUCCESS: {
                'background': '#27ae60',
                'text': '#ffffff',
                'icon': '#ffffff'
            },
            NotificationType.WARNING: {
                'background': '#f39c12',
                'text': '#ffffff',
                'icon': '#ffffff'
            },
            NotificationType.ERROR: {
                'background': '#e74c3c',
                'text': '#ffffff',
                'icon': '#ffffff'
            }
        }
        return colors.get(notification_type, colors[NotificationType.INFO])
    
    def get_notification_icon(self, notification_type: NotificationType) -> str:
        """Get icon for notification type"""
        icons = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌"
        }
        return icons.get(notification_type, "ℹ️")
    
    def remove_notification(self, notification_id: str):
        """Remove notification by ID"""
        try:
            # Remove from list
            self.notifications = [n for n in self.notifications if n.id != notification_id]
            
            # Destroy widget
            if notification_id in self.notification_widgets:
                widget = self.notification_widgets[notification_id]
                widget.destroy()
                del self.notification_widgets[notification_id]
            
            # Reposition remaining notifications
            self.reposition_notifications()
            
            logger.debug(f"Notification removed: {notification_id}")
            
        except Exception as e:
            logger.error(f"Error removing notification: {e}")
    
    def reposition_notifications(self):
        """Reposition all visible notifications"""
        try:
            current_pos = 0
            for notification in self.notifications:
                if notification.id in self.notification_widgets:
                    widget = self.notification_widgets[notification.id]
                    
                    # Calculate new position
                    screen_width = widget.winfo_screenwidth()
                    x = screen_width - self.notification_width - 20
                    y = 20 + (current_pos * (self.notification_height + self.notification_spacing))
                    
                    widget.geometry(f"{self.notification_width}x{self.notification_height}+{x}+{y}")
                    current_pos += 1
            
            self.current_position = current_pos
            
        except Exception as e:
            logger.error(f"Error repositioning notifications: {e}")
    
    def on_notification_click(self, notification: Notification):
        """Handle notification click"""
        if notification.action:
            self.execute_action(notification)
        else:
            self.remove_notification(notification.id)
    
    def execute_action(self, notification: Notification):
        """Execute notification action"""
        try:
            if notification.action:
                notification.action()
            self.remove_notification(notification.id)
        except Exception as e:
            logger.error(f"Error executing notification action: {e}")
    
    def clear_all_notifications(self):
        """Clear all notifications"""
        try:
            # Remove all notifications
            notification_ids = list(self.notification_widgets.keys())
            for notification_id in notification_ids:
                self.remove_notification(notification_id)
            
            self.notifications.clear()
            self.current_position = 0
            
            logger.info("All notifications cleared")
            
        except Exception as e:
            logger.error(f"Error clearing notifications: {e}")
    
    def get_notification_count(self) -> int:
        """Get current notification count"""
        return len(self.notifications)
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications as dictionaries"""
        return [notification.to_dict() for notification in self.notifications]

class NotificationManager:
    """Manager for application-wide notifications"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.notification_system = NotificationSystem(main_window.root)
        
        logger.info("Notification manager initialized")
    
    def show_info(self, message: str, title: str = "", duration: Optional[int] = None):
        """Show info notification"""
        self.notification_system.show_notification(
            message=message,
            notification_type=NotificationType.INFO,
            title=title,
            duration=duration
        )
    
    def show_success(self, message: str, title: str = "", duration: Optional[int] = None):
        """Show success notification"""
        self.notification_system.show_notification(
            message=message,
            notification_type=NotificationType.SUCCESS,
            title=title,
            duration=duration
        )
    
    def show_warning(self, message: str, title: str = "", duration: Optional[int] = None):
        """Show warning notification"""
        self.notification_system.show_notification(
            message=message,
            notification_type=NotificationType.WARNING,
            title=title,
            duration=duration
        )
    
    def show_error(self, message: str, title: str = "", duration: Optional[int] = None):
        """Show error notification"""
        self.notification_system.show_notification(
            message=message,
            notification_type=NotificationType.ERROR,
            title=title,
            duration=duration
        )
    
    def show_connection_status(self, azure_devops_connected: bool, llm_connected: bool):
        """Show connection status notification"""
        if azure_devops_connected and llm_connected:
            self.show_success("Todas as conexões ativas", "Status das Conexões")
        elif azure_devops_connected or llm_connected:
            self.show_warning("Conexão parcial", "Status das Conexões")
        else:
            self.show_error("Nenhuma conexão ativa", "Status das Conexões")
    
    def show_work_item_created(self, work_item_id: str, title: str):
        """Show work item created notification"""
        self.show_success(
            f"Work Item #{work_item_id} criado com sucesso",
            "Work Item Criado"
        )
    
    def show_work_item_updated(self, work_item_id: str, title: str):
        """Show work item updated notification"""
        self.show_info(
            f"Work Item #{work_item_id} atualizado",
            "Work Item Atualizado"
        )
    
    def show_search_results(self, count: int, query: str):
        """Show search results notification"""
        if count > 0:
            self.show_success(
                f"Encontrados {count} resultados para '{query}'",
                "Resultados da Busca"
            )
        else:
            self.show_warning(
                f"Nenhum resultado encontrado para '{query}'",
                "Resultados da Busca"
            )
    
    def show_llm_response(self, response_time: float):
        """Show LLM response notification"""
        self.show_info(
            f"Resposta recebida em {response_time:.1f}s",
            "LLM"
        )
    
    def show_error_with_details(self, error_message: str, details: str = ""):
        """Show error notification with details"""
        if details:
            message = f"{error_message}\n\nDetalhes: {details}"
        else:
            message = error_message
        
        self.show_error(message, "Erro")
    
    def clear_all(self):
        """Clear all notifications"""
        self.notification_system.clear_all_notifications()
    
    def get_notification_count(self) -> int:
        """Get notification count"""
        return self.notification_system.get_notification_count()
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications"""
        return self.notification_system.get_notifications() 