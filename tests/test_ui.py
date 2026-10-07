"""A smoke test that opens the real window and uses each screen.

It needs a display, so it is skipped where there is none (for example on a
server). It uses a temporary database, never your own data.
"""

import gc
import os
import tempfile
import time
import unittest
from unittest import mock

try:
    import tkinter as tk

    _probe = tk.Tk()
    _probe.destroy()
    HAVE_DISPLAY = True
except Exception:  # no Tkinter, or nowhere to draw a window
    HAVE_DISPLAY = False


@unittest.skipUnless(HAVE_DISPLAY, "needs Tkinter and a display")
class WindowTests(unittest.TestCase):
    def setUp(self):
        from ui.main_window import MainWindow

        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.app = MainWindow(db_path=os.path.join(self.folder.name, "app.db"))
        # Tkinter objects must be cleaned up on this thread, so collect the old
        # window's leftovers here rather than leave them for a worker thread.
        self.addCleanup(gc.collect)
        self.addCleanup(self.app.destroy)

        # Pop-up boxes would wait for a click, so answer them automatically.
        self.messages = []
        for name in ("showinfo", "showerror", "showwarning"):
            patcher = mock.patch(f"tkinter.messagebox.{name}", lambda *args, **kwargs: self.messages.append(args))
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch("tkinter.messagebox.askyesno", lambda *args, **kwargs: True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def open(self, name):
        self.app._show_view(name)
        self.app.update()
        gc.collect()  # tidy up the previous screen on this thread (see setUp)
        return self.app.content_frame.winfo_children()[0]

    def wait_until(self, condition, seconds=20):
        """Keep the window responsive until condition() is true."""
        deadline = time.time() + seconds
        while time.time() < deadline:
            self.app.update()
            if condition():
                return True
            time.sleep(0.01)
        return False

    def test_every_screen_opens(self):
        for name in ("lessons", "quizzes", "challenges", "playground", "flashcards",
                     "notes", "progress", "search", "settings"):
            with self.subTest(screen=name):
                self.open(name)

    def test_lists_show_titles(self):
        for name, attribute in (("lessons", "lessons"), ("quizzes", "quizzes"), ("challenges", "challenges")):
            with self.subTest(screen=name):
                view = self.open(name)
                items = getattr(view, attribute)
                self.assertEqual(list(view.listbox.get(0, "end")), [item.title for item in items])

    def test_progress_shows_titles_rather_than_ids(self):
        self.app.progress.record_quiz("quiz_basics_01", 3, 3)
        self.app.progress.record_challenge("ch_add_01", 3, 3)
        view = self.open("progress")
        rows = [view.tree.item(row, "values") for row in view.tree.get_children()]
        self.assertEqual([row[1] for row in rows], ["Write add(a, b)", "Python Basics Quiz"])
        self.assertIn("Code Sprout", view.ach_var.get())

    def test_code_is_colored_as_it_is_shown(self):
        view = self.open("challenges")
        editor = view.editor
        self.assertEqual(editor.get("1.0", "1.3"), "def")
        self.assertIn("kw", editor.tag_names("1.0"))

    def test_lessons_open_on_the_first_lesson_without_markup(self):
        view = self.open("lessons")
        shown = view.text.get("1.0", "end")
        self.assertEqual(view.title_var.get(), view.lessons[0].title)
        self.assertIn("Variables & Types", shown)
        self.assertNotIn("###", shown)
        self.assertNotIn("```", shown)

    def test_a_correct_solution_passes_through_the_run_tests_button(self):
        view = self.open("challenges")
        view.editor.delete("1.0", "end")
        view.editor.insert("end", "def add(a, b):\n    return a + b\n")
        view.run_btn.invoke()
        self.assertEqual(str(view.run_btn["state"]), "disabled")
        self.assertTrue(self.wait_until(lambda: view.status_var.get() != "Running tests..."))
        self.assertTrue(view.status_var.get().startswith("All tests passed"), view.output.get("1.0", "end"))
        self.assertEqual(str(view.run_btn["state"]), "normal")
        self.assertIn("[PASS] small ints", view.output.get("1.0", "end"))

    def test_blocked_code_does_not_freeze_the_challenge_screen(self):
        view = self.open("challenges")
        view.editor.delete("1.0", "end")
        view.editor.insert("end", "import os\ndef add(a, b):\n    return a + b\n")
        view.run_btn.invoke()
        self.assertTrue(self.wait_until(lambda: view.status_var.get() != "Running tests..."))
        self.assertEqual(str(view.run_btn["state"]), "normal")
        self.assertIn("Imports are not allowed.", view.output.get("1.0", "end"))

    def test_leaving_a_screen_while_code_runs_is_harmless(self):
        view = self.open("challenges")
        view.run_btn.invoke()
        self.open("notes")
        # Give the finished run time to report back to a screen that no longer exists.
        self.wait_until(lambda: False, seconds=1.5)

    def test_playground_runs_code_and_feeds_input(self):
        view = self.open("playground")
        view.editor.delete("1.0", "end")
        view.editor.insert("end", "name = input()\nprint('Hello, ' + name + '!')\n")
        view.stdin_text.insert("end", "Ada")
        view.run_btn.invoke()
        self.assertTrue(self.wait_until(lambda: view.status_var.get() != "Running..."))
        self.assertEqual(view.status_var.get(), "OK")
        self.assertIn("Hello, Ada!", view.output.get("1.0", "end"))

    def test_flashcard_answer_is_hidden_until_asked_for(self):
        self.app.flashcards.add_card("What does len([1, 2]) return?", "2")
        view = self.open("flashcards")
        self.assertIn("What does len([1, 2]) return?", view.review_card.get("1.0", "end"))
        self.assertNotIn("Answer:", view.review_card.get("1.0", "end"))
        self.assertEqual(str(view.knew_btn["state"]), "disabled")

        view.show_btn.invoke()
        self.assertIn("Answer:\n2", view.review_card.get("1.0", "end"))
        self.assertEqual(str(view.knew_btn["state"]), "normal")

        view.knew_btn.invoke()
        self.assertEqual(self.app.flashcards.all_cards()[0]["box"], 2)
        self.assertIn("No cards are due", view.review_card.get("1.0", "end"))

    def test_flashcards_can_be_skipped_and_deleted(self):
        self.app.flashcards.add_card("first", "1")
        self.app.flashcards.add_card("second", "2")
        view = self.open("flashcards")
        before = view._current_due["id"]
        view.skip_btn.invoke()
        self.assertNotEqual(view._current_due["id"], before)

        view.cards_list.selection_set(0)
        view._delete()
        self.assertEqual(len(self.app.flashcards.all_cards()), 1)

    def test_quiz_is_graded(self):
        view = self.open("quizzes")
        for question in view.current_quiz.questions:
            view.answer_vars[question.id].set(question.correct_index)
        view._submit()
        self.assertTrue(any("Score: 3/3" in str(message) for message in self.messages))

    def test_switching_theme_redraws_the_sidebar(self):
        from ui.main_window import THEMES

        sidebar = self.app.winfo_children()[0]
        self.assertEqual(sidebar["bg"], THEMES["light"]["sidebar"])

        view = self.open("settings")
        view.theme_var.set("dark")
        view._save_theme()
        self.app.update()

        sidebar = self.app.winfo_children()[0]
        self.assertEqual(sidebar["bg"], THEMES["dark"]["sidebar"])
        self.assertEqual(self.app.current_view_name, "settings")

    def test_reset_everything_goes_back_to_the_light_theme(self):
        self.app.settings.set("theme", "dark")
        self.app.apply_theme()
        view = self.open("settings")
        view._reset_all()
        self.app.update()
        self.assertEqual(self.app.theme_name, "light")


if __name__ == "__main__":
    unittest.main()
