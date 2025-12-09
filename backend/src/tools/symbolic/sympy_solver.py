"""SymPy integration for symbolic mathematics"""
import sympy as sp
from src.tools.base_tool import BaseTool
from typing import Dict, Any

class SymPySolver(BaseTool):
    """Symbolic mathematics using SymPy"""
    
    def __init__(self):
        super().__init__(
            name="sympy_solver",
            description="Solve symbolic math: derivatives, integrals, equations, simplification"
        )
    
    def execute(self, expression: str, operation: str = "simplify", **kwargs) -> Dict[str, Any]:
        """
        Execute symbolic operation
        
        Args:
            expression: Math expression as string
            operation: One of ['simplify', 'derivative', 'integrate', 'solve', 'expand']
            **kwargs: Additional parameters (e.g., variable='x', bounds=(0,5))
        """
        # Parse expression
        expr = sp.sympify(expression)
        
        if operation == "simplify":
            result = sp.simplify(expr)
        
        elif operation == "derivative":
            var = sp.Symbol(kwargs.get('variable', 'x'))
            result = sp.diff(expr, var)
        
        elif operation == "integrate":
            var = sp.Symbol(kwargs.get('variable', 'x'))
            bounds = kwargs.get('bounds', None)
            
            if bounds:
                result = sp.integrate(expr, (var, bounds[0], bounds[1]))
            else:
                result = sp.integrate(expr, var)
        
        elif operation == "solve":
            var = sp.Symbol(kwargs.get('variable', 'x'))
            result = sp.solve(expr, var)
        
        elif operation == "expand":
            result = sp.expand(expr)
        
        elif operation == "factor":
            result = sp.factor(expr)
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        return {
            "expression": str(expr),
            "operation": operation,
            "result": str(result),
            "latex": sp.latex(result) if hasattr(sp, 'latex') else str(result)
        }
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format for model injection"""
        return f"{result['operation']}({result['expression']}) = {result['result']}"