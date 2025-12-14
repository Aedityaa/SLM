"""Tool registration and management system"""
from typing import Dict, Optional, Type
from src.tools.base_tool import BaseTool

class ToolRegistry:
    """Registry for managing all available tools"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool):
        """Register a tool"""
        self._tools[tool.name] = tool
        print(f"✅ Registered tool: {tool.name}")
    
    def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> Dict[str, str]:
        """List all available tools"""
        return {name: tool.description for name, tool in self._tools.items()}
    
    def unregister(self, name: str):
        """Remove a tool from registry"""
        if name in self._tools:
            del self._tools[name]
            print(f"🗑️  Unregistered tool: {name}")

# Global registry instance
tool_registry = ToolRegistry()