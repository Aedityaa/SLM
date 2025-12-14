"""Examples of using the solver with tools"""
from src.generation.inference import MathSolverInference

# Initialize solver with tools
solver = MathSolverInference(
    lora_adapter_path="./models/lora_adapter",
    enable_tools=True
)

# Example 1: Integration (will use sympy_solver)
print("=" * 60)
print("Example 1: Integration")
result = solver.solve(
    "Integrate x^2 + 3x from 0 to 5",
    use_tools=True
)
print(f"Problem: {result['problem']}")
print(f"Tools used: {[tc['tool'] for tc in result['tool_calls']]}")
print(f"Solution: {result['solution']}")
print(f"Final answer: {result['final_answer']}")


# Example 2: Numerical calculation
print("\n" + "=" * 60)
print("Example 2: Numerical Calculation")
result = solver.solve(
"Calculate sin(π/2) + cos(0) * e^2",
use_tools=True
)
print(f"Tools used: {[tc['tool'] for tc in result['tool_calls']]}")
print(f"Final answer: {result['final_answer']}")


#Example 3: Without tools (pure LLM)
print("\n" + "=" * 60)
print("Example 3: Without Tools")
result = solver.solve(
"What is 2+2?",
use_tools=False
)
print(f"Tools used: {result['tools_used']}")
print(f"Solution: {result['solution']}")


