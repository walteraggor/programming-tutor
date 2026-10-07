"""Tests that every challenge can be solved, and that grading explains failures."""

import unittest

from backend.models import Challenge, ChallengeTest
from backend.repository import CHALLENGES
from backend.services import RunService

# A correct answer for every challenge. If a challenge's tests are ever wrong
# (as Char Frequency's once were), its answer here stops passing.
SOLUTIONS = {
    "ch_add_01": "def add(a, b):\n    return a + b\n",
    "ch_pal_02": (
        "def is_palindrome(s):\n"
        "    letters = ''.join(s.lower().split())\n"
        "    return letters == letters[::-1]\n"
    ),
    "ch_rev_03": "def reverse_str(s):\n    return s[::-1]\n",
    "ch_unique_04": (
        "def unique_list(lst):\n"
        "    seen = []\n"
        "    for item in lst:\n"
        "        if item not in seen:\n"
        "            seen.append(item)\n"
        "    return seen\n"
    ),
    "ch_freq_05": (
        "def char_freq(s):\n"
        "    counts = {}\n"
        "    for char in s:\n"
        "        counts[char] = counts.get(char, 0) + 1\n"
        "    return counts\n"
    ),
    "ch_sum_06": "def sum_positives(lst):\n    return sum(n for n in lst if n > 0)\n",
    "ch_isprime_07": (
        "def is_prime(n):\n"
        "    if n < 2:\n"
        "        return False\n"
        "    divisor = 2\n"
        "    while divisor * divisor <= n:\n"
        "        if n % divisor == 0:\n"
        "            return False\n"
        "        divisor += 1\n"
        "    return True\n"
    ),
    "ch_fizz_08": (
        "def fizzbuzz(n):\n"
        "    result = []\n"
        "    for i in range(1, n + 1):\n"
        "        if i % 15 == 0:\n"
        "            result.append('FizzBuzz')\n"
        "        elif i % 3 == 0:\n"
        "            result.append('Fizz')\n"
        "        elif i % 5 == 0:\n"
        "            result.append('Buzz')\n"
        "        else:\n"
        "            result.append(i)\n"
        "    return result\n"
    ),
    "ch_anagram_09": (
        "def is_anagram(a, b):\n"
        "    def letters(word):\n"
        "        return sorted(word.replace(' ', '').lower())\n"
        "    return letters(a) == letters(b)\n"
    ),
    "ch_balance_10": (
        "def is_balanced(s):\n"
        "    pairs = {')': '(', ']': '[', '}': '{'}\n"
        "    stack = []\n"
        "    for char in s:\n"
        "        if char in '([{':\n"
        "            stack.append(char)\n"
        "        elif char in pairs:\n"
        "            if not stack or stack.pop() != pairs[char]:\n"
        "                return False\n"
        "    return not stack\n"
    ),
    "ch_double_11": "n = int(input())\nprint(n * 2)\n",
    "ch_greet_12": "name = input()\nprint('Hello, ' + name + '!')\n",
}


