import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from backend.services import CatalogService, ProgressService, NotesService
from backend.models import Lesson

class LessonsView(tk.Frame):
    def __init__(self, parent, catalog: CatalogService, progress: ProgressService, notes: NotesService, theme):
        super().__init__(parent, bg=theme["bg"])
        self.catalog = catalog
        self.progress = progress
        self.notes = notes
        self.theme = theme
        self._build()

    def _build(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # left list
        left = tk.Frame(self, bg=self.theme["bg"])
        left.grid(row=0, column=0, sticky="ns")
        left.grid_propagate(False)
        left.config(width=320)

        tk.Label(left, text="Lessons", font=("Segoe UI", 14, "bold"),
                 bg=self.theme["bg"], fg=self.theme["text"]).pack(anchor="w", padx=10, pady=10)

        self.listbox = tk.Listbox(left, font=("Segoe UI", 11))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        # right content
        right = tk.Frame(self, bg=self.theme["card"], bd=1, relief="solid")
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        self.title_var = tk.StringVar(value="Select a lesson")
        tk.Label(right, textvariable=self.title_var, font=("Segoe UI", 16, "bold"),
                 bg=self.theme["card"], fg=self.theme["text"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.text = tk.Text(right, wrap="word", bg=self.theme["card"], fg=self.theme["text"], font=("Consolas", 11))
        self.text.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0,10))

        self.sample_label = tk.Label(right, text="Sample Code:", bg=self.theme["card"], fg=self.theme["text"], font=("Segoe UI", 12, "bold"))
        self.sample_label.grid(row=3, column=0, sticky="w", padx=10, pady=(5,0))
        self.sample_text = tk.Text(right, height=8, wrap="word", bg=self.theme["panel"], fg=self.theme["text"], font=("Consolas", 11))
        self.sample_text.grid(row=4, column=0, sticky="ew", padx=10, pady=(0,10))

        tools = tk.Frame(right, bg=self.theme["card"])
        tools.grid(row=5, column=0, sticky="ew", padx=10, pady=10)
        tk.Button(tools, text="Mark as Viewed", command=self._mark_viewed, bg=self.theme["accent"], fg="white", font=("Segoe UI", 11)).pack(side="right", padx=5)
        tk.Button(tools, text="Add Note", command=self._add_note_dialog, bg=self.theme["accent"], fg="white", font=("Segoe UI", 11)).pack(side="right", padx=5)

        # load data
        self.lessons = self.catalog.get_lessons()
        for l in self.lessons:
            self.listbox.insert("end", f"{l.title}  ({l.id})")
        self.current: Optional[Lesson] = None

    def _on_select(self, _event=None):
        idx = self.listbox.curselection()
        if not idx:
            return
        lesson = self.lessons[idx[0]]
        self.current = lesson
        self.title_var.set(lesson.title)
        self.text.delete("1.0", "end")
        self.text.insert("end", lesson.body_markdown)
        self.sample_text.delete("1.0", "end")
        if lesson.sample_code:
            self.sample_text.insert("end", lesson.sample_code)

    def _mark_viewed(self):
        if not self.current:
            return
        self.progress.record_viewed(self.current.id)
        messagebox.showinfo("Saved", f"Marked lesson '{self.current.title}' as viewed.")

    def _add_note_dialog(self):
        if not self.current:
            messagebox.showinfo("Select lesson", "Open a lesson first.")
            return
        dlg = tk.Toplevel(self)
        dlg.title("Add Note")
        tk.Label(dlg, text="Title:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        title_e = tk.Entry(dlg, width=60)
        title_e.grid(row=0, column=1, padx=8, pady=8)
        tk.Label(dlg, text="Content:").grid(row=1, column=0, sticky="nw", padx=8, pady=8)
        body_t = tk.Text(dlg, width=60, height=10)
        body_t.grid(row=1, column=1, padx=8, pady=8)

        def save():
            t = title_e.get().strip()
            c = body_t.get("1.0","end").strip()
            if not t or not c:
                messagebox.showerror("Missing", "Title and content required.")
                return
            self.notes.add(t, c, self.current.id)
            dlg.destroy()
            messagebox.showinfo("Saved", "Note added.")

        tk.Button(dlg, text="Save", command=save).grid(row=2, column=1, sticky="e", padx=8, pady=8)