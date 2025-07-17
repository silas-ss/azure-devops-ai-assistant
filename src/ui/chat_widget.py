import tkinter as tk
from tkinter import scrolledtext
import ttkbootstrap as tb
from typing import Dict, Any, Optional, Callable
import threading
from datetime import datetime
import re
import markdown2

from src.utils.logger import logger

class ChatWidget(tb.Frame):
    """Chat widget with message history and input"""
    
    def __init__(self, parent, main_window, appearance_settings=None):
        print("DEBUG: Iniciando ChatWidget.__init__")
        super().__init__(parent)
        self.main_window = main_window
        self.app_controller = main_window.app_controller

        # Configurações de aparência
        self.appearance_settings = appearance_settings or {}
        # Message history
        self.messages = []
        self.current_session_id = None
        # UI elements
        self.chat_display = None
        self.input_frame = None
        self.input_entry = None
        self.send_button = None
        # Callbacks
        self.on_message_sent = None
        
        print("DEBUG: Chamando setup_widget")
        self.setup_widget()
        print("DEBUG: Chamando setup_bindings")
        self.setup_bindings()
        self.apply_appearance_settings(self.appearance_settings)
        print("DEBUG: ChatWidget.__init__ concluído")
        logger.info("Chat widget initialized")
    
    def setup_widget(self):
        """Setup chat widget layout"""
        print("DEBUG: Iniciando setup_widget")
        
        # Configure grid with proper weights
        self.grid_rowconfigure(0, weight=1)  # Chat display takes most space
        self.grid_rowconfigure(1, weight=0)  # Input area takes no extra space
        self.grid_columnconfigure(0, weight=1)
        
        # Create chat display
        print("DEBUG: Chamando create_chat_display")
        self.create_chat_display()
        
        # Create input area
        print("DEBUG: Chamando create_input_area")
        self.create_input_area()
        
        # Force update to ensure proper layout
        self.update_idletasks()
        
        print("DEBUG: setup_widget concluído")
        
        # Ensure chat display is visible
        if self.chat_display:
            # Remove these lines as they might be causing the issue
            # self.chat_display.pack_propagate(False)
            # self.chat_display.grid_propagate(False)
            pass
            
        # Add a test message to verify chat is working
        self.add_system_message("Chat inicializado com sucesso!")
        
        # Force final update
        self.after(100, self.force_chat_update)
        self.after(500, self.force_chat_resize)
        
        # Log chat widget configuration
        logger.info(f"Chat widget grid info: {self.grid_info()}")
        if self.chat_display:
            logger.info(f"Chat display pack info: {self.chat_display.pack_info()}")
            logger.info(f"Chat display size: {self.chat_display.winfo_width()}x{self.chat_display.winfo_height()}")
            logger.info(f"Chat display content: {self.chat_display.get('1.0', tk.END)}")
            logger.info(f"Chat display parent: {self.chat_display.master}")
        if self.input_frame:
            logger.info(f"Input frame grid info: {self.input_frame.grid_info()}")
    
    def create_chat_display(self):
        """Create chat display area"""
        print("DEBUG: Iniciando create_chat_display")
        
        # Chat display frame
        print("DEBUG: Criando chat_frame")
        chat_frame = tb.Frame(self)
        chat_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        chat_frame.grid_rowconfigure(0, weight=1)  # Chat text area takes most space
        chat_frame.grid_columnconfigure(0, weight=1)
        print("DEBUG: chat_frame criado e configurado")
        
        # Chat display label
        print("DEBUG: Criando chat_label")
        chat_label = tb.Label(chat_frame, text="💬 Chat", font=('Arial', 12, 'bold'))
        chat_label.pack(anchor='w', pady=(0, 5))
        print("DEBUG: chat_label criado")
        
        # Chat text area - agora usando ScrolledText
        print("DEBUG: Criando chat display real (ScrolledText)")
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Arial', 12),
            height=15,
            width=50,
            bg='white',
            fg='black',
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM)
        print("DEBUG: Chat display real criado")
        
        # Force update to ensure proper layout
        self.chat_display.update_idletasks()
        print("DEBUG: Chat display configurado")
        
        # Configure tags for different message types
        self.chat_display.tag_configure('user', foreground='#2c3e50', font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_configure('assistant', foreground='#27ae60', font=('Segoe UI', 10))
        self.chat_display.tag_configure('system', foreground='#e74c3c', font=('Segoe UI', 10, 'italic'))
        self.chat_display.tag_configure('error', foreground='#e74c3c', font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_configure('timestamp', foreground='#95a5a6', font=('Segoe UI', 8))
        self.chat_display.tag_configure('separator', foreground='#bdc3c7')
    
    def create_input_area(self):
        """Create input area for messages"""
        print("DEBUG: Iniciando create_input_area")
        
        # Input frame
        print("DEBUG: Criando input_frame")
        self.input_frame = tb.Frame(self)
        self.input_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        self.input_frame.grid_columnconfigure(0, weight=1)
        print("DEBUG: input_frame criado")
        
        # Force update to ensure proper layout
        self.input_frame.update_idletasks()
        
        # Input entry - agora usando Entry real
        print("DEBUG: Criando input_entry real (Entry)")
        self.input_entry = tb.Entry(
            self.input_frame,
            font=('Arial', 10)
        )
        self.input_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        print("DEBUG: input_entry real criado")
        
        # Send button
        print("DEBUG: Criando send_button")
        self.send_button = tb.Button(
            self.input_frame,
            text="Enviar",
            bootstyle="primary",
            command=lambda: self.send_message()
        )
        self.send_button.grid(row=0, column=1)
        print("DEBUG: send_button criado")
        
        # Configure entry style
        print("DEBUG: Configurando estilo do entry")
        # The style configuration is removed as per the edit hint.
        print("DEBUG: Estilo configurado")
        
        print("DEBUG: create_input_area concluído")
    
    def setup_bindings(self):
        """Setup input bindings"""
        print("DEBUG: Iniciando setup_bindings")
        
        # Bind Enter key to send message
        print("DEBUG: Configurando bind Enter")
        self.input_entry.bind('<Return>', lambda e: self.send_message())
        
        # Bind Ctrl+Enter for new line
        print("DEBUG: Configurando bind Ctrl+Enter")
        self.input_entry.bind('<Control-Return>', lambda e: self.insert_newline())
        
        # Bind Ctrl+A to select all
        print("DEBUG: Configurando bind Ctrl+A")
        self.input_entry.bind('<Control-a>', lambda e: self.select_all())
        
        # Bind Ctrl+L to clear input
        print("DEBUG: Configurando bind Ctrl+L")
        self.input_entry.bind('<Control-l>', lambda e: self.clear_input())
        
        print("DEBUG: setup_bindings concluído")
    
    def send_message(self, message: Optional[str] = None):
        """Send current message or a provided message"""
        if message is None:
            message = self.input_entry.get().strip()
        if not message:
            return
        # Add user message to display
        self.add_user_message(message)
        # Limpar o campo de entrada após enviar
        self.clear_input()
        # Garantir que o campo de entrada permaneça habilitado e com foco
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus_set()
        # Process message in background
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
    
    def process_message(self, message: str):
        """Process message with AI"""
        try:
            # Update status
            self.main_window.update_status("Processando mensagem...", "info")
            
            # Send to app controller
            response = self.app_controller.process_user_message(message)
            logger.info(f"ChatWidget received response: {response[:100]}...")  # Log response
            
            # Add assistant response
            self.add_assistant_message(response)
            logger.info("Assistant message added to chat display")  # Log success
            
            # Update status
            self.main_window.update_status("Mensagem processada", "success")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.add_error_message(f"Erro ao processar mensagem: {e}")
            self.main_window.update_status("Erro ao processar mensagem", "error")
    
    def add_user_message(self, message: str):
        """Add user message to chat"""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[{timestamp}] Você: {message}\n\n", 'user')
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        self.messages.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.now()
        })
    
    def add_assistant_message(self, message: str):
        """Adiciona mensagem do assistente ao chat, renderizando markdown visualmente"""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.config(state=tk.NORMAL)
        # Converte markdown para HTML
        html = markdown2.markdown(message)
        # Insere timestamp e prefixo
        self.chat_display.insert(tk.END, f"[{timestamp}] Assistente: \n", 'assistant')
        # Faz parsing do HTML e aplica tags visuais
        self.parse_html_to_tk_tags(html)
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        # Garantir que o campo de entrada permaneça habilitado e com foco após resposta
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus_set()
        self.messages.append({
            'role': 'assistant',
            'content': message,
            'timestamp': datetime.now()
        })

    def parse_html_to_tk_tags(self, html: str):
        """Faz parsing básico do HTML gerado pelo markdown e aplica tags no Text"""
        # Importa aqui para evitar dependência global
        from html.parser import HTMLParser
        text_widget = self.chat_display
        class TkMarkdownParser(HTMLParser):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                self.current_tags = []
            def handle_starttag(self, tag, attrs):
                if tag in ('strong', 'b'):
                    self.current_tags.append('bold')
                elif tag in ('em', 'i'):
                    self.current_tags.append('italic')
                elif tag == 'code':
                    self.current_tags.append('code')
                elif tag in ('ul', 'ol'):
                    self.current_tags.append('list')
                elif tag == 'li':
                    self.text_widget.insert(tk.END, '• ', tuple(self.current_tags))
                elif tag in ('h1', 'h2', 'h3'):
                    self.current_tags.append('header')
            def handle_endtag(self, tag):
                if tag in ('strong', 'b', 'em', 'i', 'code', 'ul', 'ol', 'h1', 'h2', 'h3'):
                    if self.current_tags:
                        self.current_tags.pop()
            def handle_data(self, data):
                self.text_widget.insert(tk.END, data, tuple(self.current_tags))
        # Configura tags visuais
        text_widget.tag_configure('bold', font=('Segoe UI', 10, 'bold'))
        text_widget.tag_configure('italic', font=('Segoe UI', 10, 'italic'))
        text_widget.tag_configure('code', font=('Consolas', 10), background='#f4f4f4', foreground='#c0392b')
        text_widget.tag_configure('header', font=('Segoe UI', 12, 'bold'), foreground='#2980b9')
        # Parseia o HTML
        parser = TkMarkdownParser(text_widget)
        parser.feed(html)
    
    def add_system_message(self, message: str):
        """Add system message to chat"""
        print("DEBUG: Iniciando add_system_message")
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[{timestamp}] Sistema: {message}\n\n", 'system')
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        self.messages.append({
            'role': 'system',
            'content': message,
            'timestamp': datetime.now()
        })
        print("DEBUG: add_system_message concluído")
    
    def add_error_message(self, message: str):
        """Add error message to chat"""
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[{timestamp}] Erro: {message}\n\n", 'error')
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        self.messages.append({
            'role': 'error',
            'content': message,
            'timestamp': datetime.now()
        })
    
    def format_markdown(self, text: str) -> str:
        """Basic markdown formatting for chat display"""
        # This is a simple markdown formatter
        # In a real application, you might want to use a proper markdown library
        
        # Bold text
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Italic text
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Code blocks
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        # Headers
        text = re.sub(r'^### (.*?)$', r'\1', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'\1', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.*?)$', r'\1', text, flags=re.MULTILINE)
        
        # Lists
        text = re.sub(r'^- (.*?)$', r'• \1', text, flags=re.MULTILINE)
        
        return text
    
    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.messages.clear()
        logger.info("Chat history cleared")
    
    def clear_input(self):
        """Clear input field"""
        self.input_entry.delete(0, tk.END)
    
    def insert_newline(self):
        """Insert newline in input"""
        current_pos = self.input_entry.index(tk.INSERT)
        self.input_entry.insert(current_pos, '\n')
        return 'break'  # Prevent default behavior
    
    def select_all(self):
        """Select all text in input"""
        self.input_entry.select_range(0, tk.END)
        return 'break'
    
    def get_chat_history(self) -> list:
        """Get chat history"""
        return self.messages.copy()
    
    def set_session_id(self, session_id: str):
        """Set current session ID"""
        self.current_session_id = session_id
    
    def load_chat_history(self, messages: list):
        """Load chat history from session"""
        self.clear_chat()
        
        for message in messages:
            if message['role'] == 'user':
                self.add_user_message(message['content'])
            elif message['role'] == 'assistant':
                self.add_assistant_message(message['content'])
            elif message['role'] == 'system':
                self.add_system_message(message['content'])
            elif message['role'] == 'error':
                self.add_error_message(message['content'])
    
    def export_chat(self, filename: str):
        """Export chat history to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Azure DevOps AI Assistant - Chat History\n")
                f.write("=" * 50 + "\n\n")
                
                for message in self.messages:
                    timestamp = message['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                    role = message['role'].title()
                    content = message['content']
                    
                    f.write(f"[{timestamp}] {role}: {content}\n\n")
            
            logger.info(f"Chat exported to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting chat: {e}")
            return False
    
    def get_message_count(self) -> int:
        """Get total message count"""
        return len(self.messages)
    
    def get_last_message(self) -> Optional[Dict]:
        """Get last message"""
        if self.messages:
            return self.messages[-1]
        return None
    
    def force_chat_update(self):
        """Force chat display to update and be visible"""
        try:
            if self.chat_display:
                # Force update
                self.chat_display.update_idletasks()
                
                # Force redraw
                self.chat_display.update()
                
                # Force resize if needed
                if self.chat_display.winfo_width() < 100 or self.chat_display.winfo_height() < 100:
                    self.chat_display.configure(width=50, height=20)
                    self.chat_display.update_idletasks()
                
                logger.info(f"Chat display forced update - Size: {self.chat_display.winfo_width()}x{self.chat_display.winfo_height()}")
                logger.info(f"Chat display text: {self.chat_display.get('1.0', tk.END)}")
                logger.info(f"Chat display background: {self.chat_display.cget('bg')}")
                logger.info(f"Chat display foreground: {self.chat_display.cget('fg')}")
        except Exception as e:
            logger.error(f"Error forcing chat update: {e}")
    
    def force_chat_resize(self):
        """Force chat display to resize properly"""
        try:
            if self.chat_display:
                # Get parent frame size
                parent = self.chat_display.master
                parent_width = parent.winfo_width()
                parent_height = parent.winfo_height()
                
                logger.info(f"Parent frame size: {parent_width}x{parent_height}")
                
                # Force minimum size
                if parent_width > 0 and parent_height > 0:
                    # Calculate reasonable size
                    chat_width = max(50, parent_width - 20)
                    chat_height = max(20, parent_height - 100)
                    
                    self.chat_display.configure(width=chat_width, height=chat_height)
                    self.chat_display.update_idletasks()
                    
                    logger.info(f"Chat display resized to: {self.chat_display.winfo_width()}x{self.chat_display.winfo_height()}")
                else:
                    logger.warning("Parent frame has zero size, cannot resize chat")
        except Exception as e:
            logger.error(f"Error forcing chat resize: {e}")
    
    def add_visible_test_message(self):
        """Add a highly visible test message"""
        try:
            if self.chat_display:
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.insert(tk.END, '\n\n' + '=' * 50 + '\n', 'system')
                self.chat_display.config(state=tk.DISABLED)
                self.chat_display.update()
                logger.info("Teste de visibilidade adicionado ao chat")
        except Exception as e:
            logger.error(f"Erro ao adicionar teste de visibilidade: {e}") 

    def apply_appearance_settings(self, settings):
        """Aplica configurações de aparência no chat (tema, fonte, cor)"""
        if not settings:
            return
        # Tema
        theme = settings.get('theme', 'claro')
        if theme == 'escuro':
            bg = '#23272e'
            fg = '#f0f0f0'
        else:
            bg = 'white'
            fg = 'black'
        if self.chat_display:
            self.chat_display.config(bg=bg, fg=fg, insertbackground=fg)
        # Fonte
        font_family = settings.get('chat_font', 'Segoe UI')
        font_size = int(settings.get('chat_font_size', 12))
        if self.chat_display:
            self.chat_display.config(font=(font_family, font_size))
        if self.input_entry:
            self.input_entry.config(font=(font_family, max(font_size-2, 8)))
        # Cor de destaque (mensagens do assistente)
        highlight = settings.get('highlight_color', '#27ae60')
        if self.chat_display:
            self.chat_display.tag_configure('assistant', foreground=highlight, font=(font_family, font_size))
        # Atualizar tags de markdown
        if self.chat_display:
            self.chat_display.tag_configure('bold', font=(font_family, font_size, 'bold'))
            self.chat_display.tag_configure('italic', font=(font_family, font_size, 'italic'))
            self.chat_display.tag_configure('code', font=('Consolas', font_size), background='#f4f4f4', foreground='#c0392b')
            self.chat_display.tag_configure('header', font=(font_family, font_size+2, 'bold'), foreground='#2980b9') 