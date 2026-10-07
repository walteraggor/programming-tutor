from typing import List
from .models import Lesson, Quiz, QuizQuestion, Challenge, ChallengeTest

# ─────────────────────────────
# Lessons (expanded)
# ─────────────────────────────
LESSONS: List[Lesson] = [
    Lesson(
        id="py_basics_01",
        title="Python Basics: Variables & Types",
        body_markdown=(
            "### Variables & Types\n"
            "Python variables are created by assignment.\n\n"
            "```python\n"
            "x = 42\n"
            "name = 'Alice'\n"
            "pi = 3.14159\n"
            "is_admin = False\n"
            "```\n"
            "Built-in basic types: `int`, `float`, `str`, `bool`."
        ),
        sample_code="x=10; y=3; print('x+y=', x+y)\n",
        tags=["basics"]
    ),
    Lesson(
        id="py_control_02",
        title="Control Flow: if/elif/else, for, while",
        body_markdown=(
            "### If/Elif/Else & Loops\n"
            "Use `if`, `elif`, `else` to branch; `for` over iterables; `while` for conditions.\n"
        ),
        sample_code=(
            "for i in range(3):\n"
            "    print('i=', i)\n"
            "n=2\n"
            "while n>0:\n"
            "    print(n); n-=1\n"
        ),
        tags=["control"]
    ),
    Lesson(
        id="py_types_03",
        title="Data Types: Lists, Tuples, Dicts, Sets",
        body_markdown=(
            "Lists are ordered and mutable; tuples are ordered and immutable.\n"
            "Dicts map keys to values; sets hold unique items.\n"
        ),
        sample_code="nums=[1,2,3]; nums.append(4); print(nums)\n",
        tags=["collections"]
    ),
    Lesson(
        id="py_funcs_04",
        title="Functions & Parameters",
        body_markdown="Define functions with `def`. Return values with `return`. Support default args, *args, **kwargs.",
        sample_code=(
            "def add(a,b=0): return a+b\n"
            "print(add(2,3), add(5))\n"
        ),
        tags=["functions"]
    ),
    Lesson(
        id="py_files_05",
        title="Files & Context Managers",
        body_markdown="Open files with `with open(...) as f:`; always closes automatically.",
        sample_code=(
            "# Reads a file named sample.txt\n"
            "with open('sample.txt','w') as f:\n"
            "    f.write('hello')\n"
            "with open('sample.txt') as f:\n"
            "    print(f.read())\n"
        ),
        tags=["io"]
    ),
    Lesson(
        id="py_errors_06",
        title="Errors & Exceptions",
        body_markdown="Use try/except/finally. Raise exceptions with `raise`.",
        sample_code=(
            "try:\n"
            "    x = int('notint')\n"
            "except ValueError as e:\n"
            "    print('Oops:', e)\n"
        ),
        tags=["exceptions"]
    ),
    Lesson(
        id="py_oop_07",
        title="OOP Basics: Classes & Methods",
        body_markdown="Define classes with `class`. Use `__init__` to initialize.",
        sample_code=(
            "class Point:\n"
            "    def __init__(self,x,y): self.x=x; self.y=y\n"
            "    def dist(self): return (self.x**2 + self.y**2) ** 0.5\n"
            "print(Point(3,4).dist())\n"
        ),
        tags=["oop"]
    ),
]

# ─────────────────────────────
# Quizzes (expanded)
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
# Challenges (expanded)
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
]