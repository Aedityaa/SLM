"""Safe Python code execution.

SECURITY NOTE (why this was rewritten):
The original implementation only restricted __builtins__ to a hand-picked
whitelist. That blocks obvious escapes (open, __import__, eval) but does NOT
block Python's object-introspection escapes -- e.g. reaching system access
through an object's class/subclass chain rather than through a builtin
function. A builtins whitelist alone is a well-known insufficient sandbox.

This version uses RestrictedPython, which compiles code with attribute-access
guards and restricted AST nodes, closing that class of escape. It's still not
a substitute for OS-level isolation (a container / subprocess with resource
limits) if this were ever exposed to fully untrusted/adversarial users -- but
it's a meaningful, standard improvement over a hand-rolled whitelist for a
tool that executes model-generated code.
"""
from src.tools.base_tool import BaseTool
from typing import Dict, Any
import sys
import math
import numpy as np
from io import StringIO

from RestrictedPython import compile_restricted, safe_globals
from RestrictedPython.Guards import (
    safe_builtins,
    guarded_iter_unpack_sequence,
    full_write_guard,
)
from RestrictedPython.Eval import default_guarded_getiter, default_guarded_getitem


class CodeExecutor(BaseTool):
    """Execute Python code in a restricted sandbox (RestrictedPython)."""

    def __init__(self, timeout_seconds: float = 5.0):
        super().__init__(
            name="code_executor",
            description="Execute Python code for custom calculations"
        )
        self.timeout_seconds = timeout_seconds

        # Extra callables we deliberately allow beyond RestrictedPython's
        # own safe_builtins (which already includes things like abs, len,
        # range, etc.) -- these are common needs for math-tool code.
        self._extra_builtins = {
            'float': float, 'int': int, 'str': str, 'round': round,
            'list': list, 'dict': dict, 'tuple': tuple, 'bool': bool,
            'sorted': sorted, 'enumerate': enumerate, 'zip': zip,
            'sum': sum, 'min': min, 'max': max, 'abs': abs, 'len': len,
            'range': range, 'print': print,
        }

    def _build_restricted_globals(self):
        g = dict(safe_globals)
        g['__builtins__'] = dict(safe_builtins)
        g['__builtins__'].update(self._extra_builtins)
        g['_getiter_'] = default_guarded_getiter
        g['_getitem_'] = default_guarded_getitem
        g['_iter_unpack_sequence_'] = guarded_iter_unpack_sequence
        g['_write_'] = full_write_guard
        # Whitelisted modules -- deliberately small. Anything needing file,
        # network, subprocess, or os access is out of scope for this tool
        # by design, not by oversight.
        g['np'] = np
        g['math'] = math
        return g

    def _run_with_timeout(self, byte_code, restricted_globals, local_ns):
        """Run compiled code with a wall-clock timeout so a runaway loop
        (accidental or adversarial) can't hang the whole request."""
        import signal

        def _handler(signum, frame):
            raise TimeoutError(f"code_executor exceeded {self.timeout_seconds}s timeout")

        # signal-based timeout only works on the main thread in Unix; if this
        # tool is ever called from a worker thread, swap this for a
        # subprocess-based timeout instead.
        old_handler = signal.signal(signal.SIGALRM, _handler)
        signal.setitimer(signal.ITIMER_REAL, self.timeout_seconds)
        try:
            exec(byte_code, restricted_globals, local_ns)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old_handler)

    def execute(self, code: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Python code in a RestrictedPython sandbox with a timeout.

        Args:
            code: Python code to execute
        """
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        try:
            byte_code = compile_restricted(code, filename='<code_executor>', mode='exec')
        except SyntaxError as e:
            sys.stdout = old_stdout
            raise RuntimeError(f"code_executor rejected code (syntax/restricted construct): {e}") from e

        restricted_globals = self._build_restricted_globals()
        local_ns: Dict[str, Any] = {}

        try:
            self._run_with_timeout(byte_code, restricted_globals, local_ns)
            output = captured_output.getvalue()
            result_value = local_ns.get('result', None)

            return {
                "code": code,
                "output": output,
                "result": result_value,
                "variables": {k: str(v) for k, v in local_ns.items()
                              if not k.startswith('_')}
            }
        except Exception as e:
            # Propagate as a real failure -- do not swallow errors as a
            # "successful" call with a None result.
            raise RuntimeError(f"code_executor failed: {e}") from e
        finally:
            sys.stdout = old_stdout

    def format_result(self, result: Dict[str, Any]) -> str:
        """Format for model injection"""
        if 'error' in result:
            return f"Error: {result['error']}"
        return f"Output: {result['output']}\nResult: {result.get('result', 'None')}"
