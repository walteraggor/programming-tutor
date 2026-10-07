"""Tests for quiz grading, search, progress and achievements."""

import os
import tempfile
import unittest

from backend.repository import LESSONS, QUIZZES
from backend.services import (
    AchievementsService,
    CatalogService,
    ProgressService,
    QuizService,
    ResetService,
)
from backend.storage import Storage


class QuizGradingTests(unittest.TestCase):
    def setUp(self):
        self.quiz = QUIZZES[0]
        self.service = QuizService()

    def test_all_correct(self):
        answers = {q.id: q.correct_index for q in self.quiz.questions}
        result = self.service.grade(self.quiz, answers)
        self.assertEqual((result.correct, result.total), (len(self.quiz.questions), len(self.quiz.questions)))
        self.assertTrue(all(d["correct"] for d in result.details))

    def test_unanswered_questions_count_as_wrong(self):
        result = self.service.grade(self.quiz, {})
        self.assertEqual(result.correct, 0)
        self.assertEqual(result.total, len(self.quiz.questions))

    def test_every_question_comes_with_its_explanation(self):
        result = self.service.grade(self.quiz, {})
        self.assertEqual([d["explanation"] for d in result.details], [q.explanation for q in self.quiz.questions])


class QuizCatalogueTests(unittest.TestCase):
    def test_every_correct_answer_points_at_a_real_option(self):
        for quiz in QUIZZES:
            for question in quiz.questions:
                with self.subTest(quiz=quiz.id, question=question.id):
                    self.assertTrue(0 <= question.correct_index < len(question.options))

    def test_question_ids_are_unique_within_a_quiz(self):
        for quiz in QUIZZES:
            ids = [q.id for q in quiz.questions]
            self.assertEqual(len(ids), len(set(ids)), quiz.id)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = CatalogService()

    def test_find_by_id(self):
        self.assertEqual(self.catalog.find_lesson(LESSONS[0].id), LESSONS[0])
        self.assertIsNone(self.catalog.find_lesson("no_such_lesson"))
        self.assertIsNone(self.catalog.find_quiz("no_such_quiz"))
        self.assertIsNone(self.catalog.find_challenge("no_such_challenge"))

    def test_search_ignores_capital_letters(self):
        results = self.catalog.search_all("PALINDROME")
        self.assertEqual([c["id"] for c in results["challenges"]], ["ch_pal_02"])

    def test_search_looks_inside_lesson_text(self):
        results = self.catalog.search_all("indentation")
        self.assertEqual([lesson["id"] for lesson in results["lessons"]], ["py_control_02"])

    def test_search_with_no_match(self):
        results = self.catalog.search_all("zzzzzz")
        self.assertEqual(results, {"lessons": [], "quizzes": [], "challenges": []})


class ProgressAndAchievementTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.storage = Storage(os.path.join(self.folder.name, "app.db"))
        self.progress = ProgressService(self.storage)
        self.achievements = AchievementsService(self.storage)

    def unlocked(self):
        return {a["code"] for a in self.achievements.list() if a["achieved_at"]}

    def test_all_achievements_start_locked(self):
        self.assertEqual(len(self.achievements.list()), 3)
        self.assertEqual(self.unlocked(), set())

    def test_first_quiz_and_first_challenge(self):
        self.progress.record_quiz("quiz_basics_01", 1, 3)
        self.assertEqual(self.unlocked(), {"first_quiz"})
        self.progress.record_challenge("ch_add_01", 0, 3)
        self.assertEqual(self.unlocked(), {"first_quiz", "first_challenge"})

    def test_a_quiz_counts_as_passed_only_with_a_full_score(self):
        self.progress.record_quiz("quiz_basics_01", 2, 3)
        self.progress.record_quiz("quiz_basics_01", 3, 3)
        statuses = [row[2] for row in self.progress.list_progress()]
        self.assertEqual(statuses, ["passed", "attempted"])

    def test_passing_one_challenge_five_times_is_not_five_challenges(self):
        for _ in range(5):
            self.progress.record_challenge("ch_add_01", 3, 3)
        self.assertNotIn("five_challs", self.unlocked())

    def test_passing_five_different_challenges_unlocks_rising_coder(self):
        for challenge_id in ("ch_add_01", "ch_pal_02", "ch_rev_03", "ch_unique_04"):
            self.progress.record_challenge(challenge_id, 2, 2)
        self.assertNotIn("five_challs", self.unlocked())
        self.progress.record_challenge("ch_freq_05", 1, 1)
        self.assertIn("five_challs", self.unlocked())

    def test_totals_follow_recorded_scores(self):
        self.progress.record_quiz("quiz_basics_01", 2, 3)
        self.progress.record_challenge("ch_add_01", 3, 3)
        self.assertEqual(self.progress.totals(), {"score": 5, "max_score": 6})

    def test_achievements_are_listed_again_after_a_full_reset(self):
        self.progress.record_quiz("quiz_basics_01", 3, 3)
        ResetService(self.storage).reset_all()
        self.assertEqual(len(self.achievements.list()), 3)
        self.assertEqual(self.unlocked(), set())


if __name__ == "__main__":
    unittest.main()
