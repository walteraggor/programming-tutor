"""Tests for the safety check and for running code in a separate process."""

import os
import sys
import tempfile
import unittest
from unittest import mock

from backend import code_runner
from backend.code_runner import (
    InterpreterNotFound,
    SafetyViolation,
    build_function_test_harness,
    python_command,
    run_code_isolated,
    static_safety_check,
)


class SafetyCheckTests(unittest.TestCase):
    def assert_blocked(self, code):
        with self.assertRaises(SafetyViolation, msg=code):
            static_safety_check(code)

    def test_blocks_imports(self):
        self.assert_blocked("import os")
        self.assert_blocked("from os import path")
        self.assert_blocked("def f():\n    import json\n")

    def test_blocks_dangerous_calls(self):
        for code in ("open('x')", "eval('1')", "exec('x = 1')", "__import__('os')", "compile('1', 'f', 'eval')"):
            self.assert_blocked(code)

    def test_blocks_calls_to_dunder_attributes(self):
        self.assert_blocked("x = (1).__class__()")

    def test_allows_ordinary_code(self):
        static_safety_check(
            "class Point:\n"
            "    def __init__(self, x):\n"
            "        self.x = x\n"
            "for i in range(3):\n"
            "    print(Point(i).x, len('abc'), sorted([3, 1]))\n"
        )

    def test_allows_input(self):
        static_safety_check("name = input()\nprint(name)")

    def test_leaves_syntax_errors_for_python_to_report(self):
        # The checker only looks for unsafe code; broken code is reported when it runs.
        static_safety_check("def broken(:\n    pass")


class RunCodeTests(unittest.TestCase):
    def test_captures_what_the_code_prints(self):
        stdout, stderr, returncode, timed_out = run_code_isolated("print(6 * 7)")
        self.assertEqual(stdout.strip(), "42")
        self.assertEqual(stderr, "")
        self.assertEqual(returncode, 0)
        self.assertFalse(timed_out)

    def test_input_reads_the_stdin_text(self):
        code = "first = input()\nsecond = input()\nprint(second + ' ' + first)"
        stdout, _, returncode, _ = run_code_isolated(code, stdin="world\nhello\n")
        self.assertEqual(returncode, 0)
        self.assertEqual(stdout.strip(), "hello world")

    def test_errors_are_reported_with_a_readable_file_name(self):
        stdout, stderr, returncode, timed_out = run_code_isolated("print('before')\nprint(1 / 0)")
        self.assertNotEqual(returncode, 0)
        self.assertFalse(timed_out)
        self.assertEqual(stdout.strip(), "before")
        self.assertIn("ZeroDivisionError", stderr)
        self.assertIn(code_runner.DISPLAY_NAME, stderr)
        self.assertNotIn(tempfile.gettempdir(), stderr)

    def test_an_endless_loop_is_stopped(self):
        stdout, _, _, timed_out = run_code_isolated("print('started', flush=True)\nwhile True:\n    pass", timeout=1)
        self.assertTrue(timed_out)
        self.assertIn("started", stdout)

    def test_text_outside_ascii_survives_the_round_trip(self):
        code = "word = input()\nprint('caf\u00e9 \u2615 ' + word)"
        stdout, stderr, returncode, _ = run_code_isolated(code, stdin="na\u00efve \u65e5\u672c\n")
        self.assertEqual(stderr, "")
        self.assertEqual(returncode, 0)
        self.assertEqual(stdout.strip(), "caf\u00e9 \u2615 na\u00efve \u65e5\u672c")

    def test_unsafe_code_is_refused_before_it_runs(self):
        with self.assertRaises(SafetyViolation):
            run_code_isolated("import os\nprint('should never print')")

    def test_the_temporary_file_is_removed_afterwards(self):
        with tempfile.TemporaryDirectory() as folder:
            with mock.patch.object(tempfile, "tempdir", folder):
                run_code_isolated("print('hi')")
                run_code_isolated("while True:\n    pass", timeout=1)
            self.assertEqual(os.listdir(folder), [])


class PythonCommandTests(unittest.TestCase):
    def test_uses_this_python_when_run_from_source(self):
        self.assertEqual(python_command(), [sys.executable])

    def test_uses_the_installed_python_when_packaged(self):
        with mock.patch.object(sys, "frozen", True, create=True):
            with mock.patch("backend.code_runner.shutil.which", lambda name: "/usr/bin/python" if name == "python" else None):
                self.assertEqual(python_command(), ["python"])
            with mock.patch("backend.code_runner.shutil.which", lambda name: "C:\\Windows\\py.exe"):
                self.assertEqual(python_command(), ["py", "-3"])

    def test_says_so_when_packaged_and_no_python_is_installed(self):
        with mock.patch.object(sys, "frozen", True, create=True):
            with mock.patch("backend.code_runner.shutil.which", lambda name: None):
                with self.assertRaises(InterpreterNotFound):
                    python_command()
                with self.assertRaises(InterpreterNotFound):
                    run_code_isolated("print('hi')")


class HarnessTests(unittest.TestCase):
    def test_the_harness_passes_the_same_safety_check_as_student_code(self):
        harness = build_function_test_harness(
            "def echo(x):\n    return x\n",
            "echo",
            [{"name": "it's \"quoted\"", "input_args": ["a'b\"c"], "expected_return": "a'b\"c"}],
        )
        static_safety_check(harness)
        self.assertNotIn("import", harness)

    def test_unsafe_student_code_is_refused_when_the_harness_is_built(self):
        with self.assertRaises(SafetyViolation):
            build_function_test_harness("import os\n", "f", [])
