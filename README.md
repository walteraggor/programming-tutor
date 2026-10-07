# Programming Tutor v2

A desktop app for learning Python. It combines short lessons, multiple-choice quizzes, coding challenges that are graded automatically, a code playground, flashcards and notes in one window.

Built with Tkinter and SQLite using only the Python standard library, so there is nothing to install besides Python.

## Features

| Screen | What it does |
|---|---|
| **Lessons** | Seven lessons with explanations and sample code: variables and types, control flow, collections, functions, files, exceptions and classes. Mark a lesson as viewed or attach a note to it. |
| **Quizzes** | Three multiple-choice quizzes. Every answer comes with an explanation. |
| **Challenges** | Twelve coding problems, from `add(a, b)` to balanced parentheses. Write your code in the editor, press **Run Tests** and see which test cases pass. Drafts can be saved and are restored when you come back. |
| **Playground** | Run any snippet and see its output and errors. A box underneath supplies the text that `input()` reads. |
| **Flashcards** | Spaced repetition using the Leitner system: five boxes reviewed after 1, 2, 4, 7 and 14 days. The answer stays hidden until you ask for it. |
| **Notes** | Searchable notes, optionally linked to a lesson. |
| **Progress** | A history of everything you have completed, your total score and three achievements to unlock. |
| **Search** | Searches lessons, quizzes, challenges, notes and flashcards at once. |
| **Settings** | Light and dark themes, and a reset button. |

## Getting started

You need Python 3.11 or newer with Tkinter. Tkinter is included in the standard Windows and macOS installers; on Debian or Ubuntu install it with `sudo apt install python3-tk`.

```bash
git clone https://github.com/walteraggor/programming_tutor_v2.git
cd programming_tutor_v2
python app.py
```

On Windows, use `py app.py` if `python` is not on your PATH.

## How your code is run

Code from the Playground and the Challenges screen runs in a separate Python process with a 3-second timeout, so an infinite loop cannot freeze the app.

Before anything runs, a static check rejects `import` statements and calls to `open`, `eval`, `exec` and a few similar built-ins. This keeps beginner experiments from touching the file system by accident. It is a guard rail for a learning tool, not a security sandbox.

There are two kinds of challenge:

- **Function challenges** call your function with each test's arguments and compare what it returns with the expected value.
- **Program challenges** run your whole program with some input and compare what it prints with the expected output.

Either way, a failed test shows what was expected and what your code produced.

## Your data

Progress, notes, drafts, flashcards and settings are stored in a SQLite database in your home folder:

- Windows: `C:\Users\<you>\.programming_tutor\app.db`
- macOS and Linux: `~/.programming_tutor/app.db`

To start over, use **Settings → Reset EVERYTHING** or delete that file.

## Tests

```bash
python -m unittest
```

The tests cover the safety check, the code runner, storage, grading and the lesson text. One group checks that every challenge has a correct solution that passes and starter code that does not, which catches a challenge whose expected answers are wrong.

Another group opens the real window and uses each screen. It needs a display, so it is skipped automatically where there is none. All tests use a temporary database and never touch your own data.

## Building a standalone app

| Script | Result |
|---|---|
| `build_exe.bat` (Windows) | `dist\ProgrammingTutor\ProgrammingTutor.exe`, built with PyInstaller |
| `build_exe.sh` (macOS, Linux) | `dist/ProgrammingTutor/ProgrammingTutor`, built with PyInstaller |
| `build_pyz.bat` (Windows) | `build\ProgrammingTutor.pyz`, a single file that runs with `py build\ProgrammingTutor.pyz` on any machine that has Python |

The PyInstaller scripts install PyInstaller for you. `programming_tutor.spec` does the same build from a spec file: `pyinstaller programming_tutor.spec`.

The packaged app does not contain a Python of its own for running your code. It uses the Python installed on the computer, and says so in the output box if it cannot find one.

## Project structure

```
app.py                    Entry point
backend/
    models.py             Dataclasses for lessons, quizzes, challenges and results
    repository.py         The built-in lessons, quizzes and challenges
    services.py           Application logic used by the screens
    storage.py            SQLite storage
    code_runner.py        Safety check, subprocess runner and challenge test harness
ui/
    main_window.py        Window, sidebar and themes
    *_view.py             One file per screen
    background.py         Runs code without freezing the window
utils/
    markdown_lite.py      Turns lesson text into headings, code blocks and bullet points
    syntax_highlight.py   Colors the code in the editors
    timefmt.py            Shows saved times in your own time zone
tests/                    Unit tests and the window smoke test
```

## Adding your own content

Lessons, quizzes and challenges are plain Python objects in `backend/repository.py`. To add a function challenge, append a `Challenge` to the `CHALLENGES` list:

```python
Challenge(
    id="ch_square_13",
    title="Square a Number",
    description="square(n) returns n multiplied by itself.",
    starter_code="def square(n):\n    return 0\n",
    function_name="square",
    tests=[
        ChallengeTest(name="positive", kind="function", input_args=[4], expected_return=16),
        ChallengeTest(name="negative", kind="function", input_args=[-3], expected_return=9),
    ],
    tags=["math"],
),
```

A program challenge has no `function_name`. Its tests give the input to type and the output to expect:

```python
Challenge(
    id="ch_shout_14",
    title="Shout",
    description="Read a line with input() and print it in capital letters.",
    starter_code="line = input()\nprint(line)\n",
    tests=[
        ChallengeTest(name="one word", kind="stdin_stdout", stdin="hello\n", expected_stdout="HELLO"),
    ],
    tags=["input"],
),
```

A new challenge appears in the Challenges list the next time the app starts. Add a correct answer for it to `SOLUTIONS` in `tests/test_challenges.py`, and the tests will confirm it can be solved.
