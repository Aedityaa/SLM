"""Matplotlib plotting tool

SECURITY NOTE: same eval(expr, {"__builtins__": {}}, ...) pattern as
numpy_calculator had -- see src/tools/safe_eval.py's module docstring for
why an empty __builtins__ doesn't stop the object-introspection sandbox
escape. Fixed the same way: AST whitelist before evaluation.
"""
import matplotlib
matplotlib.use("Agg")  # headless backend; avoid GUI backend issues on servers
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from src.tools.base_tool import BaseTool
from src.tools.safe_eval import safe_eval_numeric, UnsafeExpressionError
from typing import Dict, Any

class MatplotlibPlotter(BaseTool):
    """Create graphs and visualizations"""
    
    def __init__(self):
        super().__init__(
            name="matplotlib_plotter",
            description="Generate graphs: functions, scatter plots, histograms"
        )
    
    def execute(
        self,
        function: str,
        x_range: tuple = (-10, 10),
        plot_type: str = "line",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a plot
        
        Args:
            function: Function to plot (e.g., "x**2", "np.sin(x)")
            x_range: Range for x-axis
            plot_type: 'line', 'scatter', 'bar'
        """
        # Generate x values
        x = np.linspace(x_range[0], x_range[1], 500)
        
        # Evaluate function through the AST-whitelisted safe evaluator
        # (see src/tools/safe_eval.py) instead of raw eval().
        safe_namespace = {
            'x': x,
            'np': np,
            'sin': np.sin,
            'cos': np.cos,
            'sqrt': np.sqrt,
            'exp': np.exp,
            'log': np.log,
        }
        try:
            y = safe_eval_numeric(function, safe_namespace, allow_np_attr=True)
        except UnsafeExpressionError as e:
            raise ValueError(f"Rejected unsafe expression: {e}") from e

        # plt.figure() is created before we know savefig will succeed; wrap
        # everything after it in try/finally so a bad function (e.g. one
        # that raises mid-plot) can't leak a figure across requests.
        plt.figure(figsize=(10, 6))
        try:
            if plot_type == "line":
                plt.plot(x, y, linewidth=2)
            elif plot_type == "scatter":
                plt.scatter(x, y)

            plt.xlabel('x', fontsize=12)
            plt.ylabel('y', fontsize=12)
            plt.title(f'Plot of {function}', fontsize=14)
            plt.grid(True, alpha=0.3)

            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)

            # Encode to base64
            image_base64 = base64.b64encode(buffer.read()).decode()
        finally:
            plt.close()

        return {
            "function": function,
            "x_range": x_range,
            "image_base64": image_base64,
            "plot_type": plot_type
        }
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format for model injection"""
        return f"Generated plot for: {result['function']}"