import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional
import threading

from src.utils.logger import logger

class CommandSuggestions(ttk.Frame):
    """Widget for command suggestions"""
    
    def __init__(self, parent, on_suggestion_click: Callable[[str], None]):
        super().__init__(parent)
        self.on_suggestion_click = on_suggestion_click
        
        # Suggestions data
        self.suggestions = []
        self.filtered_suggestions = []
        self.current_filter = ""
        
        # UI elements
        self.suggestions_frame = None
        self.suggestion_buttons = []
        
        self.setup_widget()
        
        logger.info("Command suggestions widget initialized")
    
    def setup_widget(self):
        """Setup suggestions widget"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create suggestions frame
        self.suggestions_frame = ttk.Frame(self)
        self.suggestions_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Configure frame grid
        for i in range(3):  # 3 columns
            self.suggestions_frame.grid_columnconfigure(i, weight=1)
    
    def set_suggestions(self, suggestions: List[str]):
        """Set available suggestions"""
        self.suggestions = suggestions
        self.filtered_suggestions = suggestions
        self.update_display()
    
    def filter_suggestions(self, filter_text: str):
        """Filter suggestions based on input"""
        self.current_filter = filter_text.lower()
        
        if not self.current_filter:
            self.filtered_suggestions = self.suggestions
        else:
            self.filtered_suggestions = [
                suggestion for suggestion in self.suggestions
                if self.current_filter in suggestion.lower()
            ]
        
        self.update_display()
    
    def update_display(self):
        """Update suggestions display"""
        # Clear existing buttons
        for button in self.suggestion_buttons:
            button.destroy()
        self.suggestion_buttons.clear()
        
        # Clear frame
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        
        # Add new suggestion buttons
        for i, suggestion in enumerate(self.filtered_suggestions[:9]):  # Max 9 suggestions
            row = i // 3
            col = i % 3
            
            button = ttk.Button(
                self.suggestions_frame,
                text=suggestion,
                style='Suggestion.TButton',
                command=lambda s=suggestion: self.on_suggestion_click(s)
            )
            button.grid(row=row, column=col, sticky='ew', padx=2, pady=2)
            self.suggestion_buttons.append(button)
    
    def get_suggestions(self) -> List[str]:
        """Get current suggestions"""
        return self.filtered_suggestions.copy()
    
    def clear_suggestions(self):
        """Clear all suggestions"""
        self.suggestions = []
        self.filtered_suggestions = []
        self.update_display()

class QuickCommands(ttk.Frame):
    """Widget for quick command buttons"""
    
    def __init__(self, parent, on_command_click: Callable[[str], None]):
        super().__init__(parent)
        self.on_command_click = on_command_click
        
        # Quick commands
        self.quick_commands = [
            ("📋 Boards", "Liste os boards"),
            ("📝 Work Items", "Liste os work items"),
            ("🐛 Bugs", "Mostre os bugs"),
            ("✨ Features", "Liste as features"),
            ("🔍 Buscar", "Busque itens com 'termo'"),
            ("❓ Ajuda", "Ajuda")
        ]
        
        self.setup_widget()
        
        logger.info("Quick commands widget initialized")
    
    def setup_widget(self):
        """Setup quick commands widget"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create commands frame
        commands_frame = ttk.Frame(self)
        commands_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Configure frame grid
        for i in range(3):  # 3 columns
            commands_frame.grid_columnconfigure(i, weight=1)
        
        # Create quick command buttons
        for i, (label, command) in enumerate(self.quick_commands):
            row = i // 3
            col = i % 3
            
            button = ttk.Button(
                commands_frame,
                text=label,
                style='QuickCommand.TButton',
                command=lambda cmd=command: self.on_command_click(cmd)
            )
            button.grid(row=row, column=col, sticky='ew', padx=2, pady=2)
    
    def add_quick_command(self, label: str, command: str):
        """Add a new quick command"""
        self.quick_commands.append((label, command))
        self.setup_widget()  # Recreate widget
    
    def remove_quick_command(self, label: str):
        """Remove a quick command"""
        self.quick_commands = [(l, c) for l, c in self.quick_commands if l != label]
        self.setup_widget()  # Recreate widget

