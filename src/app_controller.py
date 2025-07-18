import tkinter as tk
from typing import Dict, Any, Optional, List
import threading
import time
import datetime
import json
from pathlib import Path

from src.services.azure_devops_service import AzureDevOpsService
from src.services.llm.llm_factory import LLMFactory
from src.services.chat.conversation_manager import ConversationManager
from src.services.chat.command_parser import CommandParser, CommandLLMParser, CommandType
from src.services.chat.prompt_engineer import PromptEngineer
from src.services.chat.command_validator import CommandValidator
from src.services.chat.response_templates import ResponseTemplateEngine
from src.ui.main_window import MainWindow
from src.ui.notification_system import NotificationManager, NotificationType
from src.utils.logger import logger
from src.utils.config_manager import ConfigManager
from config.settings import settings
from src.services.llm.base_provider import LLMRequest
from src.services.chat.response_templates import TemplateContext

class AppController:
    """Main application controller"""
    
    def __init__(self):
        # Initialize components
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        # Initialize services
        self.azure_devops_service = None
        self.llm_factory = LLMFactory()
        self.llm_provider = None
        
        # Initialize chat components
        self.conversation_manager = ConversationManager()
        self.command_parser = CommandParser()
        self.prompt_engineer = PromptEngineer()
        self.command_validator = CommandValidator()
        self.response_templates = ResponseTemplateEngine()
        
        # Initialize UI
        self.main_window = None
        self.notification_manager = None
        
        # Application state
        self.is_initialized = False
        self.session_data = {}

        self.datetime = datetime.datetime
        
        logger.info("App controller initialized")
    
    def initialize_conversation_session(self):
        """Create a new conversation session and store the session_id"""
        # Ajuste esses valores conforme sua lógica real
        user_id = "default_user"
        organization = "default_org"
        project = "default_project"
        session_id = self.conversation_manager.create_session(user_id, organization, project)
        self.session_data['session_id'] = session_id

    def initialize(self):
        """Initialize the application"""
        try:
            print("DEBUG: Iniciando método initialize()")
            logger.info("Initializing application...")
            
            # Initialize Azure DevOps service
            print("DEBUG: Inicializando Azure DevOps service")
            self.initialize_azure_devops()
            
            # Initialize LLM provider
            print("DEBUG: Inicializando LLM provider")
            self.initialize_llm_provider()
            
            # Initialize UI
            print("DEBUG: Inicializando UI")
            self.initialize_ui()
            
            # Test connections
            print("DEBUG: Testando conexões")
            self.test_connections()
            
            self.is_initialized = True
            print("DEBUG: Inicializando sessão de conversa")
            self.initialize_conversation_session()
            print("DEBUG: Aplicação inicializada com sucesso")
            logger.info("Application initialized successfully")
            
        except Exception as e:
            print(f"DEBUG: Erro no método initialize(): {e}")
            logger.error(f"Error initializing application: {e}")
            raise
    
    def initialize_azure_devops(self):
        """Initialize Azure DevOps service"""
        try:
            # Get Azure DevOps configuration from settings
            azure_config = settings.azure_devops
            if not azure_config.organization or not azure_config.project or not azure_config.project_id or not azure_config.personal_access_token:
                logger.warning("Azure DevOps não está configurado corretamente nas variáveis de ambiente")
                return
            # Create Azure DevOps service
            self.azure_devops_service = AzureDevOpsService()
            logger.info("Azure DevOps service initialized")
        except Exception as e:
            logger.error(f"Error initializing Azure DevOps: {e}")
            raise
    
    def initialize_llm_provider(self):
        """Initialize LLM provider"""
        try:
            # Get default provider name and config from settings
            default_provider = settings.app.default_llm_provider
            provider_config = settings.get_provider_config(default_provider)
            if not provider_config:
                raise ValueError(f"Provider config for '{default_provider}' not found in settings.")
            
            # Convert dataclass to dict for compatibility with LLMFactory
            config_dict = provider_config.__dict__
            
            # Create LLM provider
            self.llm_provider = self.llm_factory.create_provider(
                provider_name=default_provider,
                config=config_dict
            )
            logger.info(f"LLM provider initialized: {default_provider}")
        except Exception as e:
            logger.error(f"Error initializing LLM provider: {e}")
            raise
    
    def initialize_ui(self):
        """Initialize UI components"""
        try:
            print("DEBUG: Criando MainWindow")
            # Create main window
            self.main_window = MainWindow(self)
            print("DEBUG: MainWindow criada com sucesso")
            
            print("DEBUG: Criando NotificationManager")
            # Create notification manager
            self.notification_manager = NotificationManager(self.main_window)
            print("DEBUG: NotificationManager criado com sucesso")
            
            logger.info("UI components initialized")
            print("DEBUG: Componentes UI inicializados com sucesso")
            
        except Exception as e:
            print(f"DEBUG: Erro ao inicializar UI: {e}")
            logger.error(f"Error initializing UI: {e}")
            raise
    
    def test_connections(self):
        """Test all connections"""
        try:
            logger.info("Testing connections...")
            
            # Test Azure DevOps connection
            azure_connected = self.test_azure_devops_connection()
            
            # Test LLM connection
            llm_connected = self.test_llm_connection()
            
            # Show connection status
            if self.notification_manager:
                self.notification_manager.show_connection_status(azure_connected, llm_connected)
            
            # Update status bar
            if self.main_window and hasattr(self.main_window, 'status_bar'):
                self.main_window.status_bar.update_connection_status(azure_connected, llm_connected)
            
            logger.info(f"Connection test completed - Azure DevOps: {azure_connected}, LLM: {llm_connected}")
            
        except Exception as e:
            logger.error(f"Error testing connections: {e}")
    
    def test_azure_devops_connection(self) -> bool:
        """Test Azure DevOps connection"""
        try:
            if not self.azure_devops_service:
                return False
            
            # Test connection by getting project info
            project_info = self.azure_devops_service.get_project_info()
            return project_info is not None
            
        except Exception as e:
            logger.error(f"Azure DevOps connection test failed: {e}")
            return False
    
    def test_llm_connection(self) -> bool:
        """Test LLM connection"""
        try:
            if not self.llm_provider:
                return False
            
            # Test connection with a simple prompt
            request = LLMRequest(
                messages=[{"role": "user", "content": "Hello"}],
                model=self.llm_provider.model,
                max_tokens=10,
                temperature=0.7,
                stream=False
            )
            response = self.llm_provider.generate(request)
            return response is not None and hasattr(response, "content") and len(response.content) > 0
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False
    
    def parse_command(self, user_text: str):
        """Parse o comando do usuário usando LLM primeiro, depois fallback para parser tradicional"""
        llm_parser = CommandLLMParser()
        parsed = llm_parser.parse(user_text)
        if parsed.command_type != CommandType.UNKNOWN and parsed.confidence > 0.7:
            return parsed
        # Fallback para parser tradicional
        parser = CommandParser()
        return parser.parse(user_text)
    
    def process_analytics_question(self, parsed_command, user_message: str) -> str:
        """Processa perguntas analíticas sobre work items e gera resposta natural com LLM"""
        # Exemplo: contar bugs abertos
        work_item_type = parsed_command.parameters.get('tipo') or parsed_command.parameters.get('work_item_type') or 'Bug'
        state = parsed_command.parameters.get('estado') or parsed_command.parameters.get('state') or 'Active'
        # Buscar work items
        items = self.azure_devops_service.get_work_items(work_item_types=[work_item_type], state=state)
        quantidade = len(items)
        # Montar contexto para o LLM gerar resposta
        prompt = f"""
Pergunta do usuário: {user_message}

Dados do Azure DevOps:
- Tipo: {work_item_type}
- Estado: {state}
- Quantidade encontrada: {quantidade}

Gere uma resposta natural, clara e objetiva para o usuário, explicando o resultado.
"""
        # Chamar LLM para gerar resposta
        from src.services.llm.llm_factory import get_llm_provider
        from src.services.llm.base_provider import LLMRequest
        llm = get_llm_provider()
        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            model=getattr(llm, 'model', None),
            max_tokens=128,
            temperature=0.0,
            stream=False
        )
        resposta = llm.generate(request).content
        return resposta
    
    def process_message(self, message: str) -> str:
        """Processa a mensagem do usuário usando o fluxo agent/function-calling"""
        llm_parser = CommandLLMParser()
        parsed = llm_parser.parse(message)
        # Se for resposta direta do LLM
        if 'direct_response' in parsed:
            return parsed['direct_response']
        # Se o LLM pediu execução de função
        if 'function' in parsed:
            func_name = parsed['function']
            params = parsed.get('parameters', {})
            print("DEBUG params:", params)
            print("DEBUG func_name:", func_name)
            # Mapear nome da função para função Python real
            if func_name == 'listar_work_items':
                # Mapear sinônimos de datas
                if 'data_modificacao' in params:
                    params['modificado_em'] = params.pop('data_modificacao')
                if 'data_criacao' in params:
                    params['criado_em'] = params.pop('data_criacao')
                filtros_aceitos = ['titulo', 'descricao', 'prioridade', 'criado_em', 'modificado_em', 'atribuido_para', 'tipo']
                filtros_presentes = {k: v for k, v in params.items() if k in filtros_aceitos}
                
                # Conversão de datas relativas
                for campo_data in ['criado_em', 'modificado_em']:
                    if campo_data in filtros_presentes:
                        valor = filtros_presentes[campo_data]
                        if isinstance(valor, str):
                            if valor.lower() == 'hoje':
                                filtros_presentes[campo_data] = self.datetime.now().strftime('%Y-%m-%d')
                            elif valor.lower() == 'ontem':
                                filtros_presentes[campo_data] = (self.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                
                if filtros_presentes:
                    items = self.azure_devops_service.search_work_items_advanced(filtros_presentes)
                    dados = [item.__dict__ for item in items]
                else:
                    items = self.azure_devops_service.get_work_items(
                        work_item_types=[params.get('tipo')] if params.get('tipo') else None,
                        state=params.get('estado'),
                        assigned_to=params.get('atribuido_para'),
                        top=params.get('limite', 100)
                    )
                    dados = [item.__dict__ for item in items]
            elif func_name == 'listar_boards':
                boards = self.azure_devops_service.get_boards()
                dados = [board.__dict__ for board in boards]
            elif func_name == 'buscar_work_item':
                # Mapear sinônimos de datas
                if 'data_modificacao' in params:
                    params['modificado_em'] = params.pop('data_modificacao')
                if 'data_criacao' in params:
                    params['criado_em'] = params.pop('data_criacao')
                filtros_aceitos = ['titulo', 'descricao', 'prioridade', 'criado_em', 'modificado_em', 'atribuido_para', 'tipo']
                filtros_presentes = {k: v for k, v in params.items() if k in filtros_aceitos}
                # Conversão de datas relativas
                for campo_data in ['criado_em', 'modificado_em']:
                    if campo_data in filtros_presentes:
                        valor = filtros_presentes[campo_data]
                        if isinstance(valor, str):
                            if valor.lower() == 'hoje':
                                filtros_presentes[campo_data] = self.datetime.now().strftime('%Y-%m-%d')
                            elif valor.lower() == 'ontem':
                                filtros_presentes[campo_data] = (self.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                if filtros_presentes:
                    items = self.azure_devops_service.search_work_items_advanced(filtros_presentes)
                    dados = [item.__dict__ for item in items]
                elif 'id' in params:
                    work_item = self.azure_devops_service.get_work_item_by_id(params['id'])
                    dados = [work_item.__dict__] if work_item else []
                elif 'termo' in params:
                    items = self.azure_devops_service.search_work_items(params['termo'])
                    dados = [item.__dict__ for item in items]
                elif 'termo_busca' in params:
                    items = self.azure_devops_service.search_work_items(params['termo_busca'])
                    dados = [item.__dict__ for item in items]
                elif 'titulo' in params:
                    items = self.azure_devops_service.search_work_items(params['titulo'])
                    dados = [item.__dict__ for item in items]
                else:
                    dados = []
            elif func_name == 'mostrar_work_item':
                if 'id' in params:
                    work_item = self.azure_devops_service.get_work_item_by_id(params['id'])
                    dados = [work_item.__dict__] if work_item else []
                elif 'work_item_id' in params:
                    work_item = self.azure_devops_service.get_work_item_by_id(params['work_item_id'])
                    dados = [work_item.__dict__] if work_item else []
                else:
                    dados = []
            else:
                dados = []
            
            
            # Enviar dados + pergunta original para o LLM gerar resposta final
            from src.services.llm.llm_factory import get_llm_provider
            from src.services.llm.base_provider import LLMRequest
            llm = get_llm_provider()
            prompt = f"Pergunta do usuário: {message}\n\nDados retornados: {dados}\n\nGere uma resposta natural, clara e objetiva para o usuário, explicando o resultado."
            request = LLMRequest(
                messages=[{"role": "user", "content": prompt}],
                model=getattr(llm, 'model', None),
                max_tokens=256,
                temperature=0.0,
                stream=False
            )
            resposta = llm.generate(request).content
            return resposta
        # fallback
        return "Desculpe, não consegui entender sua solicitação. Tente reformular a pergunta."
    
    def process_user_message(self, message: str) -> str:
        """Processa a mensagem do usuário e retorna a resposta usando apenas o fluxo agent/function-calling"""
        return self.process_message(message)
    
    def execute_command(self, parsed_command) -> str:
        """Execute parsed command"""
        try:
            command_type = parsed_command.command_type
            logger.info(f"Executing command type: {command_type}")  # Debug log
            
            if command_type == CommandType.LIST_BOARDS:
                return self.execute_list_boards()
            elif command_type == CommandType.LIST_WORK_ITEMS:
                return self.execute_list_work_items(parsed_command)
            elif command_type == CommandType.GET_WORK_ITEM:
                return self.execute_get_work_item(parsed_command)
            elif command_type == CommandType.SEARCH_WORK_ITEMS:
                return self.execute_search_work_items(parsed_command)
            elif command_type == CommandType.GET_BOARD:
                return self.execute_get_board(parsed_command)
            elif command_type == CommandType.HELP:
                return self.execute_help()
            else:
                logger.warning(f"Unknown command type: {command_type}")
                return self.response_templates.get_unknown_command_response()
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return f"Erro ao executar comando: {str(e)}"
    
    def execute_list_boards(self) -> str:
        """Execute list boards command"""
        try:
            if not self.azure_devops_service:
                return "Serviço Azure DevOps não está configurado."
            boards = self.azure_devops_service.get_boards()
            context = TemplateContext(
                user_name="Usuário",
                organization="Org",
                project="Projeto",
                current_time=self.datetime.now(),
                command_type=CommandType.LIST_BOARDS,
                parameters={}
            )
            return self.response_templates.create_boards_response(boards, context)
        except Exception as e:
            logger.error(f"Error listing boards: {e}")
            return f"Erro ao listar boards: {str(e)}"
    
    def execute_list_work_items(self, parsed_command) -> str:
        """Execute list work items command"""
        try:
            if not self.azure_devops_service:
                return "Serviço Azure DevOps não está configurado."
            # Get work item type filter
            work_item_type = parsed_command.parameters.get('work_item_type')
            work_items = self.azure_devops_service.get_work_items(work_item_types=[work_item_type] if work_item_type else None)
            if not work_items:
                return f"Nenhum work item encontrado{f' do tipo {work_item_type}' if work_item_type else ''}."
            # Format response
            response = "## 📝 Work Items encontrados\n\n"
            for item in work_items:
                response += f"- **ID:** {item.id} | **Título:** {item.title} | **Estado:** {item.state}\n"
            return response
        except Exception as e:
            logger.error(f"Error listing work items: {e}")
            return f"Erro ao listar work items: {e}"
    
    def execute_get_work_item(self, parsed_command: Dict[str, Any]) -> str:
        """Execute get work item command"""
        try:
            if not self.azure_devops_service:
                return "Serviço Azure DevOps não está configurado."
            
            work_item_id = parsed_command.get('work_item_id')
            if not work_item_id:
                return "ID do work item não especificado."
            
            work_item = self.azure_devops_service.get_work_item_by_id(work_item_id)
            
            if not work_item:
                return f"Work item #{work_item_id} não encontrado."
            
            # Format response
            response = f"## 📋 Work Item #{work_item_id}\n\n"
            response += f"**Título:** {work_item.title}\n"
            response += f"**Tipo:** {work_item.work_item_type}\n"
            response += f"**Estado:** {work_item.state}\n"
            response += f"**Responsável:** {work_item.assigned_to or 'N/A'}\n"
            response += f"**Data de criação:** {work_item.created_date.strftime('%d/%m/%Y %H:%M') if work_item.created_date else 'N/A'}\n"
            
            if work_item.description:
                response += f"\n**Descrição:**\n{work_item.description}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting work item: {e}")
            return f"Erro ao obter work item: {str(e)}"
    
    def execute_search_work_items(self, parsed_command: Dict[str, Any]) -> str:
        """Execute search work items command"""
        try:
            if not self.azure_devops_service:
                return "Serviço Azure DevOps não está configurado."
            
            search_term = parsed_command.get('search_terms')
            if not search_term:
                return "Termo de busca não especificado."
            
            work_items = self.azure_devops_service.search_work_items(search_term)
            
            if not work_items:
                return f"Nenhum work item encontrado para '{search_term}'."
            
            # Format response
            response = f"## 🔍 Resultados da Busca: '{search_term}'\n\n"
            
            for item in work_items[:10]:  # Limit to 10 items
                response += f"• **#{item.id}** - {item.title} ({item.state})\n"
            
            if len(work_items) > 10:
                response += f"\n... e mais {len(work_items) - 10} itens."
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching work items: {e}")
            return f"Erro ao buscar work items: {str(e)}"
    
    def execute_get_board(self, parsed_command) -> str:
        """Executa o comando para mostrar detalhes de um board pelo nome ou id"""
        try:
            if not self.azure_devops_service:
                return "Serviço Azure DevOps não está configurado."
            board_name = parsed_command.parameters.get('board_name')
            if not board_name:
                return "Nome do board não especificado."
            # Buscar todos os boards e procurar pelo nome (case-insensitive)
            boards = self.azure_devops_service.get_boards()
            board = next((b for b in boards if b.name.lower() == board_name.lower() or b.id == board_name), None)
            if not board:
                return f"Board '{board_name}' não encontrado."
            # Montar resposta detalhada
            response = f"## 📋 Detalhes do Board\n\n"
            response += f"**Nome:** {board.name}\n"
            response += f"**Tipo:** {board.board_type}\n"
            response += f"**ID:** {board.id}\n"
            response += f"**URL:** {board.url}\n"
            return response
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes do board: {e}")
            return f"Erro ao buscar detalhes do board: {str(e)}"
    
    def execute_help(self) -> str:
        """Execute help command"""
        context = TemplateContext(
            user_name="Usuário",
            organization="Org",
            project="Projeto",
            current_time=self.datetime.now(),
            command_type=CommandType.HELP,
            parameters={}
        )
        return self.response_templates.create_help_message(context)
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information"""
        try:
            if not self.azure_devops_service:
                return {
                    'organization': 'Não configurado',
                    'project': 'Não configurado',
                    'team': 'Não configurado',
                    'url': 'Não configurado'
                }
            
            project_info = self.azure_devops_service.get_project_info()
            return project_info or {
                'organization': 'Não configurado',
                'project': 'Não configurado',
                'team': 'Não configurado',
                'url': 'Não configurado'
            }
            
        except Exception as e:
            logger.error(f"Error getting project info: {e}")
            return {
                'organization': 'Erro',
                'project': 'Erro',
                'team': 'Erro',
                'url': 'Erro'
            }
    
    def apply_ui_settings(self, settings: Dict[str, Any]):
        """Apply UI settings"""
        try:
            # Apply theme
            if 'theme' in settings:
                self.apply_theme(settings['theme'])
            
            # Apply font settings
            if 'font_family' in settings or 'font_size' in settings:
                self.apply_font_settings(settings)
            
            # Apply window size
            if 'window_width' in settings and 'window_height' in settings:
                self.apply_window_size(settings['window_width'], settings['window_height'])
            
            logger.info("UI settings applied")
            
        except Exception as e:
            logger.error(f"Error applying UI settings: {e}")
    
    def apply_theme(self, theme: str):
        """Apply theme to application"""
        # This would be implemented based on the UI framework
        logger.info(f"Theme applied: {theme}")
    
    def apply_font_settings(self, settings: Dict[str, Any]):
        """Apply font settings"""
        font_family = settings.get('font_family', 'Segoe UI')
        font_size = settings.get('font_size', 10)
        
        # Apply font settings to UI components
        logger.info(f"Font settings applied: {font_family} {font_size}")
    
    def apply_window_size(self, width: int, height: int):
        """Apply window size"""
        if self.main_window and hasattr(self.main_window, 'root'):
            self.main_window.root.geometry(f"{width}x{height}")
            logger.info(f"Window size applied: {width}x{height}")
    
    def save_session(self):
        """Save session data"""
        try:
            session_data = {
                'conversation_history': self.conversation_manager.get_conversation_history(),
                'timestamp': self.datetime.now().isoformat()
            }
            
            session_file = Path("config/session.json")
            session_file.parent.mkdir(exist_ok=True)
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.info("Session saved")
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def load_session(self):
        """Load session data"""
        try:
            session_file = Path("config/session.json")
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Load conversation history
                if 'conversation_history' in session_data:
                    self.conversation_manager.load_conversation_history(
                        session_data['conversation_history']
                    )
                
                logger.info("Session loaded")
                
        except Exception as e:
            logger.error(f"Error loading session: {e}")
    
    def run(self):
        """Run the application"""
        try:
            print("DEBUG: Iniciando AppController.run()")
            
            # Initialize application
            print("DEBUG: Inicializando aplicação")
            self.initialize()
            
            # Load session
            print("DEBUG: Carregando sessão")
            self.load_session()
            
            # Run main window
            print("DEBUG: Executando janela principal")
            if self.main_window:
                print("DEBUG: MainWindow existe, chamando run()")
                self.main_window.run()
            else:
                print("DEBUG: ERRO - MainWindow não existe!")
            
        except Exception as e:
            print(f"DEBUG: Erro no AppController.run(): {e}")
            logger.error(f"Error running application: {e}")
            raise
    
    def quit(self):
        """Quit the application"""
        try:
            # Save session
            self.save_session()
            
            # Cleanup
            if self.main_window:
                self.main_window.root.quit()
            
            logger.info("Application quit")
            
        except Exception as e:
            logger.error(f"Error quitting application: {e}")
    
    def get_status_info(self) -> Dict[str, Any]:
        """Get application status information"""
        return {
            'initialized': self.is_initialized,
            'azure_devops_connected': self.test_azure_devops_connection(),
            'llm_connected': self.test_llm_connection(),
            'conversation_count': len(self.conversation_manager.get_conversation_history()),
            'timestamp': self.datetime.now().isoformat()
        } 