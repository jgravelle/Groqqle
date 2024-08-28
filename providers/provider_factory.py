import os
import sys
from pocketgroq import GroqProvider
from providers.anthropic_provider import AnthropicProvider

def log_debug(message):
    with open('debug_info.txt', 'a') as f:
        f.write(f"{message}\n")

log_debug("Entering provider_factory.py")
log_debug(f"Current working directory: {os.getcwd()}")
log_debug(f"Current sys.path: {sys.path}")

class ProviderFactory:
    @staticmethod
    def get_provider(provider_name, api_key):
        log_debug(f"get_provider called with provider_name: {provider_name}")
        providers = {
            'groq': GroqProvider,
            'anthropic': AnthropicProvider,
            # Add more providers here as needed
        }
        
        provider_class = providers.get(provider_name.lower())
        if provider_class is None:
            log_debug(f"Unsupported provider: {provider_name}")
            raise ValueError(f"Unsupported provider: {provider_name}")
        
        log_debug(f"Creating {provider_name} instance with API key")
        return provider_class(api_key)

    @staticmethod
    def get_model():
        model = os.environ.get('DEFAULT_MODEL', 'mixtral-8x7b-32768')
        log_debug(f"get_model called, returning: {model}")
        return model

log_debug("Exiting provider_factory.py")