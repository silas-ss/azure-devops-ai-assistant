import requests
from typing import Dict, List, Optional, Any
from src.services.llm.base_provider import BaseLLMProvider, LLMRequest, LLMResponse
from src.utils.logger import logger
from src.utils.exceptions import LLMProviderError

class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek LLM provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        # Set default model if not specified
        if not self.model:
            self.model = "deepseek-chat"
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using DeepSeek API"""
        try:
            self.validate_request(request)
            
            # Format messages for DeepSeek
            messages = self.format_messages(request.messages)
            
            logger.debug(f"Generating response with DeepSeek model: {request.model}")
            
            # Prepare request payload
            payload = {
                "model": request.model,
                "messages": messages,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": request.stream
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code != 200:
                if response.status_code == 401:
                    raise LLMProviderError("deepseek", "Invalid API key", 401)
                elif response.status_code == 429:
                    raise LLMProviderError("deepseek", "Rate limit exceeded", 429)
                else:
                    raise LLMProviderError("deepseek", f"API error: {response.text}", response.status_code)
            
            response_data = response.json()
            
            # Extract response content
            content = response_data['choices'][0]['message']['content']
            
            # Extract usage information
            usage = response_data.get('usage', {})
            
            # Extract finish reason
            finish_reason = response_data['choices'][0].get('finish_reason', 'stop')
            
            logger.debug(f"DeepSeek response generated successfully. Tokens used: {usage.get('total_tokens', 0)}")
            
            return LLMResponse(
                content=content,
                model=request.model,
                provider="deepseek",
                usage=usage,
                finish_reason=finish_reason
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API request failed: {e}")
            raise LLMProviderError("deepseek", f"API request failed: {e}")
        except Exception as e:
            logger.error(f"DeepSeek generation failed: {e}")
            raise LLMProviderError("deepseek", f"Generation failed: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to DeepSeek API"""
        try:
            # Try to make a simple request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("DeepSeek connection test successful")
                return True
            else:
                logger.error(f"DeepSeek connection test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"DeepSeek connection test failed: {e}")
            return False
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for DeepSeek API"""
        formatted_messages = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            # DeepSeek expects specific role names
            if role == 'assistant':
                formatted_messages.append({'role': 'assistant', 'content': content})
            elif role == 'system':
                formatted_messages.append({'role': 'system', 'content': content})
            else:
                formatted_messages.append({'role': 'user', 'content': content})
        
        return formatted_messages
    
    def get_available_models(self) -> List[str]:
        """Get list of available DeepSeek models"""
        try:
            # DeepSeek doesn't provide a models endpoint like OpenAI
            # Return known models
            return [
                "deepseek-chat",
                "deepseek-coder",
                "deepseek-chat-33b",
                "deepseek-coder-33b"
            ]
        except Exception as e:
            logger.error(f"Failed to get DeepSeek models: {e}")
            return ["deepseek-chat"]
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get usage information from DeepSeek"""
        try:
            return {
                'provider': 'deepseek',
                'model': self.model,
                'note': 'Usage information not available via API'
            }
        except Exception as e:
            logger.error(f"Failed to get DeepSeek usage info: {e}")
            return {} 