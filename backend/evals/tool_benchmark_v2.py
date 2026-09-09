"""
Real end-to-end benchmark of the SLM tool-calling pipeline:
  <tool_call> text (as the model would emit it) -> ToolRouter.parse_tool_call
  -> ToolRegistry lookup -> tool.execute -> result injection

This does NOT require the LLM (Qwen) or the Gemini router API key -
it tests the tool infrastructure exactly as the agent would invoke it,
using realistic <tool_call> strings and known ground-truth answers.
"""
import sys, os, time, json, traceback
# NOTE: this used to insert the *evals/* directory itself, which put
# "backend/evals/src/tools/..." on the lookup path instead of
# "backend/src/tools/..." -- combined with the code_executor_v2 typo below,
# this script could not even be imported (ImportError on line 1 of main).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.tool_registry import tool_registry
from src.tools.tool_router import ToolRouter
from src.tools.sympy_solver import SymPySolver
from src.tools.numpy_calculator import NumpyCalculator
from src.tools.matplotlib_plotter import MatplotlibPlotter
from src.tools.code_executor import CodeExecutor  # was src.tools.code_executor_v2, which doesn't exist

# Register tools exactly as the app would
tool_registry.register(SymPySolver())
tool_registry.register(NumpyCalculator())
tool_registry.register(MatplotlibPlotter())
tool_registry.register(CodeExecutor())

router = ToolRouter()

# ---- Test cases: (description, raw <tool_call> text, checker function) ----
# checker(result_dict) -> (pass: bool, note: str)

def close(a, b, tol=1e-6):
    try:
        return abs(float(a) - float(b)) < tol
    except Exception:
        return False

test_cases = [
    # --- sympy_solver ---
    ("sympy: derivative of x^2", 
     '<tool_call>tool: sympy_solver\nparams: {"expression": "x**2", "operation": "derivative"}</tool_call>',
     lambda r: (r.get("result") == "2*x", f"expected 2*x, got {r.get('result')}")),

    ("sympy: integrate x^2 from 0 to 3",
     '<tool_call>tool: sympy_solver\nparams: {"expression": "x**2", "operation": "integrate", "bounds": [0,3]}</tool_call>',
     lambda r: (r.get("result") == "9", f"expected 9, got {r.get('result')}")),

    ("sympy: solve x^2 - 4 = 0",
     '<tool_call>tool: sympy_solver\nparams: {"expression": "x**2 - 4", "operation": "solve"}</tool_call>',
     lambda r: (r.get("result") in ("[-2, 2]", "[2, -2]"), f"expected [-2, 2], got {r.get('result')}")),

    ("sympy: simplify (x^2-1)/(x-1)",
     '<tool_call>tool: sympy_solver\nparams: {"expression": "(x**2 - 1)/(x - 1)", "operation": "simplify"}</tool_call>',
     lambda r: (r.get("result") == "x + 1", f"expected x + 1, got {r.get('result')}")),

    ("sympy: expand (x+2)^2",
     '<tool_call>tool: sympy_solver\nparams: {"expression": "(x+2)**2", "operation": "expand"}</tool_call>',
     lambda r: (r.get("result") == "x**2 + 4*x + 4", f"expected x**2 + 4*x + 4, got {r.get('result')}")),

    ("sympy: factor x^2 - 9",
     '<tool_call>tool: sympy_solver\nparams: {"expression": "x**2 - 9", "operation": "factor"}</tool_call>',
     lambda r: (r.get("result") == "(x - 3)*(x + 3)", f"expected (x - 3)*(x + 3), got {r.get('result')}")),

    ("sympy: malformed expression (should fail gracefully)",
     '<tool_call>tool: sympy_solver\nparams: {"expression": "x**2 +++ ", "operation": "simplify"}</tool_call>',
     None),  # expect failure -> tracked separately

    # --- numpy_calculator ---
    ("numpy: basic arithmetic 2+2*5",
     '<tool_call>tool: numpy_calculator\nparams: {"expression": "2+2*5"}</tool_call>',
     lambda r: (close(r.get("result"), 12), f"expected 12, got {r.get('result')}")),

    ("numpy: sqrt(144)",
     '<tool_call>tool: numpy_calculator\nparams: {"expression": "sqrt(144)"}</tool_call>',
     lambda r: (close(r.get("result"), 12), f"expected 12, got {r.get('result')}")),

    ("numpy: sin(pi/2)",
     '<tool_call>tool: numpy_calculator\nparams: {"expression": "sin(pi/2)"}</tool_call>',
     lambda r: (close(r.get("result"), 1.0), f"expected 1.0, got {r.get('result')}")),

    ("numpy: caret exponent 2^10",
     '<tool_call>tool: numpy_calculator\nparams: {"expression": "2^10"}</tool_call>',
     lambda r: (close(r.get("result"), 1024), f"expected 1024, got {r.get('result')}")),

    ("numpy: unsafe expression should be blocked",
     '<tool_call>tool: numpy_calculator\nparams: {"expression": "__import__(\'os\').system(\'echo pwned\')"}</tool_call>',
     None),  # security check, tracked separately

    # --- matplotlib_plotter ---
    ("matplotlib: plot x**2",
     '<tool_call>tool: matplotlib_plotter\nparams: {"function": "x**2", "x_range": [-5,5]}</tool_call>',
     lambda r: (isinstance(r.get("image_base64"), str) and len(r.get("image_base64","")) > 1000,
                "expected non-trivial base64 PNG")),

    ("matplotlib: plot sin(x)",
     '<tool_call>tool: matplotlib_plotter\nparams: {"function": "np.sin(x)"}</tool_call>',
     lambda r: (isinstance(r.get("image_base64"), str) and len(r.get("image_base64","")) > 1000,
                "expected non-trivial base64 PNG")),

    # --- code_executor ---
    ("code_exec: simple sum loop",
     '<tool_call>tool: code_executor\nparams: {"code": "result = sum(range(1,101))"}</tool_call>',
     lambda r: (r.get("result") == 5050, f"expected 5050, got {r.get('result')}")),

    ("code_exec: uses numpy in sandbox",
     '<tool_call>tool: code_executor\nparams: {"code": "result = float(np.mean([1,2,3,4,5]))"}</tool_call>',
     lambda r: (close(r.get("result"), 3.0), f"expected 3.0, got {r.get('result')}")),

    ("code_exec: attempt filesystem access (should fail - no builtins for it)",
     '<tool_call>tool: code_executor\nparams: {"code": "result = open(\'/etc/passwd\').read()"}</tool_call>',
     None),  # security check, tracked separately

    ("code_exec: object-introspection sandbox escape attempt",
     '<tool_call>tool: code_executor\nparams: {"code": "result = ().__class__.__bases__[0].__subclasses__()"}</tool_call>',
     None),  # security check, tracked separately
]

