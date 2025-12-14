"""Prompt templates with tool calling instructions"""

class PromptTemplate:
    """Manages system prompts and message formatting"""
    
    SYSTEM_PROMPTS = {
        "default": "Solve the math problem below. Provide only the reasoning and the final answer.",
        
        "with_tools": """Solve the math problem below. You have access to mathematical tools that you can call.

Available tools:
- sympy_solver: For symbolic math (derivatives, integrals, equations)
- numpy_calculator: For numerical calculations
- matplotlib_plotter: For creating graphs
- code_executor: For custom Python code

To use a tool, format your request as:
<tool_call>
tool: tool_name
params: {"param1": "value1", "param2": "value2"}
</tool_call>

Example:
<tool_call>
tool: sympy_solver
params: {"expression": "x**2 + 3*x", "operation": "integrate", "variable": "x", "bounds": [0, 5]}
</tool_call>

After receiving tool results, continue solving the problem. Provide clear reasoning and the final answer.""",
        
        "step_by_step": "Solve the math problem below step by step. Show all your work and explain each step clearly.",
        
        "concise": "Solve the math problem below. Provide only the final answer with minimal explanation.",
    }
    
    @staticmethod
    def create_messages(user_query, system_prompt="default"):
        """Create formatted messages for the model"""
        if system_prompt in PromptTemplate.SYSTEM_PROMPTS:
            system_content = PromptTemplate.SYSTEM_PROMPTS[system_prompt]
        else:
            system_content = system_prompt
        
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_query}
        ]