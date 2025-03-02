import os
import asyncio
import groq
from typing import Dict, Any, Optional, Union, AsyncIterator, List

from providers.base_provider import BaseLLMProvider

class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Groq API key is not provided")
        
        try:
            self.client = groq.Client(api_key=self.api_key)
        except (ImportError, ModuleNotFoundError):
            # Fallback if groq package is not installed
            self.client = None
            print("Warning: groq package not installed. Using basic HTTP requests instead.")

    def generate(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.0, model: str = None, image_path: Optional[str] = None) -> str:
        """
        Generate a response from the Groq API
        
        Args:
            prompt: The input prompt for the model
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature parameter for generation
            model: Optional model name, uses environment variable or default if not specified
            image_path: Optional path to an image for vision models
        
        Returns:
            Generated text response
        """
        if not model:
            model = os.environ.get('GROQ_MODEL', 'llama3-8b-8192')
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Handle image input for vision models
        if image_path and model == "llama-3.2-11b-vision-preview":
            # For vision model
            return self._generate_with_vision(prompt, image_path, max_tokens, temperature, model)
        else:
            # Text-only generation
            response = self.send_request(data)
            processed_response = self.process_response(response)
            return processed_response
    
    def _generate_with_vision(self, prompt: str, image_path: str, max_tokens: int, temperature: float, model: str) -> str:
        """Generate a response using a vision model with an image input"""
        try:
            # For vision models, we need to structure the content differently
            if image_path.startswith(('http://', 'https://')):
                # For image URLs
                content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_path}}
                ]
            else:
                # For local image paths - not implemented here since we're using URLs
                raise ValueError("Local image paths are not supported")
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": content}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = self.send_request(data)
            processed_response = self.process_response(response)
            return processed_response
            
        except Exception as e:
            if os.getenv('DEBUG') == 'True':
                print(f"Groq Vision API error: {e}")
            raise Exception(f"Groq Vision API error: {str(e)}")
    
    def get_available_models(self) -> Dict[str, int]:
        """Return a dictionary of available models and their context windows"""
        return {
            "llama3-8b-8192": 32768,
            "llama2-70b-4096": 4096,
            "llama-3.2-11b-vision-preview": 4096,
            "mixtral-8x7b-32768": 32768,
            "gemma-7b-it": 8192
        }
    
    def process_response(self, response: Any) -> str:
        """Process the response from the Groq API"""
        if not response:
            return "Error: No response received from Groq API"
        
        try:
            return response.choices[0].message.content
        except (AttributeError, IndexError) as e:
            if os.getenv('DEBUG') == 'True':
                print(f"Error processing Groq response: {e}")
            return "Error: Failed to extract content from Groq response"
    
    def send_request(self, data: Dict[str, Any]) -> Any:
        """Send a request to the Groq API"""
        try:
            if self.client:
                response = self.client.chat.completions.create(
                    model=data["model"],
                    messages=data["messages"],
                    max_tokens=data.get("max_tokens", 4096),
                    temperature=data.get("temperature", 0.0)
                )
                return response
            else:
                # Fallback implementation using requests if needed
                raise NotImplementedError("Fallback implementation not available - please install the groq package")
        except Exception as e:
            if os.getenv('DEBUG') == 'True':
                print(f"Groq API error: {e}")
            raise Exception(f"Groq API error: {str(e)}")
    
    async def _async_create_completion(self, **kwargs) -> Union[str, AsyncIterator[str]]:
        """Create a completion asynchronously"""
        # This is a placeholder implementation
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.generate(
                kwargs.get('prompt', ''),
                max_tokens=kwargs.get('max_tokens', 4096),
                temperature=kwargs.get('temperature', 0.0),
                model=kwargs.get('model', None)
            )
        )
    
    def _process_tool_calls(self, response: Any, tools: List[Dict[str, Any]]) -> str:
        """Process tool calls in the response"""
        # Groq doesn't support tool calls natively yet, but we need to implement the method
        return "Tool calls not supported in Groq yet"
    
    async def _async_process_tool_calls(self, response: Any, tools: List[Dict[str, Any]]) -> str:
        """Process tool calls in the response asynchronously"""
        # Groq doesn't support tool calls natively yet, but we need to implement the method
        return "Tool calls not supported in Groq yet"