results = []
for desc, raw_call, checker in test_cases:
    entry = {"description": desc}
    t0 = time.perf_counter()
    try:
        parsed = router.parse_tool_call(raw_call)
        if parsed is None:
            entry.update(parse_ok=False, exec_ok=False, correct=False, note="failed to parse tool_call", latency_ms=None)
            results.append(entry)
            continue
        exec_result = router.execute_tool(parsed)
        latency_ms = (time.perf_counter() - t0) * 1000
        entry["parse_ok"] = True
        entry["exec_ok"] = exec_result.get("success", False)
        entry["latency_ms"] = round(latency_ms, 3)
        entry["raw_result"] = exec_result.get("result")

        if checker is None:
            # These are "should this fail / be blocked" cases
            entry["correct"] = None
            entry["security_note"] = (
                "BLOCKED (raised error, good)" if not exec_result["success"]
                else f"NOT BLOCKED - executed successfully: {exec_result.get('result')}"
            )
        else:
            ok, note = checker(exec_result.get("result", {}) if exec_result["success"] else {})
            entry["correct"] = ok if exec_result["success"] else False
            entry["note"] = note if exec_result["success"] else exec_result.get("error")
    except Exception as e:
        entry.update(parse_ok=False, exec_ok=False, correct=False, note=f"EXCEPTION: {e}", latency_ms=None)
    results.append(entry)

# ---- Aggregate metrics ----
functional_tests = [r for r in results if r["correct"] is not None]
security_tests = [r for r in results if r["correct"] is None]

n_functional = len(functional_tests)
n_correct = sum(1 for r in functional_tests if r["correct"])
n_parse_ok = sum(1 for r in results if r.get("parse_ok"))
n_exec_ok = sum(1 for r in results if r.get("exec_ok"))
latencies = [r["latency_ms"] for r in results if r.get("latency_ms") is not None]

print("="*70)
print("PER-TEST RESULTS")
print("="*70)
for r in results:
    status = "PASS" if r["correct"] else ("N/A" if r["correct"] is None else "FAIL")
    print(f"[{status:4}] {r['description']}")
    if r["correct"] is None:
        print(f"        -> {r.get('security_note')}")
    elif not r["correct"]:
        print(f"        -> {r.get('note')}")
    if r.get("latency_ms") is not None:
        print(f"        latency: {r['latency_ms']:.3f} ms")

print("\n" + "="*70)
print("AGGREGATE METRICS")
print("="*70)
print(f"Tool-call parse success rate:      {n_parse_ok}/{len(results)}  ({100*n_parse_ok/len(results):.1f}%)")
print(f"Tool execution success rate:       {n_exec_ok}/{len(results)}  ({100*n_exec_ok/len(results):.1f}%)")
print(f"Functional correctness (answer):   {n_correct}/{n_functional}  ({100*n_correct/n_functional:.1f}%)")
if latencies:
    avg = sum(latencies)/len(latencies)
    print(f"Avg tool latency:                  {avg:.3f} ms  (min {min(latencies):.3f}, max {max(latencies):.3f})")
print(f"\nSecurity probe results ({len(security_tests)} adversarial inputs):")
for r in security_tests:
    print(f"  - {r['description']}: {r.get('security_note')}")

# Save raw JSON for the record
with open("tool_benchmark_results.json", "w") as f:
    json.dump({
        "results": results,
        "summary": {
            "parse_success_rate": n_parse_ok/len(results),
            "exec_success_rate": n_exec_ok/len(results),
            "functional_accuracy": n_correct/n_functional,
            "avg_latency_ms": sum(latencies)/len(latencies) if latencies else None,
            "n_tests": len(results),
        }
    }, f, indent=2, default=str)
print("\nRaw results saved to tool_benchmark_results.json")
