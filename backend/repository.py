import textwrap
from typing import List
from .models import Lesson, Quiz, QuizQuestion, Challenge, ChallengeTest

def _text(block: str) -> str:
    """Remove the indentation that keeps the text below lined up with the code."""
    return textwrap.dedent(block).strip()

# ─────────────────────────────
# Lessons
# ─────────────────────────────
LESSONS: List[Lesson] = [
    Lesson(
        id="py_basics_01",
        title="Python Basics: Variables & Types",
        body_markdown=_text("""
            ### Variables & Types
            A variable is a name for a value. You create one by assigning to it; there is nothing to declare first.

            ```python
            x = 42
            name = 'Alice'
            pi = 3.14159
            is_admin = False
            ```

            The four basic types are `int` (whole numbers), `float` (decimals), `str` (text) and `bool` (`True` or `False`). `type(x)` tells you which one a value is.

            A variable can be given a new value at any time, even one of a different type.
        """),
        sample_code=_text("""
            x = 10
            y = 3
            print('x + y =', x + y)
            print(type(x), type('hello'))
        """) + "\n",
        tags=["basics"]
    ),
    Lesson(
        id="py_control_02",
        title="Control Flow: if/elif/else, for, while",
        body_markdown=_text("""
            ### If, Elif and Else
            `if` runs a block only when its condition is true. `elif` checks another condition, and `else` covers everything that is left.

            ```python
            if temperature > 30:
                print('hot')
            elif temperature > 15:
                print('mild')
            else:
                print('cold')
            ```

            ### Loops
            A `for` loop goes through the items of something one at a time. `range(3)` gives the numbers 0, 1 and 2.

            A `while` loop repeats for as long as its condition stays true, so something inside it has to change the condition.

            Blocks are marked by indentation: the spaces at the start of a line matter.
        """),
        sample_code=_text("""
            for i in range(3):
                print('i =', i)

            n = 2
            while n > 0:
                print(n)
                n -= 1
        """) + "\n",
        tags=["control"]
    ),
    Lesson(
        id="py_types_03",
        title="Data Types: Lists, Tuples, Dicts, Sets",
        body_markdown=_text("""
            ### Four Ways to Hold Several Values
            - A list keeps items in order and can be changed: `[1, 2, 3]`
            - A tuple keeps items in order and cannot be changed: `(1, 2, 3)`
            - A dict maps keys to values: `{'name': 'Alice', 'age': 30}`
            - A set holds each item once, in no particular order: `{1, 2, 3}`

            ```python
            nums = [1, 2, 3]
            nums.append(4)          # lists can grow
            first = nums[0]         # positions start at 0

            ages = {'Alice': 30}
            ages['Bob'] = 25        # add a key
            ```

            `len()` works on all four, and so does `in`: `2 in nums` is `True`.
        """),
        sample_code=_text("""
            nums = [1, 2, 3]
            nums.append(4)
            print(nums, len(nums))

            ages = {'Alice': 30, 'Bob': 25}
            print(ages['Bob'], 'Alice' in ages)
            print(set([1, 1, 2]))
        """) + "\n",
        tags=["collections"]
    ),
    Lesson(
        id="py_funcs_04",
        title="Functions & Parameters",
        body_markdown=_text("""
            ### Functions
            A function is a named block of code you can run again and again. Define it with `def`, and send a value back with `return`.

            ```python
            def add(a, b=0):
                return a + b
            ```

            `a` and `b` are parameters. `b=0` gives `b` a default, so `add(5)` works and returns 5.

            A function with no `return` gives back `None`.

            ### Any Number of Arguments
            `*args` collects extra positional arguments into a tuple, and `**kwargs` collects extra named arguments into a dict.
        """),
        sample_code=_text("""
            def add(a, b=0):
                return a + b

            print(add(2, 3), add(5))

            def total(*numbers):
                return sum(numbers)

            print(total(1, 2, 3))
        """) + "\n",
        tags=["functions"]
    ),
    Lesson(
        id="py_files_05",
        title="Files & Context Managers",
        body_markdown=_text("""
            ### Files
            `open()` gives you a file to read or write. Putting it in a `with` block closes the file for you when the block ends, even if something goes wrong.

            ```python
            with open('notes.txt', 'w') as f:
                f.write('hello')

            with open('notes.txt') as f:
                print(f.read())
            ```

            The second argument is the mode: `'r'` to read (the default), `'w'` to write from scratch and `'a'` to add to the end.

            File access is switched off in this app's Playground, so run this example in your own editor.
        """),
        sample_code=_text("""
            # Writes a file, then reads it back.
            with open('sample.txt', 'w') as f:
                f.write('hello')

            with open('sample.txt') as f:
                print(f.read())
        """) + "\n",
        tags=["io"]
    ),
    Lesson(
        id="py_errors_06",
        title="Errors & Exceptions",
        body_markdown=_text("""
            ### Catching Errors
            When something goes wrong, Python raises an exception. Left alone, that stops the program. `try` and `except` let you deal with it instead.

            ```python
            try:
                number = int('abc')
            except ValueError:
                print('That is not a number.')
            ```

            Name the kind of error you expect, such as `ValueError`, `KeyError` or `ZeroDivisionError`, so that other mistakes are not hidden.

            A `finally` block runs whether or not there was an error.

            ### Raising Your Own
            Use `raise` to signal a problem yourself: `raise ValueError('age cannot be negative')`.
        """),
        sample_code=_text("""
            try:
                x = int('notint')
            except ValueError as e:
                print('Oops:', e)
            finally:
                print('Done.')
        """) + "\n",
        tags=["exceptions"]
    ),
    Lesson(
        id="py_oop_07",
        title="OOP Basics: Classes & Methods",
        body_markdown=_text("""
            ### Classes
            A class describes a kind of object: the data it holds and what it can do. `__init__` runs when a new object is made and sets up its data.

            ```python
            class Point:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y

                def dist(self):
                    return (self.x ** 2 + self.y ** 2) ** 0.5
            ```

            `self` is the object itself. `Point(3, 4)` makes a new point, and `p.dist()` calls a method on it.

            Functions defined inside a class are called methods.
        """),
        sample_code=_text("""
            class Point:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y

                def dist(self):
                    return (self.x ** 2 + self.y ** 2) ** 0.5

            p = Point(3, 4)
            print(p.dist())
        """) + "\n",
        tags=["oop"]
    ),
]

