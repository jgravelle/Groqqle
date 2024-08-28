from abc import ABC, abstractmethod
from typing import Dict, Any, Union, AsyncIterator, List

class BaseLLMProvider(ABC):
    @abstractmethod
    def __init__(self, api_key: str):
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Union[str, AsyncIterator[str]]:
        pass

    @abstractmethod
    def get_available_models(self) -> Dict[str, int]:
        pass

    @abstractmethod
    def process_response(self, response: Any) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def send_request(self, data: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def _async_create_completion(self, **kwargs) -> Union[str, AsyncIterator[str]]:
        pass

    @abstractmethod
    def _process_tool_calls(self, response: Any, tools: List[Dict[str, Any]]) -> str:
        pass

    @abstractmethod
    async def _async_process_tool_calls(self, response: Any, tools: List[Dict[str, Any]]) -> str:
        pass