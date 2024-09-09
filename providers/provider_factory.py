import os
import sys
from pocketgroq import GroqProvider
from providers.anthropic_provider import AnthropicProvider

# Set up logging only if DEBUG is True in .env
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

def log_debug(message):
    if DEBUG:
        with open('debug_info.txt', 'a') as f:
            f.write(f"{message}\n")

if DEBUG:
    log_debug("Entering provider_factory.py")
    log_debug(f"Current working directory: {os.getcwd()}")
    log_debug(f"Current sys.path: {sys.path}")

class ProviderFactory:
    @staticmethod
    def get_provider(provider_name, api_key):
        if DEBUG:
            log_debug(f"get_provider called with provider_name: {provider_name}")
        providers = {
            'groq': GroqProvider,
            'anthropic': AnthropicProvider,
            # Add more providers here as needed
        }
        
        provider_class = providers.get(provider_name.lower())
        if provider_class is None:
            if DEBUG:
                log_debug(f"Unsupported provider: {provider_name}")
            raise ValueError(f"Unsupported provider: {provider_name}")
        
        if DEBUG:
            log_debug(f"Creating {provider_name} instance with API key")
        return provider_class(api_key)

    @staticmethod
    def get_model():
        model = os.environ.get('DEFAULT_MODEL', 'llava-v1.5-7b-4096-preview')
        if DEBUG:
            log_debug(f"get_model called, returning: {model}")
        return model

if DEBUG:
    log_debug("Exiting provider_factory.py")