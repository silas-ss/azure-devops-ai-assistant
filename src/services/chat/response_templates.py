from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.services.azure_devops_service import WorkItem, Board
from src.services.chat.command_parser import CommandType
from src.utils.logger import logger

@dataclass
class TemplateContext:
    """Context for template rendering"""
    user_name: str
    organization: str
    project: str
    current_time: datetime
    command_type: CommandType
    parameters: Dict[str, Any]

class ResponseTemplateEngine:
    """Engine for generating response templates"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load response templates"""
        return {
            'welcome': """## 🤖 Assistente Azure DevOps

Olá **{user_name}**! Bem-vindo ao assistente Azure DevOps.

**Organização:** {organization}
**Projeto:** {project}
**Hora atual:** {current_time}

Estou aqui para ajudá-lo a:
- 📋 Listar e visualizar boards
- 📝 Buscar e exibir work items
- 🔍 Pesquisar itens específicos
- 📊 Mostrar detalhes de work items

Digite **"ajuda"** para ver todos os comandos disponíveis ou comece fazendo uma pergunta!""",
            
            'help': """## 📚 Comandos Disponíveis

### 📋 **Boards**
- `Liste os boards` - Mostra todos os boards do projeto
- `Mostre os quadros disponíveis` - Lista boards disponíveis
- `Get board details` - Detalhes de um board específico

### 📝 **Work Items**
- `Liste os work items` - Mostra todos os work items
- `Mostre os bugs` - Lista apenas bugs
- `Liste as features` - Lista apenas features
- `Mostre os PBIs` - Lista Product Backlog Items

### 🔍 **Work Item Específico**
- `Mostre o item #123` - Exibe detalhes do work item 123
- `Get work item 456` - Mostra work item 456

### 🔎 **Busca**
- `Busque itens com 'login'` - Procura work items contendo 'login'
- `Search bugs about 'performance'` - Busca bugs sobre performance

### 🎯 **Filtros**
- `Mostre bugs ativos` - Lista bugs com status 'Active'
- `Liste itens atribuídos para João` - Filtra por responsável

### 💡 **Dicas**
- Use comandos em português ou inglês
- Para ver detalhes completos, use o ID do work item
- Use aspas para termos de busca com espaços
- Digite `ajuda` a qualquer momento para ver esta lista""",
            
            'boards_list': """## 📋 Boards Disponíveis

Aqui estão os boards do projeto **{project}**:

{boards_table}

**Total:** {count} boards

💡 **Dica:** Use `mostre board [nome]` para ver detalhes de um board específico.""",
            
            'boards_empty': """## 📋 Boards

Nenhum board encontrado no projeto **{project}**.

**Possíveis causas:**
- O projeto não possui boards configurados
- Você não tem permissão para visualizar boards
- Verifique se está conectado ao projeto correto""",
            
            'work_items_list': """## 📝 Work Items

{filter_info}

**Total encontrado:** {count} itens

{items_table}

{summary_info}

💡 **Dica:** Use `mostre item #123` para ver detalhes de um work item específico.""",
            
            'work_items_empty': """## 📝 Work Items

Nenhum work item encontrado.

{filter_info}

**Sugestões:**
- Verifique se há work items no projeto
- Tente remover filtros específicos
- Use `ajuda` para ver exemplos de comandos""",
            
            'work_item_detail': """## 📋 Work Item #{id}

### 📝 **Informações Básicas**
**Título:** {title}
**Tipo:** {type}
**Status:** {state}
**Prioridade:** {priority}
**Responsável:** {assigned_to}

### 📅 **Datas**
**Criado:** {created_date}
**Modificado:** {changed_date}

### 🗂️ **Organização**
**Área:** {area_path}
**Iteração:** {iteration_path}

### 🏷️ **Tags**
{tags}

### 📄 **Descrição**
{description}

### 🔗 **Links**
**URL:** {url}

💡 **Dica:** Use `busque itens similares` para encontrar work items relacionados.""",
            
            'search_results': """## 🔍 Resultados da Busca

**Termo buscado:** `{search_term}`
**Resultados encontrados:** {count}

{results_table}

{search_summary}

💡 **Dica:** Use `mostre item #123` para ver detalhes completos de um work item.""",
            
            'search_no_results': """## 🔍 Resultados da Busca

**Termo buscado:** `{search_term}`
**Resultados encontrados:** 0

❌ **Nenhum resultado encontrado**

**Sugestões:**
- Verifique se o termo de busca está correto
- Tente termos mais gerais
- Use diferentes palavras-chave
- Verifique se há work items no projeto

**Exemplos de busca:**
- `busque itens com 'login'`
- `search bugs about 'performance'`
- `find features with 'mobile'`""",
            
            'error_generic': """## ⚠️ Erro

Ocorreu um erro ao processar sua solicitação.

**Erro:** {error_message}

**Possíveis soluções:**
- Verifique sua conexão com o Azure DevOps
- Confirme se as credenciais estão corretas
- Tente novamente em alguns instantes
- Digite `ajuda` para ver comandos disponíveis""",
            
            'error_connection': """## 🔌 Erro de Conexão

Não foi possível conectar ao Azure DevOps.

**Possíveis causas:**
- Credenciais inválidas ou expiradas
- Problemas de rede
- Azure DevOps indisponível
- Permissões insuficientes

**Soluções:**
1. Verifique suas credenciais no arquivo `.env`
2. Confirme se o Personal Access Token está válido
3. Verifique sua conexão com a internet
4. Tente novamente em alguns instantes""",
            
            'error_not_found': """## ❌ Item Não Encontrado

O item solicitado não foi encontrado.

**Detalhes:**
- **Tipo:** {item_type}
- **ID/Nome:** {item_id}
- **Projeto:** {project}

**Possíveis causas:**
- O item foi removido ou renomeado
- Você não tem permissão para visualizar o item
- O ID está incorreto

**Sugestões:**
- Verifique se o ID está correto
- Tente buscar o item por nome
- Use `liste work items` para ver itens disponíveis""",
            
            'command_suggestions': """## 💡 Sugestões de Comandos

Com base no seu input, aqui estão algumas sugestões:

{suggestions}

**Comandos populares:**
- `Liste os boards`
- `Mostre os work items`
- `Busque itens com 'termo'`
- `Mostre o item #123`
- `Ajuda`""",
            
            'processing': """## ⏳ Processando...

Estou processando sua solicitação...

**Comando:** {command}
**Tipo:** {command_type}

Aguarde um momento...""",
            
            'stats': """## 📊 Estatísticas da Sessão

**Informações da Sessão:**
- **Usuário:** {user_name}
- **Organização:** {organization}
- **Projeto:** {project}
- **Sessão iniciada:** {session_start}

**Atividade:**
- **Total de mensagens:** {total_messages}
- **Comandos executados:** {commands_executed}
- **Work items visualizados:** {work_items_viewed}
- **Boards listados:** {boards_listed}

**Performance:**
- **Tempo médio de resposta:** {avg_response_time}s
- **Taxa de sucesso:** {success_rate}%""",
            
            'goodbye': """## 👋 Até logo!

Obrigado por usar o Assistente Azure DevOps!

**Resumo da sessão:**
- **Duração:** {session_duration}
- **Comandos executados:** {commands_executed}
- **Work items visualizados:** {work_items_viewed}

Espero ter ajudado! Volte sempre! 🤖"""
        }
    
    def render_template(self, template_name: str, context: TemplateContext, **kwargs) -> str:
        """Render a template with context"""
        if template_name not in self.templates:
            logger.warning(f"Template '{template_name}' not found")
            return f"Template '{template_name}' não encontrado."
        
        template = self.templates[template_name]
        
        # Prepare context variables
        template_vars = {
            'user_name': context.user_name,
            'organization': context.organization,
            'project': context.project,
            'current_time': context.current_time.strftime("%d/%m/%Y %H:%M:%S"),
            'command_type': context.command_type.value,
            **kwargs
        }
        
        try:
            return template.format(**template_vars)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            return f"Erro ao renderizar template: variável {e} não encontrada."
    
    def format_boards_table(self, boards: List[Board]) -> str:
        """Format boards as a markdown table"""
        if not boards:
            return "Nenhum board disponível."
        
        table_rows = []
        for board in boards:
            table_rows.append(f"| {board.name} | {board.board_type} | {board.url} |")
        
        return "| Nome | Tipo | URL |\n|------|------|-----|\n" + "\n".join(table_rows)
    
    def format_work_items_table(self, work_items: List[WorkItem], max_title_length: int = 50) -> str:
        """Format work items as a markdown table"""
        if not work_items:
            return "Nenhum work item encontrado."
        
        table_rows = []
        for item in work_items:
            title = item.title[:max_title_length] + "..." if len(item.title) > max_title_length else item.title
            assigned_to = item.assigned_to or "Não atribuído"
            table_rows.append(f"| #{item.id} | {title} | {item.work_item_type} | {item.state} | {assigned_to} |")
        
        return "| ID | Título | Tipo | Status | Responsável |\n|----|--------|------|-------|-------------|\n" + "\n".join(table_rows)
    
    def format_filter_info(self, filters: Dict[str, Any]) -> str:
        """Format filter information"""
        if not filters:
            return ""
        
        filter_parts = []
        
        if 'types' in filters:
            filter_parts.append(f"**Tipo:** {', '.join(filters['types'])}")
        
        if 'state' in filters:
            filter_parts.append(f"**Status:** {filters['state']}")
        
        if 'assigned_to' in filters:
            filter_parts.append(f"**Responsável:** {filters['assigned_to']}")
        
        if filter_parts:
            return f"**Filtros aplicados:** {', '.join(filter_parts)}\n\n"
        
        return ""
    
    def format_summary_info(self, work_items: List[WorkItem]) -> str:
        """Format summary information for work items"""
        if not work_items:
            return ""
        
        # Count by type
        type_counts = {}
        state_counts = {}
        
        for item in work_items:
            # Type counts
            item_type = item.work_item_type
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
            
            # State counts
            state = item.state
            state_counts[state] = state_counts.get(state, 0) + 1
        
        summary_parts = []
        
        if len(type_counts) > 1:
            type_summary = ", ".join([f"{count} {item_type}" for item_type, count in type_counts.items()])
            summary_parts.append(f"**Por tipo:** {type_summary}")
        
        if len(state_counts) > 1:
            state_summary = ", ".join([f"{count} {state}" for state, count in state_counts.items()])
            summary_parts.append(f"**Por status:** {state_summary}")
        
        if summary_parts:
            return "\n".join(summary_parts) + "\n"
        
        return ""
    
    def format_search_summary(self, work_items: List[WorkItem], search_term: str) -> str:
        """Format search summary"""
        if not work_items:
            return ""
        
        # Count by type
        type_counts = {}
        for item in work_items:
            item_type = item.work_item_type
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        summary_parts = []
        
        if len(type_counts) > 1:
            type_summary = ", ".join([f"{count} {item_type}" for item_type, count in type_counts.items()])
            summary_parts.append(f"**Encontrados:** {type_summary}")
        
        if summary_parts:
            return "\n".join(summary_parts) + "\n"
        
        return ""
    
    def format_tags(self, tags: List[str]) -> str:
        """Format tags list"""
        if not tags:
            return "Nenhuma tag"
        
        return ", ".join([f"`{tag}`" for tag in tags])
    
    def format_description(self, description: str, max_length: int = 500) -> str:
        """Format description with length limit"""
        if not description:
            return "Sem descrição"
        
        if len(description) <= max_length:
            return description
        
        return description[:max_length] + "...\n\n*[Descrição truncada - use o link para ver completa]*"
    
    def create_welcome_message(self, context: TemplateContext) -> str:
        """Create welcome message"""
        return self.render_template('welcome', context)
    
    def create_help_message(self, context: TemplateContext) -> str:
        """Create help message"""
        return self.render_template('help', context)
    
    def create_boards_response(self, boards: List[Board], context: TemplateContext) -> str:
        """Create boards list response"""
        if not boards:
            return self.render_template('boards_empty', context)
        
        boards_table = self.format_boards_table(boards)
        return self.render_template('boards_list', context, 
                                 boards_table=boards_table, 
                                 count=len(boards))
    
    def create_work_items_response(self, work_items: List[WorkItem], filters: Dict, context: TemplateContext) -> str:
        """Create work items list response"""
        if not work_items:
            filter_info = self.format_filter_info(filters)
            return self.render_template('work_items_empty', context, filter_info=filter_info)
        
        items_table = self.format_work_items_table(work_items)
        filter_info = self.format_filter_info(filters)
        summary_info = self.format_summary_info(work_items)
        
        return self.render_template('work_items_list', context,
                                 items_table=items_table,
                                 filter_info=filter_info,
                                 summary_info=summary_info,
                                 count=len(work_items))
    
    def create_work_item_detail_response(self, work_item: WorkItem, context: TemplateContext) -> str:
        """Create work item detail response"""
        assigned_to = work_item.assigned_to or "Não atribuído"
        description = self.format_description(work_item.description or "")
        tags = self.format_tags(work_item.tags)
        
        return self.render_template('work_item_detail', context,
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
                                 url=work_item.url)
    
    def create_search_response(self, work_items: List[WorkItem], search_term: str, context: TemplateContext) -> str:
        """Create search results response"""
        if not work_items:
            return self.render_template('search_no_results', context, search_term=search_term)
        
        results_table = self.format_work_items_table(work_items)
        search_summary = self.format_search_summary(work_items, search_term)
        
        return self.render_template('search_results', context,
                                 results_table=results_table,
                                 search_summary=search_summary,
                                 search_term=search_term,
                                 count=len(work_items))
    
    def create_error_response(self, error_message: str, context: TemplateContext, error_type: str = "generic") -> str:
        """Create error response"""
        template_name = f"error_{error_type}" if error_type != "generic" else "error_generic"
        
        if template_name not in self.templates:
            template_name = "error_generic"
        
        return self.render_template(template_name, context, error_message=error_message)
    
    def create_suggestions_response(self, suggestions: List[str], context: TemplateContext) -> str:
        """Create command suggestions response"""
        suggestions_text = "\n".join([f"- `{suggestion}`" for suggestion in suggestions])
        
        return self.render_template('command_suggestions', context, suggestions=suggestions_text) 

    def get_unknown_command_response(self) -> str:
        """Return a default response for unknown commands"""
        return (
            "## 🤔 Comando não reconhecido\n\n"
            "Desculpe, não entendi o comando informado.\n\n"
            "**Sugestões:**\n"
            "- Verifique se há erros de digitação\n"
            "- Tente um comando diferente\n"
            "- Digite `ajuda` para ver exemplos de comandos suportados"
        ) 