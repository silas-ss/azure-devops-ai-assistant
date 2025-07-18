import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import logger
from src.services.llm.llm_factory import get_llm_provider
from src.services.llm.base_provider import LLMRequest

class CommandType(Enum):
    """Types of commands that can be parsed"""
    LIST_BOARDS = "list_boards"
    LIST_WORK_ITEMS = "list_work_items"
    GET_WORK_ITEM = "get_work_item"
    SEARCH_WORK_ITEMS = "search_work_items"
    GET_BOARD = "get_board"
    HELP = "help"
    UNKNOWN = "unknown"

@dataclass
class ParsedCommand:
    """Parsed command with extracted information"""
    command_type: CommandType
    parameters: Dict[str, Any]
    confidence: float
    original_text: str

class CommandParser:
    """Parser for natural language commands"""
    
    def __init__(self):
        # Define patterns for different command types
        self.patterns = {
            CommandType.LIST_BOARDS: [
                r"(?:list|show|get|display)\s+(?:all\s+)?(?:boards?|kanban)",
                r"(?:quais|quais são|mostre|liste)\s+(?:os\s+)?(?:boards?|quadros?)",
                r"(?:boards?|quadros?)\s+(?:disponíveis|existentes)"
            ],
            
            CommandType.LIST_WORK_ITEMS: [
                r"(?:list|show|get|display)\s+(?:all\s+)?(?:work\s+items?|backlog\s+items?|tasks?)",
                r"(?:list|show|get|display)\s+(?:bugs?|features?|pbi|product\s+backlog\s+items?)",
                r"(?:quais|quais são|mostre|liste|listar|exibir|exiba|mostrar|mostra|me mostre|me liste)\s+(?:os\s+)?(?:itens?|tarefas?|bugs?|features?|work\s*items?|backlog\s*items?)",
                r"(?:backlog|itens?|work\s*items?)\s+(?:disponíveis|existentes)",
                r"(?:mostrar|exibir|exiba|exibir|mostra|me mostre|me liste)\s+(?:os\s+)?(?:work\s*items?|itens?|tarefas?)"
            ],
            
            CommandType.GET_WORK_ITEM: [
                r"(?:get|show|display|view)\s+(?:work\s+item|item|task)\s+(?:#?(\d+)|(\d+))",
                r"(?:mostre|veja|exiba)\s+(?:o\s+)?(?:item|tarefa)\s+(?:#?(\d+)|(\d+))",
                r"(?:item|tarefa)\s+(?:#?(\d+)|(\d+))"
            ],
            
            CommandType.SEARCH_WORK_ITEMS: [
                r"(?:search|find|look\s+for)\s+(?:work\s+items?|items?|tasks?)\s+(?:with|containing|about)\s+(.+)",
                r"(?:busque|procure|encontre)\s+(?:itens?|tarefas?)\s+(?:com|sobre|relacionados\s+a)\s+(.+)",
                r"(?:search|find)\s+(.+)"
            ],
            
            CommandType.GET_BOARD: [
                r"(?:get|show|display|view)\s+(?:board|kanban)\s+(.+)",
                r"(?:mostre|veja|exiba)\s+(?:o\s+)?(?:board|quadro)\s+(.+)",
                r"(?:board|quadro)\s+(.+)"
            ],
            
            CommandType.HELP: [
                r"(?:help|ajuda|socorro)",
                r"(?:what\s+can\s+you\s+do|o\s+que\s+você\s+pode\s+fazer)",
                r"(?:commands?|comandos?)"
            ]
        }
        
        # Define parameter extractors
        self.parameter_extractors = {
            CommandType.GET_WORK_ITEM: self._extract_work_item_id,
            CommandType.SEARCH_WORK_ITEMS: self._extract_search_terms,
            CommandType.GET_BOARD: self._extract_board_name,
            CommandType.LIST_WORK_ITEMS: self._extract_work_item_filters
        }
    
    def parse(self, text: str) -> ParsedCommand:
        """Parse natural language text into a command"""
        text = text.strip().lower()
        
        # Try to match patterns
        for command_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Extract parameters
                    parameters = {}
                    if command_type in self.parameter_extractors:
                        parameters = self.parameter_extractors[command_type](text, match)
                    
                    # Calculate confidence based on pattern match
                    confidence = self._calculate_confidence(text, pattern, match)
                    
                    logger.debug(f"Parsed command: {command_type.value} with confidence {confidence}")
                    
                    return ParsedCommand(
                        command_type=command_type,
                        parameters=parameters,
                        confidence=confidence,
                        original_text=text
                    )
        
        # No pattern matched
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            parameters={},
            confidence=0.0,
            original_text=text
        )
    
    def _extract_work_item_id(self, text: str, match) -> Dict[str, Any]:
        """Extract work item ID from text"""
        # Look for numbers in the text
        numbers = re.findall(r'\d+', text)
        if numbers:
            return {'work_item_id': int(numbers[0])}
        return {}
    
    def _extract_search_terms(self, text: str, match) -> Dict[str, Any]:
        """Extract search terms from text"""
        # Extract the search terms from the match
        if match.groups():
            search_terms = match.group(1).strip()
            return {'search_terms': search_terms}
        
        # Fallback: extract words after search keywords
        search_keywords = ['search', 'find', 'busque', 'procure', 'encontre']
        for keyword in search_keywords:
            if keyword in text:
                parts = text.split(keyword, 1)
                if len(parts) > 1:
                    search_terms = parts[1].strip()
                    return {'search_terms': search_terms}
        
        return {}
    
    def _extract_board_name(self, text: str, match) -> Dict[str, Any]:
        """Extract board name from text"""
        if match.groups():
            board_name = match.group(1).strip()
            return {'board_name': board_name}
        return {}
    
    def _extract_work_item_filters(self, text: str, match) -> Dict[str, Any]:
        """Extract filters for work items"""
        filters = {}
        
        # Extract work item types
        if 'bug' in text:
            filters['types'] = ['Bug']
        elif 'feature' in text:
            filters['types'] = ['Feature']
        elif 'pbi' in text or 'product backlog item' in text:
            filters['types'] = ['Product Backlog Item']
        
        # Extract state filters
        state_patterns = {
            'new': 'New',
            'active': 'Active',
            'resolved': 'Resolved',
            'closed': 'Closed',
            'removed': 'Removed'
        }
        
        for state_keyword, state_value in state_patterns.items():
            if state_keyword in text:
                filters['state'] = state_value
                break
        
        # Extract assigned to filter
        assigned_pattern = r'(?:assigned\s+to|atribuído\s+para)\s+([a-zA-Z\s]+)'
        assigned_match = re.search(assigned_pattern, text, re.IGNORECASE)
        if assigned_match:
            filters['assigned_to'] = assigned_match.group(1).strip()
        
        return filters
    
    def _calculate_confidence(self, text: str, pattern: str, match) -> float:
        """Calculate confidence score for a pattern match"""
        # Base confidence
        confidence = 0.5
        
        # Boost confidence for exact matches
        if match.group(0).lower() == text.lower():
            confidence += 0.3
        
        # Boost confidence for longer matches
        match_length = len(match.group(0))
        text_length = len(text)
        if text_length > 0:
            coverage = match_length / text_length
            confidence += coverage * 0.2
        
        # Boost confidence for specific keywords
        specific_keywords = ['board', 'work item', 'bug', 'feature', 'search', 'find']
        for keyword in specific_keywords:
            if keyword in text:
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_suggestions(self, text: str) -> List[str]:
        """Get command suggestions based on partial input"""
        suggestions = []
        
        if 'board' in text.lower():
            suggestions.extend([
                "List all boards",
                "Show boards",
                "Get board details"
            ])
        
        if 'item' in text.lower() or 'work' in text.lower():
            suggestions.extend([
                "List work items",
                "Show bugs",
                "Get work item #123",
                "Search work items"
            ])
        
        if 'search' in text.lower() or 'find' in text.lower():
            suggestions.extend([
                "Search work items with 'login'",
                "Find bugs about 'performance'"
            ])
        
        if not suggestions:
            suggestions = [
                "List all boards",
                "List work items",
                "Get work item #123",
                "Search work items",
                "Help"
            ]
        
        return suggestions[:5]  # Limit to 5 suggestions 

