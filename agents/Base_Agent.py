# agents/Base_Agent.py

from abc import ABC, abstractmethod
from typing import Any

class Base_Agent(ABC):
    @abstractmethod
    def process_request(self, request: str) -> Any:
        pass

    @abstractmethod
    def process_request(self, request: str) -> Any:
        """
        Process the user's request and return a response.
        
        Args:
        request (str): The user's request to be processed.
        
        Returns:
        Any: The processed response.
        """
        pass

    def _create_summary_prompt(self, content: str, user_request: str) -> str:
        """
        Create a summary prompt for the LLM provider.
        
        Args:
        content (str): The content to be summarized.
        user_request (str): The original user request.
        
        Returns:
        str: The formatted summary prompt.
        """
        return f"""
        Given the following content:
        {content}

        Respond to the user's request: "{user_request}"
        
        Provide a concise and relevant summary that directly addresses the user's request.
        """

    def _summarize_content(self, content: str, user_request: str) -> str:
        """
        Summarize the given content using the LLM provider.
        
        Args:
        content (str): The content to be summarized.
        user_request (str): The original user request.
        
        Returns:
        str: The summarized content.
        """
        summary_prompt = self._create_summary_prompt(content, user_request)
        return self.provider.generate(summary_prompt)