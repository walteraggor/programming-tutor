# Programming Tutor v2

A desktop app for learning Python. It combines short lessons, multiple-choice quizzes, coding challenges that are graded automatically, a code playground, flashcards and notes in one window.

Built with Tkinter and SQLite using only the Python standard library, so there is nothing to install besides Python.

## Features

| Screen | What it does |
|---|---|
| **Lessons** | Seven short lessons with sample code: variables and types, control flow, collections, functions, files, exceptions and classes. Mark a lesson as viewed or attach a note to it. |
| **Quizzes** | Three multiple-choice quizzes. Every answer comes with an explanation. |
| **Challenges** | Ten coding problems, from `add(a, b)` to balanced parentheses. Write a function in the editor, press **Run Tests** and see which test cases pass. Drafts can be saved and are restored when you come back. |
| **Playground** | Run any snippet and see its output and errors. |
| **Flashcards** | Spaced repetition using the Leitner system: five boxes reviewed after 1, 2, 4, 7 and 14 days. |
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

Before anything runs, a static check rejects `import` statements and calls to `open`, `input`, `eval`, `exec` and a few similar built-ins. This keeps beginner experiments from touching the file system by accident. It is a guard rail for a learning tool, not a security sandbox.

A challenge is graded by calling your function with each test's arguments and comparing the return value with the expected one. Failed tests show what was expected and what your function returned.

## Your data

Progress, notes, drafts, flashcards and settings are stored in a SQLite database in your home folder:

- Windows: `C:\Users\<you>\.programming_tutor\app.db`
- macOS and Linux: `~/.programming_tutor/app.db`

To start over, use **Settings → Reset EVERYTHING** or delete that file.

## Building a standalone app

| Script | Result |
|---|---|
| `build_exe.bat` (Windows) | `dist\ProgrammingTutor\ProgrammingTutor.exe`, built with PyInstaller |
| `build_exe.sh` (macOS, Linux) | `dist/ProgrammingTutor/ProgrammingTutor`, built with PyInstaller |
| `build_pyz.bat` (Windows) | `build\ProgrammingTutor.pyz`, a single file that runs with `py build\ProgrammingTutor.pyz` on any machine that has Python |

The PyInstaller scripts install PyInstaller for you. `programming_tutor.spec` does the same build from a spec file: `pyinstaller programming_tutor.spec`.

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
utils/
    syntax_highlight.py   Syntax highlighting for the challenge editor
```

## Adding your own content

Lessons, quizzes and challenges are plain Python objects in `backend/repository.py`. To add a challenge, append a `Challenge` to the `CHALLENGES` list:

```python
Challenge(
    id="ch_square_11",
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

It appears in the Challenges list the next time the app starts.
