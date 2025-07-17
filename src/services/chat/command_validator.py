import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.services.chat.command_parser import CommandType, ParsedCommand
from src.utils.logger import logger
from src.utils.exceptions import ValidationError

class ValidationLevel(Enum):
    """Validation levels for commands"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class ValidationResult:
    """Result of command validation"""
    is_valid: bool
    confidence: float
    warnings: List[str]
    errors: List[str]
    sanitized_command: str
    validation_level: ValidationLevel

class CommandValidator:
    """Validates and sanitizes user commands"""
    
    def __init__(self):
        # Define validation rules
        self.validation_rules = {
            CommandType.LIST_BOARDS: {
                'min_length': 3,
                'max_length': 100,
                'required_keywords': ['board', 'list', 'show', 'get', 'display'],
                'forbidden_patterns': [
                    r'<script>',
                    r'javascript:',
                    r'data:text/html'
                ]
            },
            
            CommandType.LIST_WORK_ITEMS: {
                'min_length': 3,
                'max_length': 200,
                'required_keywords': ['item', 'work', 'list', 'show', 'get', 'display'],
                'forbidden_patterns': [
                    r'<script>',
                    r'javascript:',
                    r'data:text/html'
                ]
            },
            
            CommandType.GET_WORK_ITEM: {
                'min_length': 5,
                'max_length': 50,
                'required_patterns': [r'\d+'],  # Must contain at least one number
                'forbidden_patterns': [
                    r'<script>',
                    r'javascript:',
                    r'data:text/html'
                ]
            },
            
            CommandType.SEARCH_WORK_ITEMS: {
                'min_length': 5,
                'max_length': 300,
                'required_keywords': ['search', 'find', 'busque', 'procure', 'encontre'],
                'forbidden_patterns': [
                    r'<script>',
                    r'javascript:',
                    r'data:text/html',
                    r'[<>]'  # No HTML tags
                ]
            },
            
            CommandType.GET_BOARD: {
                'min_length': 5,
                'max_length': 100,
                'required_keywords': ['board', 'get', 'show', 'display', 'view'],
                'forbidden_patterns': [
                    r'<script>',
                    r'javascript:',
                    r'data:text/html'
                ]
            },
            
            CommandType.HELP: {
                'min_length': 2,
                'max_length': 20,
                'required_keywords': ['help', 'ajuda', 'socorro'],
                'forbidden_patterns': [
                    r'<script>',
                    r'javascript:',
                    r'data:text/html'
                ]
            }
        }
        
        # Define sanitization rules
        self.sanitization_rules = {
            'remove_html': r'<[^>]+>',
            'remove_scripts': r'<script[^>]*>.*?</script>',
            'remove_style': r'<style[^>]*>.*?</style>',
            'remove_extra_whitespace': r'\s+',
            'remove_special_chars': r'[^\w\s\-.,!?@#$%&*()+=:;"\'<>/\\]',
            'normalize_quotes': r'["""]',
            'normalize_apostrophes': r'["""]'
        }
    
    def validate_command(self, parsed_command: ParsedCommand, validation_level: ValidationLevel = ValidationLevel.MEDIUM) -> ValidationResult:
        """Validate a parsed command"""
        warnings = []
        errors = []
        confidence = parsed_command.confidence
        
        # Get validation rules for this command type
        rules = self.validation_rules.get(parsed_command.command_type, {})
        
        # Basic length validation
        command_length = len(parsed_command.original_text)
        min_length = rules.get('min_length', 1)
        max_length = rules.get('max_length', 1000)
        
        if command_length < min_length:
            errors.append(f"Comando muito curto. Mínimo: {min_length} caracteres")
            confidence -= 0.2
        
        if command_length > max_length:
            errors.append(f"Comando muito longo. Máximo: {max_length} caracteres")
            confidence -= 0.2
        
        # Required keywords validation
        required_keywords = rules.get('required_keywords', [])
        if required_keywords:
            found_keywords = []
            for keyword in required_keywords:
                if keyword.lower() in parsed_command.original_text.lower():
                    found_keywords.append(keyword)
            
            if not found_keywords:
                errors.append(f"Comando deve conter pelo menos uma das palavras: {', '.join(required_keywords)}")
                confidence -= 0.3
        
        # Required patterns validation
        required_patterns = rules.get('required_patterns', [])
        if required_patterns:
            pattern_found = False
            for pattern in required_patterns:
                if re.search(pattern, parsed_command.original_text):
                    pattern_found = True
                    break
            
            if not pattern_found:
                errors.append("Comando não contém padrão obrigatório")
                confidence -= 0.3
        
        # Forbidden patterns validation
        forbidden_patterns = rules.get('forbidden_patterns', [])
        for pattern in forbidden_patterns:
            if re.search(pattern, parsed_command.original_text, re.IGNORECASE):
                errors.append(f"Comando contém padrão proibido: {pattern}")
                confidence -= 0.5
        
        # Command-specific validation
        if parsed_command.command_type == CommandType.GET_WORK_ITEM:
            work_item_id = parsed_command.parameters.get('work_item_id')
            if work_item_id:
                if not isinstance(work_item_id, int) or work_item_id <= 0:
                    errors.append("ID do work item deve ser um número positivo")
                    confidence -= 0.3
                elif work_item_id > 999999:
                    warnings.append("ID do work item parece ser muito alto")
        
        elif parsed_command.command_type == CommandType.SEARCH_WORK_ITEMS:
            search_terms = parsed_command.parameters.get('search_terms', '')
            if len(search_terms) < 2:
                warnings.append("Termo de busca muito curto, pode retornar muitos resultados")
            elif len(search_terms) > 100:
                warnings.append("Termo de busca muito longo")
        
        # Confidence validation based on level
        if validation_level == ValidationLevel.HIGH:
            if confidence < 0.7:
                errors.append("Confiança muito baixa para processamento seguro")
        elif validation_level == ValidationLevel.MEDIUM:
            if confidence < 0.5:
                errors.append("Confiança baixa, verifique o comando")
        
        # Sanitize command
        sanitized_command = self._sanitize_command(parsed_command.original_text)
        
        is_valid = len(errors) == 0 and confidence >= 0.3
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=max(0.0, confidence),
            warnings=warnings,
            errors=errors,
            sanitized_command=sanitized_command,
            validation_level=validation_level
        )
    
    def _sanitize_command(self, command: str) -> str:
        """Sanitize command text"""
        sanitized = command
        
        # Remove HTML and scripts
        sanitized = re.sub(self.sanitization_rules['remove_scripts'], '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(self.sanitization_rules['remove_style'], '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(self.sanitization_rules['remove_html'], '', sanitized)
        
        # Normalize quotes and apostrophes
        sanitized = re.sub(self.sanitization_rules['normalize_quotes'], '"', sanitized)
        sanitized = re.sub(self.sanitization_rules['normalize_apostrophes'], "'", sanitized)
        
        # Remove extra whitespace
        sanitized = re.sub(self.sanitization_rules['remove_extra_whitespace'], ' ', sanitized)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    def validate_parameters(self, command_type: CommandType, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate command parameters"""
        errors = []
        
        if command_type == CommandType.GET_WORK_ITEM:
            work_item_id = parameters.get('work_item_id')
            if not work_item_id:
                errors.append("ID do work item é obrigatório")
            elif not isinstance(work_item_id, int):
                errors.append("ID do work item deve ser um número")
            elif work_item_id <= 0:
                errors.append("ID do work item deve ser positivo")
        
        elif command_type == CommandType.SEARCH_WORK_ITEMS:
            search_terms = parameters.get('search_terms', '')
            if not search_terms:
                errors.append("Termos de busca são obrigatórios")
            elif len(search_terms) < 2:
                errors.append("Termos de busca devem ter pelo menos 2 caracteres")
            elif len(search_terms) > 100:
                errors.append("Termos de busca muito longos")
        
        elif command_type == CommandType.GET_BOARD:
            board_name = parameters.get('board_name', '')
            if not board_name:
                errors.append("Nome do board é obrigatório")
            elif len(board_name) < 2:
                errors.append("Nome do board deve ter pelo menos 2 caracteres")
        
        return len(errors) == 0, errors
    
    def suggest_corrections(self, original_command: str, validation_result: ValidationResult) -> List[str]:
        """Suggest corrections for invalid commands"""
        suggestions = []
        
        if not validation_result.is_valid:
            command_lower = original_command.lower()
            
            # Suggest based on common patterns
            if 'board' in command_lower:
                suggestions.extend([
                    "Liste os boards",
                    "Mostre os quadros disponíveis",
                    "Get board details"
                ])
            
            if 'item' in command_lower or 'work' in command_lower:
                suggestions.extend([
                    "Liste os work items",
                    "Mostre os bugs",
                    "Get work item #123"
                ])
            
            if 'search' in command_lower or 'find' in command_lower:
                suggestions.extend([
                    "Busque itens com 'termo'",
                    "Search work items about 'topic'"
                ])
            
            if 'help' in command_lower or 'ajuda' in command_lower:
                suggestions.append("Digite 'ajuda' para ver os comandos disponíveis")
            
            # Generic suggestions
            if not suggestions:
                suggestions = [
                    "Liste os boards",
                    "Liste os work items", 
                    "Mostre o item #123",
                    "Busque itens com 'termo'",
                    "Digite 'ajuda' para ver todos os comandos"
                ]
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def get_security_score(self, command: str) -> float:
        """Calculate security score for a command"""
        score = 1.0
        
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                score -= 0.5
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter)\b)',
            r'(\b(and|or)\b\s+\d+\s*=\s*\d+)',
            r'(\b(and|or)\b\s+\'\w+\'\s*=\s*\'\w+\')'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                score -= 0.3
        
        # Check for command injection patterns
        cmd_patterns = [
            r'[;&|`$]',
            r'(\b(cat|ls|rm|del|dir|type)\b)',
            r'(\b(echo|print|printf)\b)'
        ]
        
        for pattern in cmd_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                score -= 0.2
        
        return max(0.0, score)
    
    def log_validation_result(self, validation_result: ValidationResult, original_command: str):
        """Log validation results for monitoring"""
        if not validation_result.is_valid:
            logger.warning(f"Invalid command detected: '{original_command}' - Errors: {validation_result.errors}")
        
        if validation_result.warnings:
            logger.info(f"Command warnings: '{original_command}' - Warnings: {validation_result.warnings}")
        
        security_score = self.get_security_score(original_command)
        if security_score < 0.5:
            logger.warning(f"Low security score ({security_score}) for command: '{original_command}'") 