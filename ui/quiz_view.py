import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict
from backend.services import CatalogService, ProgressService, QuizService
from backend.models import Quiz

class QuizView(tk.Frame):
    def __init__(self, parent, catalog: CatalogService, progress: ProgressService, theme):
        super().__init__(parent, bg=theme["bg"])
        self.catalog = catalog
        self.progress = progress
        self.quiz_service = QuizService()
        self.theme = theme
        self._build()

    def _build(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # left
        left = tk.Frame(self, bg=self.theme["bg"])
        left.grid(row=0, column=0, sticky="ns")
        left.config(width=320)
        tk.Label(left, text="Quizzes", font=("Segoe UI", 14, "bold"), bg=self.theme["bg"], fg=self.theme["text"]).pack(anchor="w", padx=10, pady=10)
        self.listbox = tk.Listbox(left, font=("Segoe UI", 11))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        # right
        right = tk.Frame(self, bg=self.theme["card"], bd=1, relief="solid")
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        self.title_var = tk.StringVar(value="Select a quiz")
        tk.Label(right, textvariable=self.title_var, bg=self.theme["card"], fg=self.theme["text"], font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.container = tk.Frame(right, bg=self.theme["card"])
        self.container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.container.columnconfigure(0, weight=1)

        self.submit_btn = tk.Button(right, text="Submit Quiz", command=self._submit, bg=self.theme["accent"], fg="white", font=("Segoe UI", 11))
        self.submit_btn.grid(row=2, column=0, sticky="e", padx=10, pady=10)

        # load
        self.quizzes = self.catalog.get_quizzes()
        for q in self.quizzes:
            self.listbox.insert("end", f"{q.title}  ({q.id})")

        self.current_quiz: Quiz = None
        self.answer_vars: Dict[str, tk.IntVar] = {}

    def _on_select(self, _event=None):
        idx = self.listbox.curselection()
        if not idx: return
        self.current_quiz = self.quizzes[idx[0]]
        self.title_var.set(self.current_quiz.title)
        for child in self.container.winfo_children():
            child.destroy()
        self.answer_vars.clear()

        for i, q in enumerate(self.current_quiz.questions):
            frame = tk.LabelFrame(self.container, text=f"Q{i+1}. {q.prompt}", bg=self.theme["card"], fg=self.theme["text"])
            frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            var = tk.IntVar(value=-1)
            self.answer_vars[q.id] = var
            for j, opt in enumerate(q.options):
                rb = tk.Radiobutton(frame, text=opt, variable=var, value=j, bg=self.theme["card"], fg=self.theme["text"], anchor="w", justify="left")
                rb.pack(fill="x", padx=10, pady=2)

    def _submit(self):
        if not self.current_quiz:
            return
        answers = {qid: var.get() for qid, var in self.answer_vars.items()}
        result = self.quiz_service.grade(self.current_quiz, answers)
        # Save progress
        self.progress.record_quiz(self.current_quiz.id, result.correct, result.total)
        # Show summary
        msg_lines = [f"Score: {result.correct}/{result.total}", ""]
        for d in result.details:
            status = "✅ Correct" if d["correct"] else "❌ Incorrect"
            msg_lines.append(f"{d['question_id']}: {status}\n→ {d['explanation']}")
        messagebox.showinfo("Quiz Results", "\n\n".join(msg_lines))
