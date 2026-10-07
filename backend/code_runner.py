import ast
import subprocess
import sys
import tempfile
from typing import Tuple, List, Dict, Any

DANGEROUS_NAMES = {
    "__import__", "eval", "exec", "open", "compile", "input", "globals", "locals", "vars", "breakpoint"
}
DANGEROUS_MODULES = {"os", "sys", "subprocess", "pathlib", "shutil", "socket", "ctypes", "resource", "multiprocessing"}

class SafetyViolation(Exception):
    pass

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

def run_code_isolated(code: str, stdin: str = "", timeout: int = 3) -> Tuple[str, str, int, bool]:
    """
    Run code in an isolated Python process with a timeout.
    Returns stdout, stderr, returncode, timed_out
    """
    static_safety_check(code)

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
        tf.write(code)
        tf.flush()
        file_path = tf.name

    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-B", file_path],
            input=stdin.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout
        )
        return proc.stdout.decode("utf-8", errors="replace"), proc.stderr.decode("utf-8", errors="replace"), proc.returncode, False
    except subprocess.TimeoutExpired as e:
        stdout = (e.stdout or b"").decode("utf-8", errors="replace")
        stderr = (e.stderr or b"").decode("utf-8", errors="replace")
        return stdout, stderr, -9, True

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
            f"    try:",
            f"        _res = {function_name}(*{args_repr})",
            f"        _ok = (_res == {expected})",
            f"        _msg = '' if _ok else 'expected ' + repr({expected}) + ', got ' + repr(_res)",
            f"    except Exception as e:",
            f"        _ok = False",
            f"        _msg = 'exception: ' + repr(e)",
            f"    results.append({{'name': {name}, 'ok': _ok, 'message': _msg}})",
        ]
    lines += [
        "    print('__TEST_RESULTS__:' + repr(results))",
        "",
        "if __name__ == '__main__':",
        "    __run_tests__()",
    ]
    return "\n".join(lines)

def build_stdin_stdout_harness(code: str, testcases: List[Dict[str, Any]]) -> str:
    """
    For stdin/stdout style tasks: we run student's program as-is (no function call).
    We'll pass the stdin via process input and compare stdout lines externally in services.
    For simplicity, this util returns the code: the service will run code per test with given stdin.
    """
    static_safety_check(code)
    return code