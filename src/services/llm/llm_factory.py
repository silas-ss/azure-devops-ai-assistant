from config.settings import settings

class LLMFactory:
    """Factory para criação dinâmica de providers de LLM."""
    def create_provider(self, provider_name: str, config: dict):
        if provider_name == 'openai':
            from .openai_provider import OpenAIProvider
            return OpenAIProvider(config)
        elif provider_name == 'anthropic':
            from .anthropic_provider import AnthropicProvider
            return AnthropicProvider(config)
        elif provider_name == 'google':
            from .gemini_provider import GeminiProvider
            return GeminiProvider(config)
        elif provider_name == 'deepseek':
            from .deepseek_provider import DeepSeekProvider
            return DeepSeekProvider(config)
        else:
            raise ValueError(f"Provider LLM desconhecido: {provider_name}")

def get_llm_provider(provider_name=None):
    """Retorna uma instância do provider LLM padrão ou especificado."""
    factory = LLMFactory()
    if provider_name is None:
        provider_name = settings.app.default_llm_provider
    config = settings.app.providers[provider_name].__dict__
    return factory.create_provider(provider_name, config) 