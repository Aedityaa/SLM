"""Initialize and register all tools"""
from src.tools.tool_registry import tool_registry
from src.tools.tool_router import ToolRouter

# Import all tools
from src.tools.symbolic.sympy_solver import SymPySolver
from src.tools.numerical.numpy_calculator import NumpyCalculator
from src.tools.visualization.matplotlib_plotter import MatplotlibPlotter
from src.tools.execution.code_executor import CodeExecutor

def initialize_tools():
    """Register all available tools"""
    # Register symbolic tools
    tool_registry.register(SymPySolver())
    
    # Register numerical tools
    tool_registry.register(NumpyCalculator())
    
    # Register visualization tools
    tool_registry.register(MatplotlibPlotter())
    
    # Register execution tools
    tool_registry.register(CodeExecutor())
    
    print("✅ All tools initialized!")
    print("📋 Available tools:", list(tool_registry.list_tools().keys()))

# Auto-initialize on import
initialize_tools()

__all__ = [
    'tool_registry',
    'ToolRouter',
    'initialize_tools'
]