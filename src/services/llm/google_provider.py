import google.generativeai as genai
from typing import Dict, List, Optional, Any
from src.services.llm.base_provider import BaseLLMProvider, LLMRequest, LLMResponse
from src.utils.logger import logger
from src.utils.exceptions import LLMProviderError

class GoogleProvider(BaseLLMProvider):
    """Google Gemini LLM provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        genai.configure(api_key=self.api_key)
        
        # Set default model if not specified
        if not self.model:
            self.model = "gemini-1.5-pro"
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Google Gemini API"""
        try:
            self.validate_request(request)
            
            # Format messages for Gemini
            messages = self.format_messages(request.messages)
            
            logger.debug(f"Generating response with Google model: {request.model}")
            
            # Create model instance
            model = genai.GenerativeModel(request.model)
            
            # Convert messages to Gemini format
            chat = model.start_chat(history=[])
            
            # Send the last user message (Gemini doesn't support full conversation history in the same way)
            last_user_message = None
            for message in messages:
                if message['role'] == 'user':
                    last_user_message = message['content']
            
            if not last_user_message:
                raise ValueError("No user message found")
            
            response = chat.send_message(last_user_message)
            
            # Extract response content
            content = response.text
            
            # Gemini doesn't provide detailed usage info in the same way
            usage = {
                'prompt_tokens': 0,  # Not available
                'completion_tokens': 0,  # Not available
                'total_tokens': 0  # Not available
            }
            
            logger.debug(f"Google response generated successfully")
            
            return LLMResponse(
                content=content,
                model=request.model,
                provider="google",
                usage=usage,
                finish_reason="stop"
            )
            
        except Exception as e:
            logger.error(f"Google generation failed: {e}")
            raise LLMProviderError("google", f"Generation failed: {e}")
    
    def test_connection(self) -> bool:
        """Test connection to Google Gemini API"""
        try:
            # Try to list models
            models = genai.list_models()
            logger.info("Google connection test successful")
            return True
        except Exception as e:
            logger.error(f"Google connection test failed: {e}")
            return False
    
    def format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for Google Gemini API"""
        # Gemini has a different conversation model
        # We'll extract the system message and user message
        formatted_messages = []
        
        system_message = ""
        user_message = ""
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                system_message = content
            elif role == 'user':
                user_message = content
            elif role == 'assistant':
                # For now, we'll ignore assistant messages in the history
                # as Gemini handles conversation differently
                pass
        
        # Combine system and user messages
        if system_message and user_message:
            combined_message = f"{system_message}\n\n{user_message}"
        elif system_message:
            combined_message = system_message
        else:
            combined_message = user_message
        
        formatted_messages.append({'role': 'user', 'content': combined_message})
        
        return formatted_messages
    
    def get_available_models(self) -> List[str]:
        """Get list of available Google models"""
        try:
            models = genai.list_models()
            return [model.name for model in models if 'gemini' in model.name.lower()]
        except Exception as e:
            logger.error(f"Failed to get Google models: {e}")
            return [
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-pro"
            ]
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get usage information from Google"""
        try:
            return {
                'provider': 'google',
                'model': self.model,
                'note': 'Usage information not available via API'
            }
        except Exception as e:
            logger.error(f"Failed to get Google usage info: {e}")
            return {} 