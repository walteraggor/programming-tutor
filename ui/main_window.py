import tkinter as tk
from tkinter import ttk
from backend.storage import Storage
from backend.services import (
    CatalogService, ProgressService, QuizService, RunService,
    NotesService, FlashcardsService, SettingsService, AchievementsService, DraftsService, ResetService
)
from .lessons_view import LessonsView
from .quiz_view import QuizView
from .challenge_view import ChallengeView
from .progress_view import ProgressView
from .settings_view import SettingsView
from .playground_view import PlaygroundView
from .notes_view import NotesView
from .flashcards_view import FlashcardsView
from .search_view import SearchView

THEMES = {
    "light": {"bg":"#f1faee","card":"#ffffff","text":"#000000","accent":"#457b9d","panel":"#f8f9fa","sidebar":"#1d3557","sidebar_text":"#ffffff"},
    "dark": {"bg":"#0e1117","card":"#161b22","text":"#e6edf3","accent":"#2ea043","panel":"#0d1117","sidebar":"#0b1220","sidebar_text":"#c9d1d9"},
}

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Programming Tutor v2")
        self.geometry("1200x780")
        self.minsize(1000, 650)

        # services
        self.storage = Storage()
        self.catalog = CatalogService()
        self.progress = ProgressService(self.storage)
        self.quiz = QuizService()
        self.runner = RunService()
        self.notes = NotesService(self.storage)
        self.flashcards = FlashcardsService(self.storage)
        self.settings = SettingsService(self.storage)
        self.achievements = AchievementsService(self.storage)
        self.drafts = DraftsService(self.storage)
        self.reset_service = ResetService(self.storage)

        self.theme_name = self.settings.get("theme","light")
        self.theme = THEMES.get(self.theme_name, THEMES["light"])

        self._build_layout()
        self._show_view("lessons")

    def apply_theme(self, root=None):
        # In a real app, you'd propagate styles; here we refresh current view by re-showing it
        self.theme_name = self.settings.get("theme","light")
        self.theme = THEMES.get(self.theme_name, THEMES["light"])
        self._show_view(self.current_view_name)

    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Sidebar
        sidebar = tk.Frame(self, bg=self.theme["sidebar"])
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        sidebar.config(width=220)

        title = tk.Label(sidebar, text="Programming Tutor v2",
                         fg=self.theme["sidebar_text"], bg=self.theme["sidebar"],
                         font=("Segoe UI", 14, "bold"), padx=10, pady=20, anchor="w", wraplength=200)
        title.pack(fill="x")

        def sb_btn(text, name):
            return tk.Button(sidebar, text=text, command=lambda: self._show_view(name),
                             fg=self.theme["sidebar_text"], bg=self.theme["accent"],
                             activebackground=self.theme["accent"], relief="flat", font=("Segoe UI", 11), padx=10, pady=10)

        for label, name in [
            ("Lessons","lessons"), ("Quizzes","quizzes"), ("Challenges","challenges"),
            ("Playground","playground"), ("Flashcards","flashcards"), ("Notes","notes"),
            ("Progress","progress"), ("Search","search"), ("Settings","settings")
        ]:
            sb_btn(label, name).pack(fill="x", padx=10, pady=6)

        # Content area
        self.content_frame = tk.Frame(self, bg=self.theme["bg"])
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_propagate(True)

        self.views = {}
        self.current_view_name = "lessons"

    def _show_view(self, name: str):
        for child in self.content_frame.winfo_children():
            child.destroy()
        self.current_view_name = name

        if name == "lessons":
            view = LessonsView(self.content_frame, self.catalog, self.progress, self.notes, self.theme)
        elif name == "quizzes":
            view = QuizView(self.content_frame, self.catalog, self.progress, self.theme)
        elif name == "challenges":
            view = ChallengeView(self.content_frame, self.catalog, self.progress, self.runner, self.drafts, self.theme)
        elif name == "playground":
            view = PlaygroundView(self.content_frame, self.runner, self.theme)
        elif name == "flashcards":
            view = FlashcardsView(self.content_frame, self.flashcards, self.theme)
        elif name == "notes":
            view = NotesView(self.content_frame, self.notes, self.catalog, self.theme)
        elif name == "progress":
            view = ProgressView(self.content_frame, self.progress, self.achievements, self.theme)
        elif name == "search":
            view = SearchView(self.content_frame, self.catalog, self.notes, self.flashcards, self.theme)
        elif name == "settings":
            view = SettingsView(self.content_frame, self.settings, self.reset_service, self.apply_theme, self.theme)
        else:
            view = tk.Label(self.content_frame, text="Unknown view", bg=self.theme["bg"], fg=self.theme["text"])

        view.pack(fill="both", expand=True)

def run_app():
    app = MainWindow()
    app.mainloop()