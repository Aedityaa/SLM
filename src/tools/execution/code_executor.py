"""Safe Python code execution"""
from src.tools.base_tool import BaseTool
from typing import Dict, Any
import sys
from io import StringIO

class CodeExecutor(BaseTool):
    """Execute Python code safely"""
    
    def __init__(self):
        super().__init__(
            name="code_executor",
            description="Execute Python code for custom calculations"
        )
        
        # Safe built-ins
        self.safe_builtins = {
            'abs': abs,
            'max': max,
            'min': min,
            'sum': sum,
            'len': len,
            'range': range,
            'print': print,
        }
    
    def execute(self, code: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Python code in sandboxed environment
        
        Args:
            code: Python code to execute
        """
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        # Safe namespace
        namespace = {
            '__builtins__': self.safe_builtins,
            'np': __import__('numpy'),
            'math': __import__('math'),
        }
        
        try:
            # Execute code
            exec(code, namespace)
            
            # Get output
            output = captured_output.getvalue()
            
            # Get result if 'result' variable exists
            result_value = namespace.get('result', None)
            
            return {
                "code": code,
                "output": output,
                "result": result_value,
                "variables": {k: str(v) for k, v in namespace.items() 
                            if not k.startswith('_')}
            }
        
        except Exception as e:
            return {
                "code": code,
                "error": str(e),
                "output": captured_output.getvalue()
            }
        
        finally:
            sys.stdout = old_stdout
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format for model injection"""
        if 'error' in result:
            return f"Error: {result['error']}"
        return f"Output: {result['output']}\nResult: {result.get('result', 'None')}"