def find(challenge_id):
    return next(c for c in CHALLENGES if c.id == challenge_id)


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.runner = RunService()

    def test_ids_are_unique(self):
        ids = [c.id for c in CHALLENGES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_challenge_has_a_reference_solution(self):
        self.assertEqual(set(SOLUTIONS), {c.id for c in CHALLENGES})

    def test_every_challenge_has_tests_of_a_known_kind(self):
        for challenge in CHALLENGES:
            with self.subTest(challenge=challenge.id):
                self.assertTrue(challenge.tests)
                for test in challenge.tests:
                    self.assertIn(test.kind, ("function", "stdin_stdout"))
                if any(t.kind == "function" for t in challenge.tests):
                    self.assertTrue(challenge.function_name)

    def test_a_correct_solution_passes_every_challenge(self):
        for challenge in CHALLENGES:
            with self.subTest(challenge=challenge.id):
                result = self.runner.run_challenge_tests(challenge, SOLUTIONS[challenge.id])
                self.assertTrue(result.ok, f"{result.tests_summary} {result.stderr}")
                self.assertEqual(len(result.tests_summary), len(challenge.tests))

    def test_the_starter_code_does_not_pass(self):
        for challenge in CHALLENGES:
            with self.subTest(challenge=challenge.id):
                result = self.runner.run_challenge_tests(challenge, challenge.starter_code)
                self.assertFalse(result.ok)
                # It still runs, and reports on every test rather than crashing.
                self.assertEqual(len(result.tests_summary), len(challenge.tests))


class FunctionChallengeTests(unittest.TestCase):
    def setUp(self):
        self.runner = RunService()
        self.add = find("ch_add_01")

    def test_a_wrong_answer_says_what_was_expected(self):
        result = self.runner.run_challenge_tests(self.add, "def add(a, b):\n    return a - b\n")
        self.assertFalse(result.ok)
        self.assertEqual(result.tests_summary[0], {"name": "small ints", "ok": False, "message": "expected 5, got -1"})

    def test_an_import_is_reported_instead_of_raising(self):
        result = self.runner.run_challenge_tests(self.add, "import os\ndef add(a, b):\n    return a + b\n")
        self.assertFalse(result.ok)
        self.assertEqual(result.stderr, "Imports are not allowed.")
        self.assertEqual(result.tests_summary, [])

    def test_a_trailing_decorator_cannot_smuggle_code_past_the_check(self):
        # On its own this is a syntax error, so only the finished harness can be checked.
        result = self.runner.run_challenge_tests(self.add, "import os\ndef add(a, b):\n    return a + b\n@print\n")
        self.assertFalse(result.ok)
        self.assertIn("Imports are not allowed.", result.stderr)

    def test_a_syntax_error_is_shown(self):
        result = self.runner.run_challenge_tests(self.add, "def add(a, b)\n    return a + b\n")
        self.assertFalse(result.ok)
        self.assertIn("SyntaxError", result.stderr)
        self.assertEqual(result.tests_summary, [])

    def test_an_error_inside_the_function_is_reported_for_each_test(self):
        result = self.runner.run_challenge_tests(self.add, "def add(a, b):\n    return a / 0\n")
        self.assertFalse(result.ok)
        self.assertEqual(len(result.tests_summary), 3)
        self.assertTrue(result.tests_summary[0]["message"].startswith("exception: ZeroDivisionError"))

    def test_an_endless_loop_times_out(self):
        result = self.runner.run_challenge_tests(self.add, "def add(a, b):\n    while True:\n        pass\n", timeout=1)
        self.assertTrue(result.timed_out)
        self.assertFalse(result.ok)

    def test_printing_inside_a_solution_does_not_break_grading(self):
        code = "def add(a, b):\n    print('adding', a, b)\n    return a + b\n"
        result = self.runner.run_challenge_tests(self.add, code)
        self.assertTrue(result.ok)
        self.assertIn("adding 2 3", result.stdout)

    def test_printing_the_results_marker_does_not_fool_the_grader(self):
        code = "print('__TEST_RESULTS__:[]')\ndef add(a, b):\n    return a + b\n"
        result = self.runner.run_challenge_tests(self.add, code)
        self.assertTrue(result.ok)
        self.assertEqual(len(result.tests_summary), 3)

    def test_values_with_every_kind_of_quote(self):
        tricky = Challenge(
            id="x", title="t", description="d", starter_code="", function_name="echo",
            tests=[
                ChallengeTest(name="it's \"quoted\" \\ back", kind="function", input_args=["a'b\"c"], expected_return="a'b\"c"),
                ChallengeTest(name="braces {x}", kind="function", input_args=[{"k": "{v}"}], expected_return={"k": "{v}"}),
                ChallengeTest(name="new\nline", kind="function", input_args=["l1\nl2"], expected_return="l1\nl2"),
                ChallengeTest(name="none", kind="function", input_args=[None], expected_return=None),
            ],
        )
        passing = self.runner.run_challenge_tests(tricky, "def echo(x):\n    return x\n")
        self.assertTrue(passing.ok, passing.stderr)
        self.assertEqual([t["name"] for t in passing.tests_summary], [t.name for t in tricky.tests])

        failing = self.runner.run_challenge_tests(tricky, "def echo(x):\n    return 0\n")
        self.assertFalse(failing.ok)
        self.assertEqual(failing.tests_summary[0]["message"], "expected 'a\\'b\"c', got 0")


class ProgramChallengeTests(unittest.TestCase):
    def setUp(self):
        self.runner = RunService()
        self.double = find("ch_double_11")

    def test_wrong_output_shows_expected_and_actual(self):
        result = self.runner.run_challenge_tests(self.double, "n = int(input())\nprint(n + 1)\n")
        self.assertFalse(result.ok)
        self.assertEqual(result.tests_summary[0], {"name": "positive", "ok": False, "message": "expected output '42', got '22'"})

    def test_prompt_text_counts_as_output(self):
        result = self.runner.run_challenge_tests(self.double, "n = int(input('Number: '))\nprint(n * 2)\n")
        self.assertFalse(result.ok)
        self.assertEqual(result.tests_summary[0]["message"], "expected output '42', got 'Number: 42'")

    def test_extra_blank_space_around_the_output_is_ignored(self):
        result = self.runner.run_challenge_tests(self.double, "n = int(input())\nprint()\nprint(n * 2, '  ')\nprint()\n")
        self.assertTrue(result.ok, result.tests_summary)

    def test_a_crash_is_reported_with_its_last_line(self):
        result = self.runner.run_challenge_tests(self.double, "n = int(input())\nprint(n / 0)\n")
        self.assertFalse(result.ok)
        self.assertEqual(len(result.tests_summary), 3)
        self.assertTrue(result.tests_summary[0]["message"].startswith("error: ZeroDivisionError"))
        self.assertIn("ZeroDivisionError", result.stderr)

    def test_an_endless_loop_times_out(self):
        result = self.runner.run_challenge_tests(self.double, "while True:\n    pass\n", timeout=1)
        self.assertTrue(result.timed_out)
        self.assertFalse(result.ok)
        self.assertEqual(result.tests_summary[0]["message"], "timed out")

    def test_function_and_program_tests_can_be_mixed(self):
        mixed = Challenge(
            id="x", title="t", description="d", starter_code="", function_name="double",
            tests=[
                ChallengeTest(name="as a function", kind="function", input_args=[4], expected_return=8),
                ChallengeTest(name="as a program", kind="stdin_stdout", stdin="5\n", expected_stdout="10"),
            ],
        )
        code = (
            "def double(n):\n"
            "    return n * 2\n"
            "\n"
            "try:\n"
            "    print(double(int(input())))\n"
            "except EOFError:\n"
            "    pass  # no input is given while the function tests run\n"
        )
        result = self.runner.run_challenge_tests(mixed, code)
        self.assertEqual([t["name"] for t in result.tests_summary], ["as a function", "as a program"])
        self.assertTrue(result.ok, f"{result.tests_summary} {result.stderr}")


class PlaygroundTests(unittest.TestCase):
    def setUp(self):
        self.runner = RunService()

    def test_runs_code(self):
        result = self.runner.run_arbitrary("print(sum(range(5)))")
        self.assertTrue(result.ok)
        self.assertEqual(result.stdout.strip(), "10")

    def test_passes_the_input_box_to_input(self):
        result = self.runner.run_arbitrary("print('Hello, ' + input() + '!')", stdin="Ada")
        self.assertTrue(result.ok)
        self.assertEqual(result.stdout.strip(), "Hello, Ada!")

    def test_reports_blocked_code(self):
        result = self.runner.run_arbitrary("import os")
        self.assertFalse(result.ok)
        self.assertEqual(result.stderr, "Imports are not allowed.")

    def test_reports_an_endless_loop(self):
        result = self.runner.run_arbitrary("while True:\n    pass", timeout=1)
        self.assertTrue(result.timed_out)
        self.assertFalse(result.ok)


if __name__ == "__main__":
    unittest.main()
