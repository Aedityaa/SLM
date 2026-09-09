"""
Security regression test for the eval()/sympify() sandbox-escape fix in
numpy_calculator.py, matplotlib_plotter.py, and sympy_solver.py.

BACKGROUND: code_executor.py was previously hardened with RestrictedPython
because a plain `{"__builtins__": {}}` eval() does not stop the classic
object-introspection escape (walking `().__class__.__bases__[0]
.__subclasses__()` to reach a class with real __builtins__ access). That
same insecure eval()/sympify() pattern was still present, unfixed, in three
other tools that also evaluate model-generated expressions. This script
proves (a) the escape is blocked in all three now, and (b) legitimate
functionality is unaffected.

Run:
    cd backend && python evals/security_regression.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.numpy_calculator import NumpyCalculator
from src.tools.matplotlib_plotter import MatplotlibPlotter
from src.tools.sympy_solver import SymPySolver

ADVERSARIAL_PAYLOADS = [
    "__import__('os').system('echo PWNED_DIRECT')",
    "().__class__.__bases__[0].__subclasses__()",
    "[c for c in ().__class__.__bases__[0].__subclasses__() if c.__name__=='catch_warnings'][0]()._module.__builtins__['__import__']('os').system('echo PWNED_CHAIN')",
    "(1).__class__.__mro__[-1].__subclasses__()",
    "open('/etc/passwd').read()",
]

LEGIT_NUMPY = [
    ("2+2*5", 12.0), ("sqrt(144)", 12.0), ("sin(pi/2)", 1.0),
    ("2^10", 1024.0), ("cos(0)", 1.0), ("exp(1)", 2.718281828459045),
    ("log(e)", 1.0), ("abs(-5)", 5.0),
]

LEGIT_SYMPY = [
    ({"expression": "x**2", "operation": "derivative"}, "2*x"),
    ({"expression": "x**2", "operation": "integrate", "bounds": [0, 3]}, "9"),
    ({"expression": "(x**2 - 1)/(x - 1)", "operation": "simplify"}, "x + 1"),
    ({"expression": "(x+2)**2", "operation": "expand"}, "x**2 + 4*x + 4"),
    ({"expression": "x**2 - 9", "operation": "factor"}, "(x - 3)*(x + 3)"),
]

LEGIT_PLOTS = ["x**2", "np.sin(x)", "sin(x)"]


def main():
    nc, mp, ss = NumpyCalculator(), MatplotlibPlotter(), SymPySolver()
    failures = []

    print("=" * 70)
    print("SECURITY: adversarial payloads must be BLOCKED in all 3 tools")
    print("=" * 70)
    for tool_name, tool, kwarg in [
        ("numpy_calculator", nc, "expression"),
        ("sympy_solver", ss, "expression"),
        ("matplotlib_plotter", mp, "function"),
    ]:
        for p in ADVERSARIAL_PAYLOADS:
            kwargs = {kwarg: p}
            if tool_name == "sympy_solver":
                kwargs["operation"] = "simplify"
            r = tool(**kwargs)
            blocked = not r["success"]
            status = "BLOCKED" if blocked else f"NOT BLOCKED -> {r.get('result')}"
            print(f"[{'ok' if blocked else 'SECURITY FAIL'}] {tool_name}: {p[:55]!r}... -> {status}")
            if not blocked:
                failures.append(f"{tool_name} did not block: {p}")

    print("\n" + "=" * 70)
    print("FUNCTIONAL: legitimate expressions must still work")
    print("=" * 70)
    for expr, expected in LEGIT_NUMPY:
        r = nc(expression=expr)
        ok = r["success"] and abs(float(r["result"]["result"]) - expected) < 1e-6
        print(f"[{'PASS' if ok else 'FAIL'}] numpy_calculator: {expr}")
        if not ok:
            failures.append(f"numpy_calculator regressed on: {expr}")

    for params, expected in LEGIT_SYMPY:
        r = ss(**params)
        got = r["result"]["result"] if r["success"] else r.get("error")
        ok = r["success"] and got == expected
        print(f"[{'PASS' if ok else 'FAIL'}] sympy_solver: {params} -> {got}")
        if not ok:
            failures.append(f"sympy_solver regressed on: {params}")

    for func in LEGIT_PLOTS:
        r = mp(function=func, x_range=(-5, 5))
        ok = r["success"] and len(r["result"].get("image_base64", "")) > 1000
        print(f"[{'PASS' if ok else 'FAIL'}] matplotlib_plotter: function={func!r}")
        if not ok:
            failures.append(f"matplotlib_plotter regressed on: {func}")

    print("\n" + "=" * 70)
    if failures:
        print(f"RESULT: {len(failures)} FAILURE(S)")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("RESULT: all security probes blocked, all legit cases pass.")


if __name__ == "__main__":
    main()
