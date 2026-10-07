import tkinter as tk
from tkinter import messagebox
from backend.services import FlashcardsService

class FlashcardsView(tk.Frame):
    def __init__(self, parent, flashcards: FlashcardsService, theme):
        super().__init__(parent, bg=theme["bg"])
        self.flashcards = flashcards
        self.theme = theme
        self._due = []          # cards waiting to be reviewed
        self._position = 0      # which of the due cards is on screen
        self._revealed = False  # whether the answer is showing
        self._rows = []         # the cards in the list at the bottom
        self._query = ""
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
        tk.Button(tools, text="Delete Selected", command=self._delete, bg="#e63946", fg="white").pack(side="left", padx=8)

        self.review_card = tk.Text(self, height=6, wrap="word", font=("Consolas", 11), bg=self.theme["panel"], fg=self.theme["text"])
        self.review_card.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,6))

        rvtools = tk.Frame(self, bg=self.theme["bg"])
        rvtools.grid(row=3, column=0, sticky="ew", padx=10, pady=(0,8))
        self.show_btn = tk.Button(rvtools, text="Show Answer", command=self._reveal, bg=self.theme["accent"], fg="white")
        self.show_btn.pack(side="left", padx=4)
        self.knew_btn = tk.Button(rvtools, text="I Knew It", command=lambda: self._grade(True), bg="#2ea043", fg="white")
        self.knew_btn.pack(side="left", padx=4)
        self.forgot_btn = tk.Button(rvtools, text="I Forgot", command=lambda: self._grade(False), bg="#e63946", fg="white")
        self.forgot_btn.pack(side="left", padx=4)
        self.skip_btn = tk.Button(rvtools, text="Skip", command=self._skip, bg=self.theme["accent"], fg="white")
        self.skip_btn.pack(side="left", padx=8)
        self.due_var = tk.StringVar(value="")
        tk.Label(rvtools, textvariable=self.due_var, bg=self.theme["bg"], fg="#888").pack(side="left", padx=10)

        self.cards_list = tk.Listbox(self, font=("Segoe UI", 11), height=10, exportselection=False, bg=self.theme["card"], fg=self.theme["text"], selectbackground=self.theme["accent"], selectforeground="white")
        self.cards_list.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        self.rowconfigure(4, weight=1)

    @property
    def _current_due(self):
        return self._due[self._position] if self._due else None

    def _refresh(self):
        """Reload everything from storage and show the card that is now due."""
        self._due = self.flashcards.due_cards()
        self._position = min(self._position, max(len(self._due) - 1, 0))
        self._revealed = False
        self._show_card()
        self._reload_list()

    def _show_card(self):
        card = self._current_due
        self.review_card.delete("1.0", "end")
        if card is None:
            self.review_card.insert("end", "No cards are due. Add a card, or come back later.")
            self.due_var.set("No cards due")
        elif self._revealed:
            self.review_card.insert("end", f"Question:\n{card['front']}\n\nAnswer:\n{card['back']}")
        else:
            self.review_card.insert("end", f"Question:\n{card['front']}\n\nThink of the answer, then press Show Answer.")
        if card is not None:
            count = len(self._due)
            self.due_var.set(f"{count} card{'' if count == 1 else 's'} due")

        # The answer has to be seen before it can be marked right or wrong.
        waiting_for_answer = card is not None and not self._revealed
        self.show_btn.config(state="normal" if waiting_for_answer else "disabled")
        grading = "normal" if (card is not None and self._revealed) else "disabled"
        self.knew_btn.config(state=grading)
        self.forgot_btn.config(state=grading)
        self.skip_btn.config(state="normal" if len(self._due) > 1 else "disabled")

    def _reveal(self):
        if self._current_due is None:
            return
        self._revealed = True
        self._show_card()

    def _skip(self):
        if len(self._due) < 2:
            return
        self._position = (self._position + 1) % len(self._due)
        self._revealed = False
        self._show_card()

    def _reload_list(self):
        self.cards_list.delete(0, "end")
        self._rows = self.flashcards.all_cards(self._query if self._query else None)
        for r in self._rows:
            self.cards_list.insert("end", f"#{r['id']} [box {r['box']}] {r['front']} -> {r['back']}")

    def _grade(self, correct: bool):
        if self._current_due is None or not self._revealed:
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

    def _delete(self):
        idx = self.cards_list.curselection()
        if not idx:
            messagebox.showinfo("Select", "Choose a card in the list first.")
            return
        row = self._rows[idx[0]]
        if messagebox.askyesno("Confirm", f"Delete card #{row['id']}?"):
            self.flashcards.delete(int(row["id"]))
            self._refresh()

    def _search(self):
        self._query = self.search_e.get().strip()
        self._reload_list()