class CommandHistory(ttk.Frame):
    """Widget for command history"""
    
    def __init__(self, parent, on_history_click: Callable[[str], None]):
        super().__init__(parent)
        self.on_history_click = on_history_click
        
        # Command history
        self.command_history = []
        self.max_history = 20
        
        # UI elements
        self.history_listbox = None
        
        self.setup_widget()
        
        logger.info("Command history widget initialized")
    
    def setup_widget(self):
        """Setup command history widget"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create history frame
        history_frame = ttk.Frame(self)
        history_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        
        # History label
        history_label = ttk.Label(history_frame, text="📜 Histórico de Comandos", style='Subtitle.TLabel')
        history_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # History listbox
        self.history_listbox = tk.Listbox(
            history_frame,
            font=('Segoe UI', 9),
            selectmode=tk.SINGLE,
            height=8
        )
        self.history_listbox.grid(row=1, column=0, sticky='nsew')
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        scrollbar.grid(row=1, column=1, sticky='ns')
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        
        # Bind double-click event
        self.history_listbox.bind('<Double-Button-1>', self.on_history_double_click)
    
    def add_command(self, command: str):
        """Add command to history"""
        # Remove if already exists
        if command in self.command_history:
            self.command_history.remove(command)
        
        # Add to beginning
        self.command_history.insert(0, command)
        
        # Limit history size
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[:self.max_history]
        
        self.update_display()
    
    def update_display(self):
        """Update history display"""
        self.history_listbox.delete(0, tk.END)
        
        for command in self.command_history:
            self.history_listbox.insert(tk.END, command)
    
    def on_history_double_click(self, event):
        """Handle double-click on history item"""
        selection = self.history_listbox.curselection()
        if selection:
            command = self.history_listbox.get(selection[0])
            self.on_history_click(command)
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
        self.update_display()
    
    def get_history(self) -> List[str]:
        """Get command history"""
        return self.command_history.copy()

class CommandInput(ttk.Frame):
    """Enhanced command input widget"""
    
    def __init__(self, parent, on_send: Callable[[str], None]):
        super().__init__(parent)
        self.on_send = on_send
        
        # UI elements
        self.input_entry = None
        self.send_button = None
        self.suggestions_widget = None
        
        self.setup_widget()
        
        logger.info("Command input widget initialized")
    
    def setup_widget(self):
        """Setup command input widget"""
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Input frame
        input_frame = ttk.Frame(self)
        input_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Input entry
        self.input_entry = ttk.Entry(
            input_frame,
            font=('Segoe UI', 10),
            style='Command.TEntry'
        )
        self.input_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        # Send button
        self.send_button = ttk.Button(
            input_frame,
            text="Enviar",
            style='Primary.TButton',
            command=self.send_command
        )
        self.send_button.grid(row=0, column=1)
        
        # Suggestions widget
        self.suggestions_widget = CommandSuggestions(self, self.on_suggestion_click)
        self.suggestions_widget.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        # Setup bindings
        self.setup_bindings()
        
        # Configure entry style
        style = ttk.Style()
        style.configure('Command.TEntry', padding=(10, 5))
    
    def setup_bindings(self):
        """Setup input bindings"""
        # Bind Enter key
        self.input_entry.bind('<Return>', lambda e: self.send_command())
        
        # Bind key events for suggestions
        self.input_entry.bind('<KeyRelease>', self.on_key_release)
        
        # Bind Ctrl+Enter for new line
        self.input_entry.bind('<Control-Return>', lambda e: self.insert_newline())
        
        # Bind Ctrl+A to select all
        self.input_entry.bind('<Control-a>', lambda e: self.select_all())
    
    def send_command(self):
        """Send current command"""
        command = self.input_entry.get().strip()
        if command:
            self.on_send(command)
            self.input_entry.delete(0, tk.END)
    
    def on_key_release(self, event):
        """Handle key release for suggestions"""
        current_text = self.input_entry.get()
        
        # Update suggestions based on input
        if hasattr(self, 'suggestions_widget'):
            self.suggestions_widget.filter_suggestions(current_text)
    
    def on_suggestion_click(self, suggestion: str):
        """Handle suggestion click"""
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, suggestion)
        self.input_entry.focus()
    
    def insert_newline(self):
        """Insert newline in input"""
        current_pos = self.input_entry.index(tk.INSERT)
        self.input_entry.insert(current_pos, '\n')
        return 'break'
    
    def select_all(self):
        """Select all text in input"""
        self.input_entry.select_range(0, tk.END)
        return 'break'
    
    def set_suggestions(self, suggestions: List[str]):
        """Set command suggestions"""
        if self.suggestions_widget:
            self.suggestions_widget.set_suggestions(suggestions)
    
    def clear_input(self):
        """Clear input field"""
        self.input_entry.delete(0, tk.END)
    
    def get_input_text(self) -> str:
        """Get current input text"""
        return self.input_entry.get()
    
    def set_input_text(self, text: str):
        """Set input text"""
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, text)
    
    def focus_input(self):
        """Focus on input field"""
        self.input_entry.focus() 