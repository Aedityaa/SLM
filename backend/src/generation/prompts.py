"""Prompt templates with tool calling instructions"""

class PromptTemplate:
    """Manages system prompts and message formatting"""
    
    SYSTEM_PROMPTS = {
        "default": "Solve the math problem below. Provide only the reasoning and the final answer.",
        
        "with_tools": """Solve the math problem below. You have access to mathematical tools that you can call.

Available tools:
- sympy_solver: For symbolic math (derivatives, integrals, equations, simplification)
  Example: derivatives, integrals, solve equations, expand/factor expressions
  
- numpy_calculator: For numerical calculations
  Example: trigonometry, arithmetic, square roots, exponentials
  
- matplotlib_plotter: For creating graphs and visualizations
  Example: plot functions, scatter plots, bar charts
  
- code_executor: For custom Python code execution
  Example: loops, custom algorithms, complex calculations
  
- wolfram_alpha: For advanced computations and real-world data (if enabled)
  Example: physics constants, unit conversions, complex symbolic math, scientific data
  Use this when other tools are insufficient or for real-world information

To use a tool, format your request as:
<tool_call>
tool: tool_name
params: {"param1": "value1", "param2": "value2"}
</tool_call>

Examples:

Integration with SymPy:
<tool_call>
tool: sympy_solver
params: {"expression": "x**2 + 3*x", "operation": "integrate", "variable": "x", "bounds": [0, 5]}
</tool_call>

Numerical calculation:
<tool_call>
tool: numpy_calculator
params: {"expression": "sin(pi/4) * sqrt(2)"}
</tool_call>

Query Wolfram Alpha:
<tool_call>
tool: wolfram_alpha
params: {"query": "integrate x^2 from 0 to 5"}
</tool_call>

After receiving tool results, continue solving the problem. Provide clear reasoning and the final answer.""",
        
        "step_by_step": "Solve the math problem below step by step. Show all your work and explain each step clearly.",
        
        "concise": "Solve the math problem below. Provide only the final answer with minimal explanation.",
    }
    
    @staticmethod
    def create_messages(user_query: str, system_prompt: str = "default") -> list:
        """Create formatted messages for the model"""
        if system_prompt in PromptTemplate.SYSTEM_PROMPTS:
            system_content = PromptTemplate.SYSTEM_PROMPTS[system_prompt]
        else:
            system_content = system_prompt
        
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_query}
        ]