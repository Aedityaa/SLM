"""NumPy-based numerical calculator"""
import numpy as np
from src.tools.base_tool import BaseTool
from typing import Dict, Any

class NumpyCalculator(BaseTool):
    """Numerical computations using NumPy"""
    
    def __init__(self):
        super().__init__(
            name="numpy_calculator",
            description="Numerical calculations: arithmetic, trigonometry, statistics"
        )
        
        # Safe namespace for eval
        self.safe_namespace = {
            'np': np,
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'sqrt': np.sqrt,
            'log': np.log,
            'exp': np.exp,
            'abs': np.abs,
            'pi': np.pi,
            'e': np.e,
        }
    
    def execute(self, expression: str, **kwargs) -> Dict[str, Any]:
        """
        Evaluate numerical expression
        
        Args:
            expression: Mathematical expression
        """
        # Replace common notations
        expression = expression.replace('^', '**')
        
        # Evaluate safely
        result = eval(expression, {"__builtins__": {}}, self.safe_namespace)
        
        return {
            "expression": expression,
            "result": float(result) if np.isscalar(result) else result.tolist(),
            "type": type(result).__name__
        }
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format for model injection"""
        return f"{result['expression']} = {result['result']}"