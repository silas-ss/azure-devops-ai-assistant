from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class LLMResponse:
    """Response from LLM provider"""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None

@dataclass
class LLMRequest:
    """Request to LLM provider"""
    messages: List[Dict[str, str]]
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    stream: bool = False

class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.model = config.get('model')
        self.max_tokens = config.get('max_tokens', 4000)
        self.temperature = config.get('temperature', 0.7)
        
        if not self.api_key:
            raise ValueError("API key is required")
        if not self.model:
            raise ValueError("Model name is required")
    
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to LLM provider"""
        pass
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for the specific provider"""
        return messages
    
    def validate_request(self, request: LLMRequest) -> bool:
        """Validate LLM request"""
        if not request.messages:
            raise ValueError("Messages cannot be empty")
        
        if request.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        
        if not (0 <= request.temperature <= 2):
            raise ValueError("temperature must be between 0 and 2")
        
        return True
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get usage information from provider"""
        return {}
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return [self.model] 