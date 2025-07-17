from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from src.services.azure_devops_service import WorkItem, Board
from src.utils.logger import logger

@dataclass
class ChatContext:
    """Context for chat conversation"""
    conversation_history: List[Dict[str, str]]
    current_user: str
    organization: str
    project: str
    last_command: Optional[str] = None
    last_response: Optional[str] = None

class PromptEngineer:
    """Engineer prompts for Azure DevOps interactions"""
    
    def __init__(self):
        self.system_prompt = self._get_system_prompt()
        self.response_templates = self._get_response_templates()
    
    def _get_system_prompt(self) -> str:
        """Get the base system prompt"""
        return """Você é um assistente especializado em Azure DevOps que ajuda usuários a interagir com boards, work items e projetos.

CAPACIDADES:
- Listar e visualizar boards do projeto
- Buscar e exibir work items (Product Backlog Items, Bugs, Features)
- Mostrar detalhes específicos de work items
- Buscar work items por texto
- Explicar status e campos dos work items

FORMATO DE RESPOSTA:
- Sempre responda em português de forma clara e concisa
- Use formatação markdown quando apropriado
- Para listas de itens, use tabelas ou listas organizadas
- Para work items, mostre informações relevantes como ID, título, status, prioridade, responsável
- Seja útil e forneça contexto quando necessário

CONTEXTO:
- Organização: {organization}
- Projeto: {project}
- Usuário: {user}

INSTRUÇÕES ESPECÍFICAS:
1. Se o usuário pedir para listar boards, mostre todos os boards disponíveis
2. Se o usuário pedir work items, pergunte se quer todos ou algum tipo específico (PBI, Bug, Feature)
3. Para work items, sempre mostre ID, título, tipo, status e responsável
4. Se não souber algo, seja honesto e sugira alternativas
5. Mantenha o tom profissional mas amigável"""
    
    def _get_response_templates(self) -> Dict[str, str]:
        """Get response templates for different scenarios"""
        return {
            'boards_list': """## 📋 Boards Disponíveis

Aqui estão os boards do projeto **{project}**:

{boards_table}

Você pode pedir para ver detalhes de um board específico ou listar work items.""",
            
            'work_items_list': """## 📝 Work Items

{filter_info}

**Total encontrado:** {count} itens

{items_table}

{did_you_know}""",
            
            'work_item_detail': """## 📋 Work Item #{id}

**Título:** {title}
**Tipo:** {type}
**Status:** {state}
**Prioridade:** {priority}
**Responsável:** {assigned_to}
**Criado:** {created_date}
**Modificado:** {changed_date}
**Área:** {area_path}
**Iteração:** {iteration_path}

**Descrição:**
{description}

**Tags:** {tags}

**URL:** {url}""",
            
            'search_results': """## 🔍 Resultados da Busca

**Termo buscado:** "{search_term}"
**Resultados encontrados:** {count}

{results_table}

{did_you_know}""",
            
            'no_results': """## ❌ Nenhum resultado encontrado

Não foram encontrados itens que correspondam aos critérios especificados.

**Sugestões:**
- Verifique se o termo de busca está correto
- Tente termos mais gerais
- Use diferentes palavras-chave
- Verifique se há work items no projeto""",
            
            'error': """## ⚠️ Erro

Ocorreu um erro ao processar sua solicitação:

**Erro:** {error_message}

**Possíveis soluções:**
- Verifique sua conexão com o Azure DevOps
- Confirme se as credenciais estão corretas
- Tente novamente em alguns instantes"""
        }
    
    def create_system_prompt(self, context: ChatContext) -> str:
        """Create system prompt with context"""
        return self.system_prompt.format(
            organization=context.organization,
            project=context.project,
            user=context.current_user
        )
    
    def create_user_prompt(self, command: str, context: ChatContext) -> str:
        """Create user prompt for a command"""
        prompt = f"Comando do usuário: {command}\n\n"
        
        # Add context from previous conversation if relevant
        if context.last_command and context.last_response:
            prompt += f"Comando anterior: {context.last_command}\n"
            prompt += f"Resposta anterior: {context.last_response}\n\n"
        
        prompt += "Por favor, processe este comando e forneça uma resposta útil."
        
        return prompt
    
    def format_boards_response(self, boards: List[Board]) -> str:
        """Format boards list response"""
        if not boards:
            return "Nenhum board encontrado no projeto."
        
        # Create table
        table_rows = []
        for board in boards:
            table_rows.append(f"| {board.name} | {board.board_type} | {board.url} |")
        
        boards_table = "| Nome | Tipo | URL |\n|------|------|-----|\n" + "\n".join(table_rows)
        
        return self.response_templates['boards_list'].format(
            project="Projeto Atual",
            boards_table=boards_table
        )
    
    def format_work_items_response(self, work_items: List[WorkItem], filters: Dict = None) -> str:
        """Format work items list response"""
        if not work_items:
            return "Nenhum work item encontrado."
        
        # Create filter info
        filter_info = ""
        if filters:
            filter_parts = []
            if 'types' in filters:
                filter_parts.append(f"Tipo: {', '.join(filters['types'])}")
            if 'state' in filters:
                filter_parts.append(f"Status: {filters['state']}")
            if 'assigned_to' in filters:
                filter_parts.append(f"Responsável: {filters['assigned_to']}")
            
            if filter_parts:
                filter_info = f"**Filtros aplicados:** {', '.join(filter_parts)}\n\n"
        
        # Create table
        table_rows = []
        for item in work_items:
            assigned_to = item.assigned_to or "Não atribuído"
            table_rows.append(f"| #{item.id} | {item.title[:50]}... | {item.work_item_type} | {item.state} | {assigned_to} |")
        
        items_table = "| ID | Título | Tipo | Status | Responsável |\n|----|--------|------|-------|-------------|\n" + "\n".join(table_rows)
        
        # Add helpful tip
        did_you_know = "\n💡 **Dica:** Use 'mostre item #123' para ver detalhes de um work item específico."
        
        return self.response_templates['work_items_list'].format(
            filter_info=filter_info,
            count=len(work_items),
            items_table=items_table,
            did_you_know=did_you_know
        )
    
    def format_work_item_detail(self, work_item: WorkItem) -> str:
        """Format work item detail response"""
        assigned_to = work_item.assigned_to or "Não atribuído"
        description = work_item.description or "Sem descrição"
        tags = ", ".join(work_item.tags) if work_item.tags else "Nenhuma"
        
        return self.response_templates['work_item_detail'].format(
            id=work_item.id,
            title=work_item.title,
            type=work_item.work_item_type,
            state=work_item.state,
            priority=work_item.priority,
            assigned_to=assigned_to,
            created_date=work_item.created_date.strftime("%d/%m/%Y %H:%M"),
            changed_date=work_item.changed_date.strftime("%d/%m/%Y %H:%M"),
            area_path=work_item.area_path,
            iteration_path=work_item.iteration_path,
            description=description,
            tags=tags,
            url=work_item.url
        )
    
    def format_search_results(self, work_items: List[WorkItem], search_term: str) -> str:
        """Format search results response"""
        if not work_items:
            return self.response_templates['no_results'].format(
                search_term=search_term
            )
        
        # Create table
        table_rows = []
        for item in work_items:
            assigned_to = item.assigned_to or "Não atribuído"
            table_rows.append(f"| #{item.id} | {item.title[:50]}... | {item.work_item_type} | {item.state} | {assigned_to} |")
        
        results_table = "| ID | Título | Tipo | Status | Responsável |\n|----|--------|------|-------|-------------|\n" + "\n".join(table_rows)
        
        # Add helpful tip
        did_you_know = "\n💡 **Dica:** Use 'mostre item #123' para ver detalhes completos de um work item."
        
        return self.response_templates['search_results'].format(
            search_term=search_term,
            count=len(work_items),
            results_table=results_table,
            did_you_know=did_you_know
        )
    
    def format_error_response(self, error_message: str) -> str:
        """Format error response"""
        return self.response_templates['error'].format(
            error_message=error_message
        )
    
    def create_help_response(self) -> str:
        """Create help response"""
        return """## 🤖 Assistente Azure DevOps - Ajuda

### 📋 Comandos Disponíveis

**Boards:**
- "Liste os boards" - Mostra todos os boards do projeto
- "Mostre os quadros disponíveis" - Lista boards disponíveis

**Work Items:**
- "Liste os work items" - Mostra todos os work items
- "Mostre os bugs" - Lista apenas bugs
- "Liste as features" - Lista apenas features
- "Mostre os PBIs" - Lista Product Backlog Items

**Work Item Específico:**
- "Mostre o item #123" - Exibe detalhes do work item 123
- "Get work item 456" - Mostra work item 456

**Busca:**
- "Busque itens com 'login'" - Procura work items contendo 'login'
- "Search bugs about 'performance'" - Busca bugs sobre performance

**Filtros:**
- "Mostre bugs ativos" - Lista bugs com status 'Active'
- "Liste itens atribuídos para João" - Filtra por responsável

### 💡 Dicas
- Use comandos em português ou inglês
- Para ver detalhes completos, use o ID do work item
- Use aspas para termos de busca com espaços
- Digite "ajuda" a qualquer momento para ver esta lista

### 🔧 Problemas?
Se algo não funcionar, verifique:
- Sua conexão com o Azure DevOps
- Se as credenciais estão configuradas corretamente
- Se você tem permissão para acessar o projeto"""
    
    def create_context_prompt(self, context: ChatContext) -> str:
        """Create context-aware prompt"""
        prompt = self.create_system_prompt(context)
        
        # Add conversation history if available
        if context.conversation_history:
            prompt += "\n\n**Histórico da conversa:**\n"
            for message in context.conversation_history[-5:]:  # Last 5 messages
                role = message.get('role', 'user')
                content = message.get('content', '')
                prompt += f"{role.upper()}: {content}\n"
        
        return prompt 