import os
from providers.anthropic_provider import AnthropicProvider
from providers.groq_provider import Groq_Provider

class ProviderFactory:
    @staticmethod
    def get_provider():
        default_provider = os.environ.get('DEFAULT_PROVIDER', 'Anthropic')
        if default_provider == "Anthropic":
            return AnthropicProvider()
        elif default_provider == "Groq":
            return Groq_Provider()
        else:
            raise ValueError(f"Unsupported provider: {default_provider}")

    @staticmethod
    def get_model():
        return os.environ.get('DEFAULT_MODEL', 'claude-3-5-sonnet-20240620')