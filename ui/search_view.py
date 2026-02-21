import tkinter as tk
from tkinter import ttk
from backend.services import CatalogService, NotesService, FlashcardsService

class SearchView(tk.Frame):
    def __init__(self, parent, catalog: CatalogService, notes: NotesService, flashcards: FlashcardsService, theme):
        super().__init__(parent, bg=theme["bg"])
        self.catalog = catalog
        self.notes = notes
        self.flashcards = flashcards
        self.theme = theme
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        tk.Label(self, text="Search", font=("Segoe UI", 16, "bold"), bg=self.theme["bg"], fg=self.theme["text"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        bar = tk.Frame(self, bg=self.theme["bg"])
        bar.grid(row=1, column=0, sticky="ew", padx=10)
        self.q = tk.Entry(bar, width=80)
        self.q.pack(side="left", padx=6)
        tk.Button(bar, text="Search", bg=self.theme["accent"], fg="white", command=self._run).pack(side="left", padx=6)

        self.out = tk.Text(self, height=28, font=("Consolas", 11), bg=self.theme["panel"], fg=self.theme["text"])
        self.out.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.rowconfigure(2, weight=1)

    def _run(self):
        query = self.q.get().strip()
        if not query:
            return
        results = self.catalog.search_all(query)
        notes = self.notes.list(query)
        cards = self.flashcards.all_cards(query)

        lines = []
        lines.append("== Lessons ==")
        for r in results["lessons"]:
            lines.append(f" • {r['title']} ({r['id']})")
        lines.append("\n== Quizzes ==")
        for r in results["quizzes"]:
            lines.append(f" • {r['title']} ({r['id']})")
        lines.append("\n== Challenges ==")
        for r in results["challenges"]:
            lines.append(f" • {r['title']} ({r['id']})")
        lines.append("\n== Notes ==")
        for n in notes:
            lines.append(f" • #{n['id']} {n['title']}")
        lines.append("\n== Flashcards ==")
        for c in cards:
            lines.append(f" • #{c['id']} [box {c['box']}] {c['front']} -> {c['back']}")

        self.out.delete("1.0","end")
        self.out.insert("end", "\n".join(lines))