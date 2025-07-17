from typing import Dict, Optional, Type
from src.services.llm.base_provider import BaseLLMProvider
from src.services.llm.openai_provider import OpenAIProvider
from src.services.llm.anthropic_provider import AnthropicProvider
from src.services.llm.google_provider import GoogleProvider
from src.services.llm.deepseek_provider import DeepSeekProvider
from src.utils.logger import logger
from src.utils.exceptions import ConfigurationError

class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    _providers: Dict[str, Type[BaseLLMProvider]] = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'google': GoogleProvider,
        'deepseek': DeepSeekProvider
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseLLMProvider]):
        """Register a new provider"""
        cls._providers[name] = provider_class
        logger.info(f"Registered LLM provider: {name}")
    
    @classmethod
    def get_provider(cls, name: str, config: Dict) -> BaseLLMProvider:
        """Get a provider instance by name"""
        if name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ConfigurationError(f"Unknown provider '{name}'. Available providers: {available}")
        
        provider_class = cls._providers[name]
        
        try:
            provider = provider_class(config)
            logger.info(f"Created LLM provider: {name}")
            return provider
        except Exception as e:
            logger.error(f"Failed to create provider '{name}': {e}")
            raise ConfigurationError(f"Failed to create provider '{name}': {e}")
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available provider names"""
        return list(cls._providers.keys())
    
    @classmethod
    def test_provider(cls, name: str, config: Dict) -> bool:
        """Test if a provider can be created and connected"""
        try:
            provider = cls.get_provider(name, config)
            return provider.test_connection()
        except Exception as e:
            logger.error(f"Provider test failed for '{name}': {e}")
            return False

class LLMService:
    """Service for managing LLM providers"""
    
    def __init__(self, default_provider: str = None):
        self.default_provider = default_provider
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.factory = LLMProviderFactory()
    
    def add_provider(self, name: str, config: Dict) -> BaseLLMProvider:
        """Add a provider to the service"""
        provider = self.factory.get_provider(name, config)
        self.providers[name] = provider
        logger.info(f"Added LLM provider: {name}")
        return provider
    
    def get_provider(self, name: str = None) -> BaseLLMProvider:
        """Get a provider by name or default"""
        provider_name = name or self.default_provider
        
        if not provider_name:
            raise ConfigurationError("No provider specified and no default provider set")
        
        if provider_name not in self.providers:
            raise ConfigurationError(f"Provider '{provider_name}' not found. Available: {list(self.providers.keys())}")
        
        return self.providers[provider_name]
    
    def get_available_providers(self) -> list[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def test_all_providers(self) -> Dict[str, bool]:
        """Test all registered providers"""
        results = {}
        
        for name, provider in self.providers.items():
            try:
                results[name] = provider.test_connection()
                logger.info(f"Provider '{name}' test: {'PASS' if results[name] else 'FAIL'}")
            except Exception as e:
                results[name] = False
                logger.error(f"Provider '{name}' test failed: {e}")
        
        return results
    
    def switch_provider(self, name: str) -> bool:
        """Switch to a different provider"""
        if name in self.providers:
            self.default_provider = name
            logger.info(f"Switched to provider: {name}")
            return True
        else:
            logger.error(f"Cannot switch to provider '{name}': not found")
            return False 