# ─────────────────────────────
# Quizzes
# ─────────────────────────────
QUIZZES: List[Quiz] = [
    Quiz(
        id="quiz_basics_01",
        title="Python Basics Quiz",
        tags=["basics"],
        questions=[
            QuizQuestion(
                id="q1",
                prompt="What is the output of: print(type(42))",
                options=["<class 'int'>", "<type 'int'>", "int", "42"],
                correct_index=0,
                explanation="In Python 3, `type(42)` returns `<class 'int'>`."
            ),
            QuizQuestion(
                id="q2",
                prompt="Which of these is a valid variable name?",
                options=["2name", "name_2", "class", "first-name"],
                correct_index=1,
                explanation="Can't start with digits, can't be keywords, no hyphens."
            ),
            QuizQuestion(
                id="q3",
                prompt="What does `bool('')` evaluate to?",
                options=["True", "False"],
                correct_index=1,
                explanation="Empty string is falsy."
            ),
        ]
    ),
    Quiz(
        id="quiz_collections_02",
        title="Collections & Loops",
        tags=["collections","control"],
        questions=[
            QuizQuestion(
                id="q1",
                prompt="Which is immutable?",
                options=["list","dict","tuple","set"],
                correct_index=2,
                explanation="Tuples are immutable."
            ),
            QuizQuestion(
                id="q2",
                prompt="What does `len({1,1,2})` return?",
                options=["3","2","1"],
                correct_index=1,
                explanation="Set removes duplicates → {1,2} so length is 2."
            ),
        ]
    ),
    Quiz(
        id="quiz_funcs_03",
        title="Functions & Errors",
        tags=["functions","exceptions"],
        questions=[
            QuizQuestion(
                id="q1",
                prompt="`def f(a,b=1): return a+b; f(2)` returns?",
                options=["TypeError","3","None","'2'"],
                correct_index=1,
                explanation="Uses default b=1."
            ),
            QuizQuestion(
                id="q2",
                prompt="Which block always runs if present?",
                options=["try","except","else","finally"],
                correct_index=3,
                explanation="`finally` always executes."
            ),
        ]
    ),
]

