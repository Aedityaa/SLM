"""Base class for all mathematical tools"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the tool and return results"""
        pass
    
    def validate_input(self, *args, **kwargs) -> bool:
        """Validate input parameters"""
        return True
    
    def format_result(self, result: Any) -> str:
        """Format the result for injection back to model"""
        return str(result)
    
    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        """Make tool callable"""
        if not self.validate_input(*args, **kwargs):
            return {
                "success": False,
                "error": "Invalid input parameters",
                "tool": self.name
            }
        
        try:
            result = self.execute(*args, **kwargs)
            return {
                "success": True,
                "result": result,
                "tool": self.name,
                "formatted": self.format_result(result)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool": self.name
            }