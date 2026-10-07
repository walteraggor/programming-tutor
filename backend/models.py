from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Lesson:
    id: str
    title: str
    body_markdown: str
    sample_code: Optional[str] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class QuizQuestion:
    id: str
    prompt: str
    options: List[str]
    correct_index: int
    explanation: str

@dataclass
class Quiz:
    id: str
    title: str
    questions: List[QuizQuestion] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

@dataclass
class ChallengeTest:
    name: str
    kind: str  # "function" or "stdin_stdout"
    input_args: Optional[List[Any]] = None  # for kind=function
    expected_return: Optional[Any] = None   # for kind=function
    stdin: Optional[str] = None             # for kind=stdin_stdout
    expected_stdout: Optional[str] = None   # for kind=stdin_stdout

@dataclass
class Challenge:
    id: str
    title: str
    description: str
    starter_code: str
    function_name: Optional[str] = None
    tests: List[ChallengeTest] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

@dataclass
class GradeResult:
    total: int
    correct: int
    details: List[Dict[str, Any]]

@dataclass
class RunResult:
    ok: bool
    stdout: str
    stderr: str
    timed_out: bool
    tests_summary: Optional[List[Dict[str, Any]]] = None

# Extras for v2
@dataclass
class Note:
    id: int
    title: str
    content: str
    related_lesson_id: Optional[str]
    created_at: str

@dataclass
class Flashcard:
    id: int
    front: str
    back: str
    box: int
    next_review: str
    created_at: str

@dataclass
class Achievement:
    code: str
    name: str
    achieved_at: Optional[str] = None

@dataclass
class Setting:
    key: str
    value: str