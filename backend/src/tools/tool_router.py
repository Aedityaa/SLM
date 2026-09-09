"""Routes tool calls to appropriate tools"""
import json
import re
from typing import Dict, Any, Optional
from src.tools.tool_registry import tool_registry

class ToolRouter:
    """Routes and executes tool calls from model output"""
    
    def __init__(self):
        self.tool_call_pattern = r'<tool_call>(.*?)</tool_call>'
        self.tool_name_pattern = r'tool:\s*(\w+)'
        # NOTE: params are no longer extracted with a regex (see
        # _extract_params_json below). A non-greedy `{.*?}` silently breaks
        # on (a) nested JSON objects in params -- stops at the first `}` --
        # and (b) multi-line/pretty-printed JSON, since `.` doesn't match
        # newlines without re.DOTALL. Both are realistic model outputs
        # (nested params like {"bounds": {...}}, or a model that
        # pretty-prints JSON), and both used to fail SILENTLY: parse_tool_call
        # would return params={} with no error, so the tool ran with no
        # arguments instead of the agent knowing the call failed to parse.

    def _extract_params_json(self, tool_call_content: str) -> Dict[str, Any]:
        """Find the `params: { ... }` block and extract its JSON by
        scanning for the matching closing brace (handles nesting and
        multi-line JSON), instead of a regex that can't balance braces."""
        marker_match = re.search(r'params:\s*{', tool_call_content)
        if not marker_match:
            return {}

        start = marker_match.end() - 1  # position of the opening '{'
        depth = 0
        i = start
        in_string = False
        escape = False
        while i < len(tool_call_content):
            ch = tool_call_content[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    in_string = False
            else:
                if ch == '"':
                    in_string = True
                elif ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
            i += 1
        else:
            return {}  # never balanced -- truncated/malformed

        raw_json = tool_call_content[start:i]
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError:
            return {}

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
        
        # Extract parameters (if any) -- brace-balanced, newline-safe.
        params = self._extract_params_json(tool_call_content)
        
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