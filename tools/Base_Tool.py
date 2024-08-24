# tools/Base_Tool.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Base_Tool(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the tool's main functionality.
        
        Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
        
        Returns:
        Any: The result of the tool's execution.
        """
        pass

    def _validate_input(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Validate the input data for the tool.
        
        Args:
        data (Dict[str, Any]): The input data to validate.
        
        Returns:
        Optional[str]: An error message if validation fails, None otherwise.
        """
        return None

    def _format_output(self, result: Any) -> Dict[str, Any]:
        """
        Format the output of the tool execution.
        
        Args:
        result (Any): The raw result of the tool execution.
        
        Returns:
        Dict[str, Any]: The formatted output.
        """
        return {"result": result}

    def _handle_error(self, error: Exception) -> str:
        """
        Handle and format any errors that occur during tool execution.
        
        Args:
        error (Exception): The error that occurred.
        
        Returns:
        str: A formatted error message.
        """
        return f"An error occurred: {str(error)}"