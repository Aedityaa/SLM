"""NumPy-based numerical calculator

SECURITY NOTE: this used to do eval(expr, {"__builtins__": {}}, safe_namespace).
Emptying __builtins__ blocks direct calls like open()/__import__(), but not
the classic object-introspection sandbox escape (e.g.
`().__class__.__bases__[0].__subclasses__()` -> walk to a class that still
has real __builtins__ access, e.g. warnings.catch_warnings -> arbitrary code
execution). That escape needs no builtins at all, so the old guard didn't
touch it. See src/tools/safe_eval.py for the fix: an AST whitelist rejects
attribute/subscript access entirely (except a tightly-scoped np.<fn> form),
so the escape's syntax can't even be parsed, let alone executed.
"""
import numpy as np
from src.tools.base_tool import BaseTool
from src.tools.safe_eval import safe_eval_numeric, UnsafeExpressionError
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
        
        # Evaluate through the AST-whitelisted safe evaluator (see
        # src/tools/safe_eval.py) instead of raw eval().
        try:
            result = safe_eval_numeric(expression, self.safe_namespace, allow_np_attr=True)
        except UnsafeExpressionError as e:
            raise ValueError(f"Rejected unsafe expression: {e}") from e
        
        return {
            "expression": expression,
            "result": float(result) if np.isscalar(result) else result.tolist(),
            "type": type(result).__name__
        }
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format for model injection"""
        return f"{result['expression']} = {result['result']}"