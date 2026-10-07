"""Tests for the SQLite storage, each on its own temporary database."""

import os
import tempfile
import unittest
from datetime import datetime, timedelta

from backend import storage as storage_module
from backend.storage import Storage


class StorageTestCase(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.db_path = os.path.join(self.folder.name, "data", "app.db")
        self.storage = Storage(self.db_path)


class SetupTests(StorageTestCase):
    def test_creates_the_folder_and_the_database(self):
        self.assertTrue(os.path.exists(self.db_path))

    def test_opening_an_existing_database_keeps_its_data(self):
        self.storage.add_note("Title", "Content", None)
        again = Storage(self.db_path)
        self.assertEqual(len(again.list_notes()), 1)

    def test_the_database_file_is_not_left_open(self):
        # Windows refuses to delete a file that is still open, so this fails
        # there if a connection has been left behind.
        self.storage.add_note("Title", "Content", None)
        self.storage.list_notes()
        os.remove(self.db_path)
        self.assertFalse(os.path.exists(self.db_path))


class ProgressTests(StorageTestCase):
    def test_totals_start_at_zero(self):
        self.assertEqual(self.storage.get_totals(), {"score": 0, "max_score": 0})

    def test_totals_add_up_scores(self):
        self.storage.record_progress("quiz", "quiz_1", "attempted", 2, 3)
        self.storage.record_progress("challenge", "ch_1", "passed", 3, 3)
        self.assertEqual(self.storage.get_totals(), {"score": 5, "max_score": 6})

    def test_history_lists_the_newest_first(self):
        self.storage.record_progress("lesson", "first", "viewed")
        self.storage.record_progress("lesson", "second", "viewed")
        self.assertEqual([row[1] for row in self.storage.list_progress()], ["second", "first"])

    def test_reset_progress_clears_only_progress(self):
        self.storage.record_progress("lesson", "first", "viewed")
        self.storage.add_note("Title", "Content", None)
        self.storage.reset_all_progress()
        self.assertEqual(self.storage.list_progress(), [])
        self.assertEqual(len(self.storage.list_notes()), 1)


class NotesTests(StorageTestCase):
    def test_add_list_and_delete(self):
        note_id = self.storage.add_note("Slicing", "s[::-1] reverses a string", "py_basics_01")
        notes = self.storage.list_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["title"], "Slicing")
        self.assertEqual(notes[0]["related_lesson_id"], "py_basics_01")
        self.storage.delete_note(note_id)
        self.assertEqual(self.storage.list_notes(), [])

    def test_search_looks_in_title_and_content(self):
        self.storage.add_note("Loops", "for and while", None)
        self.storage.add_note("Functions", "use def to make a loop helper", None)
        self.storage.add_note("Classes", "objects", None)
        self.assertEqual({n["title"] for n in self.storage.list_notes("loop")}, {"Loops", "Functions"})


class DraftsTests(StorageTestCase):
    def test_no_draft_yet(self):
        self.assertIsNone(self.storage.latest_draft("ch_add_01"))

    def test_latest_draft_is_the_last_one_saved(self):
        # Saved within the same second, so only the row order can tell them apart.
        self.storage.save_draft("ch_add_01", "first")
        self.storage.save_draft("ch_add_01", "second")
        self.storage.save_draft("ch_other", "unrelated")
        self.assertEqual(self.storage.latest_draft("ch_add_01"), "second")


