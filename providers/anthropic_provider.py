import anthropic
import os
from typing import Dict, Any

from providers.base_provider import BaseLLMProvider

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Anthropic API key is not provided")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        data = {
            "model": os.environ.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20240620'),
            "messages": [{"role": "user", "content": prompt}]
        }
        response = self.send_request(data)
        processed_response = self.process_response(response)
        return processed_response['choices'][0]['message']['content']

    def get_available_models(self) -> Dict[str, int]:
        return {
            "claude-3-5-sonnet-20240620": 4096,
            "claude-3-opus-20240229": 4096,
            "claude-3-sonnet-20240229": 4096,
            "claude-3-haiku-20240307": 4096,
            "claude-2.1": 100000,
            "claude-2.0": 100000,
            "claude-instant-1.2": 100000,
        }
                
    def process_response(self, response: Any) -> Dict[str, Any]:
        if response is not None:
            return {
                "choices": [
                    {
                        "message": {
                            "content": response.content[0].text
                        }
                    }
                ]
            }
        return None
    
    def send_request(self, data: Dict[str, Any]) -> Any:
        try:
            model = data['model']
            max_tokens = min(data.get('max_tokens', 4096), self.get_available_models()[model])
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=data.get('temperature', 0.1),
                messages=[
                    {"role": "user", "content": message["content"]}
                    for message in data['messages']
                ]
            )
            return response
        except anthropic.APIError as e:
            if os.environ.get('DEBUG') == 'True':
                print(f"Anthropic API error: {e}")
            raise Exception(f"Anthropic API error: {str(e)}")