# ─────────────────────────────
# Challenges
# ─────────────────────────────
CHALLENGES: List[Challenge] = [
    Challenge(
        id="ch_add_01",
        title="Write add(a, b)",
        description="Return the sum of a and b.",
        starter_code="def add(a, b):\n    return 0\n",
        function_name="add",
        tests=[
            ChallengeTest(name="small ints", kind="function", input_args=[2,3], expected_return=5),
            ChallengeTest(name="negatives", kind="function", input_args=[-5,7], expected_return=2),
            ChallengeTest(name="floats", kind="function", input_args=[2.5,0.5], expected_return=3.0),
        ],
        tags=["basics"]
    ),
    Challenge(
        id="ch_pal_02",
        title="Check Palindrome",
        description="Implement is_palindrome(s) ignoring case and spaces.",
        starter_code="def is_palindrome(s: str) -> bool:\n    return False\n",
        function_name="is_palindrome",
        tests=[
            ChallengeTest(name="simple true", kind="function", input_args=["racecar"], expected_return=True),
            ChallengeTest(name="with spaces/case", kind="function", input_args=["Never odd or even"], expected_return=True),
            ChallengeTest(name="false case", kind="function", input_args=["python"], expected_return=False),
        ],
        tags=["strings"]
    ),
    Challenge(
        id="ch_rev_03",
        title="Reverse String",
        description="Implement reverse_str(s) that returns s reversed.",
        starter_code="def reverse_str(s: str) -> str:\n    return ''\n",
        function_name="reverse_str",
        tests=[
            ChallengeTest(name="simple", kind="function", input_args=["abc"], expected_return="cba"),
            ChallengeTest(name="empty", kind="function", input_args=[""], expected_return=""),
        ],
        tags=["strings"]
    ),
    Challenge(
        id="ch_unique_04",
        title="Unique Elements",
        description="unique_list(lst) → list of unique items in order of first appearance.",
        starter_code="def unique_list(lst):\n    return []\n",
        function_name="unique_list",
        tests=[
            ChallengeTest(name="basic", kind="function", input_args=[[1,1,2,3,2]], expected_return=[1,2,3]),
            ChallengeTest(name="strings", kind="function", input_args=[['a','a','b']], expected_return=['a','b']),
        ],
        tags=["lists"]
    ),
    Challenge(
        id="ch_freq_05",
        title="Char Frequency",
        description="char_freq(s) → dict of {char: count}.",
        starter_code="def char_freq(s: str):\n    return {}\n",
        function_name="char_freq",
        tests=[
            ChallengeTest(name="small", kind="function", input_args=["abba"], expected_return={'a':2,'b':2}),
        ],
        tags=["dicts","strings"]
    ),
    Challenge(
        id="ch_sum_06",
        title="Sum Positives",
        description="sum_positives(lst) → sum of positive numbers only.",
        starter_code="def sum_positives(lst):\n    return 0\n",
        function_name="sum_positives",
        tests=[
            ChallengeTest(name="basic", kind="function", input_args=[[1,-2,3,0]], expected_return=4),
        ],
        tags=["lists"]
    ),
    Challenge(
        id="ch_isprime_07",
        title="Is Prime",
        description="is_prime(n) → True if prime; else False (n>=0).",
        starter_code="def is_prime(n: int) -> bool:\n    return False\n",
        function_name="is_prime",
        tests=[
            ChallengeTest(name="2", kind="function", input_args=[2], expected_return=True),
            ChallengeTest(name="9", kind="function", input_args=[9], expected_return=False),
            ChallengeTest(name="17", kind="function", input_args=[17], expected_return=True),
        ],
        tags=["math"]
    ),
    Challenge(
        id="ch_fizz_08",
        title="FizzBuzz",
        description="fizzbuzz(n) → list 1..n, multiples of 3→'Fizz', 5→'Buzz', 15→'FizzBuzz'.",
        starter_code="def fizzbuzz(n:int):\n    return []\n",
        function_name="fizzbuzz",
        tests=[
            ChallengeTest(name="n=5", kind="function", input_args=[5], expected_return=[1,2,'Fizz',4,'Buzz']),
        ],
        tags=["control"]
    ),
    Challenge(
        id="ch_anagram_09",
        title="Anagram Check",
        description="is_anagram(a,b) → True if words are anagrams (ignore spaces/case).",
        starter_code="def is_anagram(a:str,b:str)->bool:\n    return False\n",
        function_name="is_anagram",
        tests=[
            ChallengeTest(name="yes", kind="function", input_args=["listen","silent"], expected_return=True),
            ChallengeTest(name="no", kind="function", input_args=["hello","world"], expected_return=False),
        ],
        tags=["strings"]
    ),
    Challenge(
        id="ch_balance_10",
        title="Parentheses Balance",
        description="is_balanced(s) → True if parentheses (), [], {} are balanced.",
        starter_code="def is_balanced(s:str)->bool:\n    return False\n",
        function_name="is_balanced",
        tests=[
            ChallengeTest(name="ok", kind="function", input_args=["([]){}"], expected_return=True),
            ChallengeTest(name="bad", kind="function", input_args=["([)]"], expected_return=False),
        ],
        tags=["stacks"]
    ),
    Challenge(
        id="ch_double_11",
        title="Double the Number",
        description=(
            "Read a whole number with input() and print the number doubled.\n\n"
            "Call input() with no prompt text: everything your program prints is checked."
        ),
        starter_code="n = int(input())\nprint(n)\n",
        tests=[
            ChallengeTest(name="positive", kind="stdin_stdout", stdin="21\n", expected_stdout="42"),
            ChallengeTest(name="zero", kind="stdin_stdout", stdin="0\n", expected_stdout="0"),
            ChallengeTest(name="negative", kind="stdin_stdout", stdin="-5\n", expected_stdout="-10"),
        ],
        tags=["input"]
    ),
    Challenge(
        id="ch_greet_12",
        title="Greet by Name",
        description=(
            "Read a name with input() and print: Hello, <name>!\n\n"
            "Call input() with no prompt text: everything your program prints is checked."
        ),
        starter_code="name = input()\nprint('Hello')\n",
        tests=[
            ChallengeTest(name="one word", kind="stdin_stdout", stdin="Ada\n", expected_stdout="Hello, Ada!"),
            ChallengeTest(name="two words", kind="stdin_stdout", stdin="Grace Hopper\n", expected_stdout="Hello, Grace Hopper!"),
        ],
        tags=["input", "strings"]
    ),
]