class CommandLLMParser:
    """Parser de comandos usando LLM para identificar intenção e parâmetros"""
    def __init__(self, provider_name=None):
        self.llm = get_llm_provider(provider_name)
        self.comandos = [
            {"nome": "listar_work_items", "descricao": "Lista todos os work items do projeto."},
            {"nome": "mostrar_board", "descricao": "Mostra detalhes de um board."},
            {"nome": "buscar_work_item", "descricao": "Busca work items por termo."},
            {"nome": "mostrar_work_item", "descricao": "Mostra detalhes de um work item pelo ID."},
            {"nome": "help", "descricao": "Mostra ajuda sobre os comandos."}
        ]

    def parse(self, text: str) -> dict:
        prompt = self._build_agent_prompt(text)
        request = LLMRequest(
            messages=[{"role": "user", "content": prompt}],
            model=getattr(self.llm, 'model', None),
            max_tokens=256,
            temperature=0.0,
            stream=False
        )
        resposta = self.llm.generate(request).content
        import json
        try:
            parsed = json.loads(resposta)
            # Esperado: {"function": ..., "parameters": {...}} ou {"direct_response": ...}
            return parsed
        except Exception:
            # fallback: retorna resposta direta
            return {"direct_response": resposta}

    def _build_agent_prompt(self, user_text: str) -> str:
        exemplos = """
Exemplos:
Usuário: "Quais bugs foram modificados hoje?"
Resposta: {"function": "listar_work_items", "parameters": {"tipo": "Bug", "modificado_em": "hoje"}}
Usuário: "Quais work items foram criados ontem?"
Resposta: {"function": "listar_work_items", "parameters": {"criado_em": "ontem"}}
Usuário: "Quais tarefas foram modificadas em 2024-06-01?"
Resposta: {"function": "listar_work_items", "parameters": {"tipo": "Task", "modificado_em": "2024-06-01"}}
Usuário: "Quantos bugs estão abertos?"
Resposta: {"function": "listar_work_items", "parameters": {"tipo": "Bug", "estado": "Active"}}
Usuário: "Quais boards existem?"
Resposta: {"function": "listar_boards", "parameters": {}}
Usuário: "Me mostre todos os quadros"
Resposta: {"function": "listar_boards", "parameters": {}}
Usuário: "Preciso de ajuda"
Resposta: {"direct_response": "Claro! Posso te ajudar a consultar boards, work items, prazos e mais. Pergunte algo!"}
Usuário: "Qual o prazo do próximo item?"
Resposta: {"function": "listar_work_items", "parameters": {"ordenar_por": "prazo", "limite": 1}}
Usuário: "Me explique o que é um board"
Resposta: {"direct_response": "Um board no Azure DevOps é..."}
Usuário: "Liste os bugs do projeto"
Resposta: {"function": "listar_work_items", "parameters": {"tipo": "Bug"}}
Usuário: "Quero saber dos boards"
Resposta: {"function": "listar_boards", "parameters": {}}
Usuário: "Me ajude"
Resposta: {"direct_response": "Posso te ajudar a consultar boards, work items, prazos e mais. Pergunte algo!"}
"""
        comandos_str = "listar_work_items, listar_boards, mostrar_board, buscar_work_item, mostrar_work_item, help"
        prompt = f"""
Você é um assistente de Azure DevOps. Quando precisar consultar dados, responda apenas em JSON:
{{"function": <nome_da_funcao>, "parameters": {{...}}}}
Se não precisar consultar dados, responda apenas em JSON:
{{"direct_response": <resposta_para_o_usuario>}}
Funções disponíveis: {comandos_str}

{exemplos}

Usuário: "{user_text}"
Resposta:
"""
        return prompt 