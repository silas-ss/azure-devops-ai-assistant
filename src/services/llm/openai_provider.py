import openai
from typing import Dict, List, Optional, Any
from src.services.llm.base_provider import BaseLLMProvider, LLMRequest, LLMResponse
from src.utils.logger import logger
from src.utils.exceptions import LLMProviderError
from openai import OpenAI, AuthenticationError, RateLimitError, APIError

class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = OpenAI(api_key=self.api_key)
        
        # Set default model if not specified
        if not self.model:
            self.model = "gpt-4o"
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API"""
        try:
            self.validate_request(request)
            
            # Format messages for OpenAI
            messages = self.format_messages(request.messages)
            
            logger.debug(f"Generating response with OpenAI model: {request.model}")
            
            response = self.client.chat.completions.create(
                model=request.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                stream=request.stream
            )
            
            # Extract response content
            content = response.choices[0].message.content
            
            # Extract usage information
            usage = {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            # Extract finish reason
            finish_reason = response.choices[0].finish_reason
            
            logger.debug(f"OpenAI response generated successfully. Tokens used: {usage['total_tokens']}")
            
            return LLMResponse(
                content=content,
                model=request.model,
                provider="openai",
                usage=usage,
                finish_reason=finish_reason
            )
            
        except AuthenticationError:
            raise LLMProviderError("openai", "Invalid API key", 401)
        except RateLimitError:
            raise LLMProviderError("openai", "Rate limit exceeded", 429)
        except APIError as e:
            raise LLMProviderError("openai", f"API error: {e}", 500)
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise LLMProviderError("openai", f"Generation failed: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to OpenAI API"""
        try:
            # Try to list models
            self.client.models.list()
            logger.info("OpenAI connection test successful")
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for OpenAI API"""
        formatted_messages = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            # OpenAI expects specific role names
            if role == 'assistant':
                formatted_messages.append({'role': 'assistant', 'content': content})
            elif role == 'system':
                formatted_messages.append({'role': 'system', 'content': content})
            else:
                formatted_messages.append({'role': 'user', 'content': content})
        
        return formatted_messages
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if 'gpt' in model.id.lower()]
        except Exception as e:
            logger.error(f"Failed to get OpenAI models: {e}")
            return ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get usage information from OpenAI"""
        try:
            # Note: OpenAI doesn't provide usage info via API in the same way
            # This would require additional API calls to billing endpoints
            return {
                'provider': 'openai',
                'model': self.model,
                'note': 'Usage information requires billing API access'
            }
        except Exception as e:
            logger.error(f"Failed to get OpenAI usage info: {e}")
            return {} 