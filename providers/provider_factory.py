import os
from providers.groq_provider import Groq_Provider

class ProviderFactory:
    @staticmethod
    def get_provider(api_key):
        return Groq_Provider(api_key)

    @staticmethod
    def get_model():
        return os.environ.get('DEFAULT_MODEL', 'mixtral-8x7b-32768')