"""Runs submitted code in a separate Python process, after a basic safety check."""

import ast
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Tuple

# input() is allowed: it only reads the text typed into the stdin box.
DANGEROUS_NAMES = {
    "__import__", "eval", "exec", "open", "compile", "globals", "locals", "vars", "breakpoint"
}
DANGEROUS_MODULES = {"os", "sys", "subprocess", "pathlib", "shutil", "socket", "ctypes", "resource", "multiprocessing"}

# The name shown in error messages instead of the temporary file's real path.
DISPLAY_NAME = "your_code.py"

# Stops Windows from flashing a console window for every run of the packaged app.
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class SafetyViolation(Exception):
    """Raised when submitted code uses something the checker does not allow."""


class InterpreterNotFound(Exception):
    """Raised when there is no Python available to run submitted code."""


class SafeChecker(ast.NodeVisitor):
    """Basic static checker to block imports and dangerous calls."""
    def visit_Import(self, node):
        raise SafetyViolation("Imports are not allowed.")
    def visit_ImportFrom(self, node):
        raise SafetyViolation("Imports are not allowed.")
    def visit_Call(self, node: ast.Call):
        # Block direct names
        if isinstance(node.func, ast.Name) and node.func.id in DANGEROUS_NAMES:
            raise SafetyViolation(f"Use of '{node.func.id}' is not allowed.")
        # Block dunder attribute calls and dangerous module attrs
        if isinstance(node.func, ast.Attribute):
            if node.func.attr.startswith("__"):
                raise SafetyViolation("Access to dunder attributes is not allowed.")
            if isinstance(node.func.value, ast.Name):
                base = node.func.value.id
                if base in DANGEROUS_MODULES:
                    raise SafetyViolation(f"Access to module '{base}' is not allowed.")
        self.generic_visit(node)

def static_safety_check(code: str) -> None:
    try:
        tree = ast.parse(code)
        SafeChecker().visit(tree)
    except SafetyViolation:
        raise
    except Exception:
        # Non-safety parse issues are deferred to runtime
        return

def python_command() -> List[str]:
    """Return the command that starts Python for running submitted code.

    Normally that is the interpreter running this app. In a build made with
    PyInstaller, sys.executable is the app's own program rather than Python, so
    the Python installed on the computer is used instead.
    """
    if not getattr(sys, "frozen", False):
        return [sys.executable]
    for candidate in (["py", "-3"], ["python"], ["python3"]):
        if shutil.which(candidate[0]):
            return candidate
    raise InterpreterNotFound(
        "Running code needs Python installed on this computer. "
        "Install it from https://www.python.org/downloads/ and try again."
    )

def _decode(data) -> str:
    return (data or b"").decode("utf-8", errors="replace")

def run_code_isolated(code: str, stdin: str = "", timeout: int = 3) -> Tuple[str, str, int, bool]:
    """
    Run code in an isolated Python process with a timeout.
    Returns stdout, stderr, returncode, timed_out
    """
    static_safety_check(code)
    command = python_command()

    # Saved as UTF-8 so every character in the code survives, whatever the
    # computer's default encoding is.
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tf:
        tf.write(code)
        file_path = tf.name

    try:
        try:
            proc = subprocess.run(
                # -I isolates the run from the user's Python settings, -B skips
                # .pyc files and -X utf8 makes input and output UTF-8 everywhere.
                command + ["-I", "-B", "-X", "utf8", file_path],
                input=stdin.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                creationflags=_NO_WINDOW,
            )
            stdout, stderr, returncode, timed_out = proc.stdout, proc.stderr, proc.returncode, False
        except subprocess.TimeoutExpired as e:
            stdout, stderr, returncode, timed_out = e.stdout, e.stderr, -9, True
    finally:
        try:
            os.unlink(file_path)
        except OSError:
            pass

    # Tracebacks read better with a plain file name than a long temporary path.
    return _decode(stdout), _decode(stderr).replace(file_path, DISPLAY_NAME), returncode, timed_out

def build_function_test_harness(student_code: str, function_name: str, tests: List[Dict[str, Any]]) -> str:
    static_safety_check(student_code)
    # The finished harness goes through static_safety_check again when it is
    # run, so it may only use what student code may use: no imports. Results
    # are printed with repr() and read back with ast.literal_eval().
    lines = [
        student_code,
        "",
        "def __run_tests__():",
        "    results = []",
    ]
    for idx, t in enumerate(tests):
        # repr() gives a valid Python literal whatever quotes the value contains.
        args_repr = repr(t["input_args"])
        expected = repr(t["expected_return"])
        name = repr(t["name"])
        lines += [
            f"    # Test {idx+1}: {name}",
            "    try:",
            f"        _res = {function_name}(*{args_repr})",
            f"        _ok = (_res == {expected})",
            f"        _msg = '' if _ok else 'expected ' + repr({expected}) + ', got ' + repr(_res)",
            "    except Exception as e:",
            "        _ok = False",
            "        _msg = 'exception: ' + repr(e)",
            f"    results.append({{'name': {name}, 'ok': _ok, 'message': _msg}})",
        ]
    lines += [
        "    print('__TEST_RESULTS__:' + repr(results))",
        "",
        "if __name__ == '__main__':",
        "    __run_tests__()",
    ]
    return "\n".join(lines)
