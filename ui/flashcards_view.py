import tkinter as tk
from tkinter import ttk, messagebox
from backend.services import FlashcardsService

class FlashcardsView(tk.Frame):
    def __init__(self, parent, flashcards: FlashcardsService, theme):
        super().__init__(parent, bg=theme["bg"])
        self.flashcards = flashcards
        self.theme = theme
        self._build()
        self._refresh()

    def _build(self):
        self.columnconfigure(0, weight=1)
        tk.Label(self, text="Flashcards (SRS)", font=("Segoe UI", 16, "bold"), bg=self.theme["bg"], fg=self.theme["text"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        tools = tk.Frame(self, bg=self.theme["bg"])
        tools.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,8))
        tk.Button(tools, text="Add Card", command=self._add, bg=self.theme["accent"], fg="white").pack(side="left")
        self.search_e = tk.Entry(tools, width=40)
        self.search_e.pack(side="left", padx=8)
        tk.Button(tools, text="Search", command=self._search, bg=self.theme["accent"], fg="white").pack(side="left")

        self.review_card = tk.Text(self, height=6, font=("Consolas", 11), bg=self.theme["panel"], fg=self.theme["text"])
        self.review_card.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,6))

        rvtools = tk.Frame(self, bg=self.theme["bg"])
        rvtools.grid(row=3, column=0, sticky="ew", padx=10, pady=(0,8))
        tk.Button(rvtools, text="I Knew It", command=lambda: self._grade(True), bg="#2ea043", fg="white").pack(side="left", padx=4)
        tk.Button(rvtools, text="I Forgot", command=lambda: self._grade(False), bg="#e63946", fg="white").pack(side="left", padx=4)
        tk.Button(rvtools, text="Next Due", command=self._refresh, bg=self.theme["accent"], fg="white").pack(side="left", padx=8)

        self.cards_list = tk.Listbox(self, font=("Segoe UI", 11), height=10)
        self.cards_list.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        self.rowconfigure(4, weight=1)

        self._current_due = None

    def _refresh(self):
        due = self.flashcards.due_cards()
        self._current_due = due[0] if due else None
        self.review_card.delete("1.0","end")
        if self._current_due:
            self.review_card.insert("end", f"Front:\n{self._current_due['front']}\n\nBack (click 'I Knew It' to reveal in mind, or 'I Forgot'):\n{self._current_due['back']}")
        else:
            self.review_card.insert("end", "No cards due. Add or search cards below.")
        self._reload_list()

    def _reload_list(self, query: str = ""):
        self.cards_list.delete(0,"end")
        rows = self.flashcards.all_cards(query if query else None)
        for r in rows:
            self.cards_list.insert("end", f"#{r['id']} [box {r['box']}] {r['front']} -> {r['back']}")

    def _grade(self, correct: bool):
        if not self._current_due:
            return
        self.flashcards.review(self._current_due["id"], correct)
        self._refresh()

    def _add(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add Flashcard")
        tk.Label(dlg, text="Front:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        e1 = tk.Entry(dlg, width=60)
        e1.grid(row=0, column=1, padx=8, pady=8)
        tk.Label(dlg, text="Back:").grid(row=1, column=0, sticky="w", padx=8, pady=8)
        e2 = tk.Entry(dlg, width=60)
        e2.grid(row=1, column=1, padx=8, pady=8)
        def save():
            a = e1.get().strip(); b = e2.get().strip()
            if not a or not b:
                messagebox.showerror("Missing", "Both sides required.")
                return
            self.flashcards.add_card(a, b)
            dlg.destroy()
            self._refresh()
        tk.Button(dlg, text="Save", command=save).grid(row=2, column=1, sticky="e", padx=8, pady=8)

    def _search(self):
        q = self.search_e.get().strip()
        self._reload_list(q)