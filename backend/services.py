import ast
from typing import List, Dict, Any, Optional
from .models import Lesson, Quiz, QuizQuestion, Challenge, ChallengeTest, GradeResult, RunResult
from .repository import LESSONS, QUIZZES, CHALLENGES
from .storage import Storage
from .code_runner import run_code_isolated, build_function_test_harness, build_stdin_stdout_harness, static_safety_check, SafetyViolation

class CatalogService:
    def get_lessons(self) -> List[Lesson]:
        return LESSONS

    def get_quizzes(self) -> List[Quiz]:
        return QUIZZES

    def get_challenges(self) -> List[Challenge]:
        return CHALLENGES

    def find_lesson(self, lesson_id: str) -> Optional[Lesson]:
        return next((l for l in LESSONS if l.id == lesson_id), None)

    def find_quiz(self, quiz_id: str) -> Optional[Quiz]:
        return next((q for q in QUIZZES if q.id == quiz_id), None)

    def find_challenge(self, challenge_id: str) -> Optional[Challenge]:
        return next((c for c in CHALLENGES if c.id == challenge_id), None)

    # Search meta
    def search_all(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        q = query.lower()
        lessons = [{"id": l.id, "title": l.title} for l in LESSONS if q in l.title.lower() or q in l.body_markdown.lower()]
        quizzes = [{"id": qu.id, "title": qu.title} for qu in QUIZZES if q in qu.title.lower()]
        challenges = [{"id": ch.id, "title": ch.title} for ch in CHALLENGES if q in ch.title.lower() or q in ch.description.lower()]
        return {"lessons": lessons, "quizzes": quizzes, "challenges": challenges}

class ProgressService:
    def __init__(self, storage: Storage):
        self.storage = storage

    def record_viewed(self, lesson_id: str):
        self.storage.record_progress("lesson", lesson_id, "viewed", 0, 0)

    def record_quiz(self, quiz_id: str, score: int, total: int):
        status = "passed" if score == total else "attempted"
        self.storage.record_progress("quiz", quiz_id, status, score, total)
        # achievements
        self.storage.ensure_achievement("first_quiz", "Quiz Novice: First quiz attempt")
        self.storage.grant_achievement("first_quiz")

    def record_challenge(self, challenge_id: str, passed: int, total: int):
        status = "passed" if passed == total else "attempted"
        self.storage.record_progress("challenge", challenge_id, status, passed, total)
        # achievements
        self.storage.ensure_achievement("first_challenge", "Code Sprout: First challenge attempt")
        self.storage.grant_achievement("first_challenge")
        # If passed many, grant others
        hist = self.storage.list_progress()
        total_passed = sum(1 for t, _, s, sc, mx, _ in hist if t == "challenge" and s == "passed")
        if total_passed >= 5:
            self.storage.ensure_achievement("five_challs", "Rising Coder: 5 challenges passed")
            self.storage.grant_achievement("five_challs")

    def totals(self) -> Dict[str, int]:
        return self.storage.get_totals()

    def list_progress(self):
        return self.storage.list_progress()

    def reset(self):
        self.storage.reset_all_progress()

class QuizService:
    def grade(self, quiz: Quiz, answers: Dict[str, int]) -> GradeResult:
        details = []
        correct = 0
        for q in quiz.questions:
            ans_index = answers.get(q.id, -1)
            ok = (ans_index == q.correct_index)
            if ok:
                correct += 1
            details.append({
                "question_id": q.id,
                "correct": ok,
                "explanation": q.explanation
            })
        return GradeResult(total=len(quiz.questions), correct=correct, details=details)

class RunService:
    def run_arbitrary(self, code: str, stdin: str = "", timeout: int = 3) -> RunResult:
        try:
            stdout, stderr, rc, to = run_code_isolated(code, stdin=stdin, timeout=timeout)
            ok = (rc == 0) and not to
            return RunResult(ok=ok, stdout=stdout, stderr=stderr, timed_out=to)
        except SafetyViolation as e:
            return RunResult(ok=False, stdout="", stderr=str(e), timed_out=False)

    def run_challenge_tests(self, challenge: Challenge, student_code: str, timeout: int = 3) -> RunResult:
        func_tests = [{
            "name": t.name,
            "input_args": t.input_args,
            "expected_return": t.expected_return
        } for t in challenge.tests if t.kind == "function"]

        try:
            harness = build_function_test_harness(student_code, challenge.function_name, func_tests)
            stdout, stderr, rc, to = run_code_isolated(harness, stdin="", timeout=timeout)
        except SafetyViolation as e:
            # Same as run_arbitrary: report it instead of letting the worker thread die.
            return RunResult(ok=False, stdout="", stderr=str(e), timed_out=False, tests_summary=[])
        tests_summary = []
        if "__TEST_RESULTS__:" in stdout:
            payload = stdout.split("__TEST_RESULTS__:", 1)[1].strip()
            try:
                parsed = ast.literal_eval(payload)
            except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
                parsed = []
            if isinstance(parsed, list):
                tests_summary = [t for t in parsed if isinstance(t, dict)]
        passed = sum(1 for t in tests_summary if t.get("ok"))
        total = len(func_tests)
        ok = (passed == total) and not to and rc == 0
        return RunResult(ok=ok, stdout=stdout, stderr=stderr, timed_out=to, tests_summary=tests_summary)

class NotesService:
    def __init__(self, storage: Storage):
        self.storage = storage

    def add(self, title: str, content: str, related_lesson_id: Optional[str]):
        return self.storage.add_note(title, content, related_lesson_id)

    def list(self, query: Optional[str] = None):
        return self.storage.list_notes(query)

    def delete(self, note_id: int):
        self.storage.delete_note(note_id)

class DraftsService:
    def __init__(self, storage: Storage):
        self.storage = storage

    def save_draft(self, challenge_id: str, code: str):
        self.storage.save_draft(challenge_id, code)

    def latest(self, challenge_id: str) -> Optional[str]:
        return self.storage.latest_draft(challenge_id)

class FlashcardsService:
    def __init__(self, storage: Storage):
        self.storage = storage

    def add_card(self, front: str, back: str):
        self.storage.add_flashcard(front, back)

    def due_cards(self):
        return self.storage.list_due_flashcards()

    def review(self, card_id: int, correct: bool):
        self.storage.promote_or_demote_card(card_id, correct)

    def all_cards(self, query: Optional[str] = None):
        return self.storage.list_all_flashcards(query)

    def delete(self, card_id: int):
        self.storage.delete_flashcard(card_id)

class SettingsService:
    def __init__(self, storage: Storage):
        self.storage = storage

    def set(self, key: str, value: str):
        self.storage.set_setting(key, value)

    def get(self, key: str, default: str = "") -> str:
        return self.storage.get_setting(key, default)

class AchievementsService:
    def __init__(self, storage: Storage):
        self.storage = storage
        # Ensure catalog exists
        self.storage.ensure_achievement("first_quiz", "Quiz Novice: First quiz attempt")
        self.storage.ensure_achievement("first_challenge", "Code Sprout: First challenge attempt")
        self.storage.ensure_achievement("five_challs", "Rising Coder: 5 challenges passed")

    def list(self):
        return self.storage.list_achievements()

class ResetService:
    def __init__(self, storage: Storage):
        self.storage = storage
    def reset_all(self):
        self.storage.reset_all()
