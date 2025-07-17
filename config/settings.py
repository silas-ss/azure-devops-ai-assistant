import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AzureDevOpsConfig:
    """Configuration for Azure DevOps integration"""
    organization: str
    project: str
    project_id: str
    personal_access_token: str
    team: str = ""
    base_url: str = "https://dev.azure.com"

@dataclass
class LLMProviderConfig:
    """Configuration for LLM providers"""
    name: str
    api_key: str
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7

@dataclass
class AppConfig:
    """Main application configuration"""
    default_llm_provider: str
    log_level: str
    cache_enabled: bool
    cache_ttl: int
    providers: Dict[str, LLMProviderConfig]

class Settings:
    """Central settings manager"""
    
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables"""
        
        # Azure DevOps config
        self.azure_devops = AzureDevOpsConfig(
            organization=os.getenv("AZURE_DEVOPS_ORGANIZATION", ""),
            project=os.getenv("AZURE_DEVOPS_PROJECT", ""),
            project_id=os.getenv("AZURE_DEVOPS_PROJECT_ID", ""),
            personal_access_token=os.getenv("AZURE_DEVOPS_PAT", ""),
            team=os.getenv("AZURE_DEVOPS_TEAM", "")
        )
        
        # LLM Providers config
        providers = {}
        
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            providers["openai"] = LLMProviderConfig(
                name="openai",
                api_key=os.getenv("OPENAI_API_KEY"),
                model=os.getenv("OPENAI_MODEL", "gpt-4o")
            )
        
        # Anthropic
        if os.getenv("ANTHROPIC_API_KEY"):
            providers["anthropic"] = LLMProviderConfig(
                name="anthropic",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            )
        
        # Google
        if os.getenv("GOOGLE_API_KEY"):
            providers["google"] = LLMProviderConfig(
                name="google",
                api_key=os.getenv("GOOGLE_API_KEY"),
                model=os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")
            )
        
        # DeepSeek
        if os.getenv("DEEPSEEK_API_KEY"):
            providers["deepseek"] = LLMProviderConfig(
                name="deepseek",
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            )
        
        # App config
        self.app = AppConfig(
            default_llm_provider=os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.getenv("CACHE_TTL", "300")),
            providers=providers
        )
    
    def get_provider_config(self, provider_name: str) -> Optional[LLMProviderConfig]:
        """Get configuration for a specific LLM provider"""
        return self.app.providers.get(provider_name)
    
    def get_default_provider_config(self) -> Optional[LLMProviderConfig]:
        """Get configuration for the default LLM provider"""
        return self.get_provider_config(self.app.default_llm_provider)
    
    def validate_config(self) -> bool:
        """Validate that all required configuration is present"""
        if not self.azure_devops.organization:
            raise ValueError("AZURE_DEVOPS_ORGANIZATION is required")
        if not self.azure_devops.project:
            raise ValueError("AZURE_DEVOPS_PROJECT is required")
        if not self.azure_devops.project_id:
            raise ValueError("AZURE_DEVOPS_PROJECT_ID is required")
        if not self.azure_devops.personal_access_token:
            raise ValueError("AZURE_DEVOPS_PAT is required")
        
        if not self.app.providers:
            raise ValueError("At least one LLM provider must be configured")
        
        default_provider = self.get_default_provider_config()
        if not default_provider:
            raise ValueError(f"Default LLM provider '{self.app.default_llm_provider}' not found")
        
        return True

# Global settings instance
settings = Settings() 