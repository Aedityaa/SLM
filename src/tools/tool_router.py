"""Routes tool calls to appropriate tools"""
import re
from typing import Dict, Any, Optional
from src.tools.tool_registry import tool_registry

class ToolRouter:
    """Routes and executes tool calls from model output"""
    
    def __init__(self):
        self.tool_call_pattern = r'<tool_call>(.*?)</tool_call>'
        self.tool_name_pattern = r'tool:\s*(\w+)'
        self.tool_params_pattern = r'params:\s*({.*?})'
    
    def detect_tool_call(self, text: str) -> bool:
        """Check if text contains a tool call"""
        return bool(re.search(self.tool_call_pattern, text, re.DOTALL))
    
    def parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse tool call from model output"""
        match = re.search(self.tool_call_pattern, text, re.DOTALL)
        
        if not match:
            return None
        
        tool_call_content = match.group(1)
        
        # Extract tool name
        tool_match = re.search(self.tool_name_pattern, tool_call_content)
        if not tool_match:
            return None
        
        tool_name = tool_match.group(1)
        
        # Extract parameters (if any)
        params = {}
        params_match = re.search(self.tool_params_pattern, tool_call_content)
        if params_match:
            import json
            try:
                params = json.loads(params_match.group(1))
            except:
                pass
        
        return {
            "tool_name": tool_name,
            "params": params,
            "raw_call": tool_call_content
        }
    
    def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool and return result"""
        tool_name = tool_call["tool_name"]
        params = tool_call["params"]
        
        # Get tool from registry
        tool = tool_registry.get(tool_name)
        
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "tool": tool_name
            }
        
        # Execute tool
        return tool(**params)
    
    def inject_result(self, original_text: str, result: Dict[str, Any]) -> str:
        """Inject tool result back into text"""
        if result["success"]:
            result_text = f"<tool_result>{result['formatted']}</tool_result>"
        else:
            result_text = f"<tool_error>{result['error']}</tool_error>"
        
        # Replace tool call with result
        injected = re.sub(
            self.tool_call_pattern,
            result_text,
            original_text,
            count=1,
            flags=re.DOTALL
        )
        
        return injected