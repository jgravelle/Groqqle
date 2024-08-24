import json
import os
import requests

from providers.base_provider import BaseLLMProvider

DEBUG = os.environ.get('DEBUG') == 'True'

class Groq_Provider(BaseLLMProvider):
    def __init__(self, api_key, api_url=None):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Groq API key is not provided")
        self.api_url = api_url or "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt):
        data = {
            "model": os.environ.get('GROQ_MODEL', 'mixtral-8x7b-32768'),
            "messages": [{"role": "user", "content": prompt}]
        }
        response = self.send_request(data)
        processed_response = self.process_response(response)
        return processed_response['choices'][0]['message']['content']

    def get_available_models(self):
        if DEBUG:
            print("GROQ: get_available_models")
        response = requests.get("https://api.groq.com/openai/v1/models", headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        if response.status_code == 200:
            models = response.json().get("data", [])
            return [model["id"] for model in models]
        else:
            raise Exception(f"Failed to retrieve models: {response.status_code}")

    def process_response(self, response):
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Request failed with status code {response.status_code}")

    def send_request(self, data):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        json_data = json.dumps(data) if isinstance(data, dict) else data
        response = requests.post(self.api_url, data=json_data, headers=headers)
        return response