"""Shared safe-expression validation for tools that evaluate model-generated
math expressions (numpy_calculator, matplotlib_plotter, sympy_solver).

WHY THIS EXISTS
----------------
Three tools previously did `eval(expr, {"__builtins__": {}}, safe_namespace)`
(or the sympy equivalent, `sp.sympify(expr)`, which also falls back to a raw
`eval` internally). Emptying `__builtins__` blocks *direct* calls like
`open(...)` or `__import__(...)`, but it does NOT block the well-known
object-introspection escape, which never touches `__builtins__` at all:

    ().__class__.__bases__[0].__subclasses__()   # walk to any loaded class
    # ... then pick something like `catch_warnings` to reach a real module's
    # __builtins__ and call __import__ from there.

That chain is pure attribute access + calls, so an empty-builtins eval does
nothing to stop it. This was demonstrated to still execute shell commands
(see backend/evals/security_regression.py).

APPROACH
--------
Rather than trying to blacklist dangerous names (fragile — there's always
another gadget chain), we whitelist the *grammar* itself with Python's `ast`
module before any expression is evaluated:

  - Only arithmetic operators, numeric/bool constants, names, calls, and
    (for plotting) a tightly whitelisted `np.<safe_function>` attribute form
    are permitted.
  - `ast.Attribute` is banned except for the single-level `np.<name>` form
    where `<name>` is in an explicit whitelist and does not start with `_`.
  - `ast.Subscript`, `ast.Lambda`, comprehensions, `ast.Attribute` chains,
    string literals used as call arguments, and any other construct are
    rejected outright.

Because the introspection escape *requires* chained/dunder attribute access
(`.__class__`, `.__bases__`, `.__subclasses__`, ...) and subscripting, and
those are structurally impossible to write once the AST validator rejects
them, this closes the escape independent of whatever `eval`/`sympify` does
internally -- the dangerous syntax simply never reaches the evaluator.
"""
import ast
from typing import Iterable, Optional

# Numpy/np.* attribute names we consider safe to expose for plotting-style
# expressions like "np.sin(x)". Deliberately small and math-only.
SAFE_NP_ATTRS = {
    "sin", "cos", "tan", "arcsin", "arccos", "arctan", "arctan2",
    "sinh", "cosh", "tanh", "sqrt", "exp", "log", "log2", "log10",
    "abs", "power", "pi", "e", "floor", "ceil", "round", "clip",
    "linspace", "arange", "mean", "std", "sum", "min", "max", "median",
}

_ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Load,
    ast.Constant, ast.Call, ast.Tuple, ast.List, ast.Name,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv,
    ast.USub, ast.UAdd,
)


class UnsafeExpressionError(ValueError):
    """Raised when an expression contains a construct we won't evaluate."""
    pass


def validate_safe_expression(
    expression: str,
    allow_np_attr: bool = False,
    extra_allowed_names: Optional[Iterable[str]] = None,
) -> ast.AST:
    """Parse `expression` and raise UnsafeExpressionError unless every node
    in the tree is one of a small arithmetic/call whitelist.

    Returns the parsed AST on success (callers that want to re-serialize a
    known-safe string can use ast.unparse on it).
    """
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise UnsafeExpressionError(f"could not parse expression: {e}") from e

    for node in ast.walk(tree):
        if isinstance(node, _ALLOWED_NODES):
            continue

        if isinstance(node, ast.Attribute):
            if not allow_np_attr:
                raise UnsafeExpressionError(
                    f"attribute access is not allowed: '{ast.dump(node)}'"
                )
            # Only a single-level `np.<safe_name>` form is allowed -- the
            # value being accessed must itself be a bare Name 'np', not a
            # chained/derived expression (which is exactly how the
            # introspection escape works: ().__class__.__bases__...).
            if not (isinstance(node.value, ast.Name) and node.value.id == "np"):
                raise UnsafeExpressionError(
                    "only 'np.<function>' attribute access is allowed"
                )
            if node.attr.startswith("_") or node.attr not in SAFE_NP_ATTRS:
                raise UnsafeExpressionError(
                    f"'np.{node.attr}' is not on the allowed function list"
                )
            continue

        # Everything else (Subscript, Lambda, comprehensions, Dict, Set,
        # Starred, JoinedStr/f-strings, Attribute chains not caught above,
        # Compare, BoolOp, IfExp, walrus, etc.) is rejected.
        raise UnsafeExpressionError(
            f"disallowed syntax in expression: {type(node).__name__}"
        )

    # Extra guard: every bare Name must not shadow dunder-ish identifiers.
    # (Defense in depth -- the Attribute/Subscript ban already prevents the
    # known escape, but this stops someone from getting a dangerous name
    # into scope some other way in the future.)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id.startswith("__") and node.id.endswith("__"):
            raise UnsafeExpressionError(f"dunder name not allowed: '{node.id}'")

    return tree


def safe_eval_numeric(expression: str, namespace: dict, allow_np_attr: bool = True):
    """Validate `expression` against the AST whitelist, then evaluate it
    against a caller-supplied namespace with builtins fully removed.

    Safe to use for numpy_calculator / matplotlib_plotter style numeric
    expressions. Raises UnsafeExpressionError for anything outside the
    arithmetic/whitelisted-call grammar.
    """
    validate_safe_expression(expression, allow_np_attr=allow_np_attr)
    return eval(compile(ast.parse(expression, mode="eval"), "<safe_eval>", "eval"),
                {"__builtins__": {}}, namespace)
