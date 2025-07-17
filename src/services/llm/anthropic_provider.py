import anthropic
from typing import Dict, List, Optional, Any
from src.services.llm.base_provider import BaseLLMProvider, LLMRequest, LLMResponse
from src.utils.logger import logger
from src.utils.exceptions import LLMProviderError

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
        # Set default model if not specified
        if not self.model:
            self.model = "claude-3-5-sonnet-20241022"
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic Claude API"""
        try:
            self.validate_request(request)
            
            # Format messages for Anthropic
            messages = self.format_messages(request.messages)
            
            logger.debug(f"Generating response with Anthropic model: {request.model}")
            
            response = self.client.messages.create(
                model=request.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            # Extract response content
            content = response.content[0].text
            
            # Extract usage information
            usage = {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }
            
            # Extract finish reason
            finish_reason = response.stop_reason
            
            logger.debug(f"Anthropic response generated successfully. Tokens used: {usage['total_tokens']}")
            
            return LLMResponse(
                content=content,
                model=request.model,
                provider="anthropic",
                usage=usage,
                finish_reason=finish_reason
            )
            
        except anthropic.AuthenticationError:
            raise LLMProviderError("anthropic", "Invalid API key", 401)
        except anthropic.RateLimitError:
            raise LLMProviderError("anthropic", "Rate limit exceeded", 429)
        except anthropic.APIError as e:
            raise LLMProviderError("anthropic", f"API error: {e}", 500)
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise LLMProviderError("anthropic", f"Generation failed: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to Anthropic API"""
        try:
            # Try to get model info
            self.client.models.get("claude-3-5-sonnet-20241022")
            logger.info("Anthropic connection test successful")
            return True
        except Exception as e:
            logger.error(f"Anthropic connection test failed: {e}")
            return False
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for Anthropic API"""
        formatted_messages = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            # Anthropic expects specific role names
            if role == 'assistant':
                formatted_messages.append({'role': 'assistant', 'content': content})
            elif role == 'system':
                # Anthropic doesn't support system messages in the same way
                # We'll prepend system messages to the first user message
                if formatted_messages and formatted_messages[0]['role'] == 'user':
                    formatted_messages[0]['content'] = f"{content}\n\n{formatted_messages[0]['content']}"
                else:
                    # If no user message yet, create one with system content
                    formatted_messages.append({'role': 'user', 'content': content})
            else:
                formatted_messages.append({'role': 'user', 'content': content})
        
        return formatted_messages
    
    def get_available_models(self) -> List[str]:
        """Get list of available Anthropic models"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if 'claude' in model.id.lower()]
        except Exception as e:
            logger.error(f"Failed to get Anthropic models: {e}")
            return [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get usage information from Anthropic"""
        try:
            # Note: Anthropic doesn't provide usage info via API in the same way
            # This would require additional API calls to billing endpoints
            return {
                'provider': 'anthropic',
                'model': self.model,
                'note': 'Usage information requires billing API access'
            }
        except Exception as e:
            logger.error(f"Failed to get Anthropic usage info: {e}")
            return {} 