class FlashcardTests(StorageTestCase):
    def only_card(self):
        cards = self.storage.list_all_flashcards()
        self.assertEqual(len(cards), 1)
        return cards[0]

    def test_a_new_card_is_due_straight_away_in_box_one(self):
        self.storage.add_flashcard("front", "back")
        due = self.storage.list_due_flashcards()
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]["box"], 1)

    def test_knowing_a_card_moves_it_up_and_schedules_it_later(self):
        self.storage.add_flashcard("front", "back")
        self.storage.promote_or_demote_card(self.only_card()["id"], True)
        self.assertEqual(self.only_card()["box"], 2)
        self.assertEqual(self.storage.list_due_flashcards(), [])

    def test_review_gaps_grow_with_the_box(self):
        self.storage.add_flashcard("front", "back")
        card_id = self.only_card()["id"]
        expected_days = {2: 2, 3: 4, 4: 7, 5: 14}
        for box in (2, 3, 4, 5):
            before = storage_module._utc_now()
            self.storage.promote_or_demote_card(card_id, True)
            card = self.only_card()
            self.assertEqual(card["box"], box)
            next_review = datetime.fromisoformat(card["next_review"])
            gap = next_review - before
            self.assertAlmostEqual(gap / timedelta(days=1), expected_days[box], places=2)

    def test_the_top_box_is_five(self):
        self.storage.add_flashcard("front", "back")
        card_id = self.only_card()["id"]
        for _ in range(8):
            self.storage.promote_or_demote_card(card_id, True)
        self.assertEqual(self.only_card()["box"], 5)

    def test_forgetting_a_card_sends_it_back_to_box_one(self):
        self.storage.add_flashcard("front", "back")
        card_id = self.only_card()["id"]
        for _ in range(3):
            self.storage.promote_or_demote_card(card_id, True)
        self.storage.promote_or_demote_card(card_id, False)
        self.assertEqual(self.only_card()["box"], 1)

    def test_reviewing_a_missing_card_does_nothing(self):
        self.storage.promote_or_demote_card(999, True)

    def test_search_and_delete(self):
        self.storage.add_flashcard("What is a list?", "An ordered collection")
        self.storage.add_flashcard("What is a dict?", "Keys mapped to values")
        found = self.storage.list_all_flashcards("dict")
        self.assertEqual(len(found), 1)
        self.storage.delete_flashcard(found[0]["id"])
        self.assertEqual(len(self.storage.list_all_flashcards()), 1)


class SettingsTests(StorageTestCase):
    def test_default_is_returned_until_a_value_is_set(self):
        self.assertEqual(self.storage.get_setting("theme", "light"), "light")
        self.storage.set_setting("theme", "dark")
        self.assertEqual(self.storage.get_setting("theme", "light"), "dark")

    def test_setting_again_replaces_the_value(self):
        self.storage.set_setting("theme", "dark")
        self.storage.set_setting("theme", "light")
        self.assertEqual(self.storage.get_setting("theme"), "light")


class AchievementTests(StorageTestCase):
    def test_an_achievement_is_locked_until_granted(self):
        self.storage.ensure_achievement("first_quiz", "Quiz Novice")
        self.storage.ensure_achievement("first_quiz", "Quiz Novice")  # adding twice is harmless
        achievements = self.storage.list_achievements()
        self.assertEqual(len(achievements), 1)
        self.assertIsNone(achievements[0]["achieved_at"])

        self.storage.grant_achievement("first_quiz")
        self.assertIsNotNone(self.storage.list_achievements()[0]["achieved_at"])


class ResetTests(StorageTestCase):
    def test_reset_all_empties_every_table(self):
        self.storage.record_progress("lesson", "first", "viewed")
        self.storage.add_note("Title", "Content", None)
        self.storage.save_draft("ch_add_01", "code")
        self.storage.add_flashcard("front", "back")
        self.storage.set_setting("theme", "dark")
        self.storage.ensure_achievement("first_quiz", "Quiz Novice")

        self.storage.reset_all()

        self.assertEqual(self.storage.list_progress(), [])
        self.assertEqual(self.storage.list_notes(), [])
        self.assertIsNone(self.storage.latest_draft("ch_add_01"))
        self.assertEqual(self.storage.list_all_flashcards(), [])
        self.assertEqual(self.storage.get_setting("theme", "light"), "light")
        self.assertEqual(self.storage.list_achievements(), [])
