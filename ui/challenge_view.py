import threading
import tkinter as tk
from tkinter import ttk, messagebox
from backend.services import CatalogService, ProgressService, RunService, DraftsService
from backend.models import Challenge
from utils.syntax_highlight import PythonHighlighter

class ChallengeView(tk.Frame):
    def __init__(self, parent, catalog: CatalogService, progress: ProgressService, runner: RunService, drafts: DraftsService, theme):
        super().__init__(parent, bg=theme["bg"])
        self.catalog = catalog
        self.progress = progress
        self.runner = runner
        self.drafts = drafts
        self.theme = theme
        self._build()

    def _build(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left = tk.Frame(self, bg=self.theme["bg"])
        left.grid(row=0, column=0, sticky="ns")
        left.config(width=320)
        tk.Label(left, text="Challenges", font=("Segoe UI", 14, "bold"), bg=self.theme["bg"], fg=self.theme["text"]).pack(anchor="w", padx=10, pady=10)

        self.listbox = tk.Listbox(left, font=("Segoe UI", 11))
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        right = tk.Frame(self, bg=self.theme["card"], bd=1, relief="solid")
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(3, weight=1)
        right.rowconfigure(5, weight=1)

        self.title_var = tk.StringVar(value="Select a challenge")
        tk.Label(right, textvariable=self.title_var, font=("Segoe UI", 16, "bold"), bg=self.theme["card"], fg=self.theme["text"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.desc = tk.Text(right, height=6, wrap="word", bg=self.theme["card"], fg=self.theme["text"], font=("Segoe UI", 11))
        self.desc.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        tk.Label(right, text="Your Code:", bg=self.theme["card"], fg=self.theme["text"], font=("Segoe UI", 12, "bold")).grid(row=2, column=0, sticky="w", padx=10, pady=(10,0))
        self.editor = tk.Text(right, wrap="none", height=12, font=("Consolas", 11), bg=self.theme["panel"], fg=self.theme["text"], insertbackground=self.theme["text"])
        self.editor.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.highlighter = PythonHighlighter(self.editor, self.theme)

        run_frame = tk.Frame(right, bg=self.theme["card"])
        run_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        self.run_btn = tk.Button(run_frame, text="Run Tests", command=self._run_tests, bg=self.theme["accent"], fg="white", font=("Segoe UI", 11))
        self.run_btn.pack(side="left")
        tk.Button(run_frame, text="Save Draft", command=self._save_draft, bg=self.theme["accent"], fg="white").pack(side="left", padx=6)
        self.status_var = tk.StringVar(value="")
        tk.Label(run_frame, textvariable=self.status_var, bg=self.theme["card"], fg="#888").pack(side="left", padx=10)

        tk.Label(right, text="Results:", bg=self.theme["card"], fg=self.theme["text"], font=("Segoe UI", 12, "bold")).grid(row=5, column=0, sticky="w", padx=10)
        self.output = tk.Text(right, height=8, wrap="word", font=("Consolas", 11), bg=self.theme["panel"], fg=self.theme["text"])
        self.output.grid(row=6, column=0, sticky="nsew", padx=10, pady=(0,10))

        self.challenges = self.catalog.get_challenges()
        for c in self.challenges:
            self.listbox.insert("end", f"{c.title}  ({c.id})")
        self.current: Challenge = None

    def _on_select(self, _event=None):
        idx = self.listbox.curselection()
        if not idx: return
        self.current = self.challenges[idx[0]]
        self.title_var.set(self.current.title)
        self.desc.delete("1.0", "end")
        self.desc.insert("end", self.current.description)
        self.editor.delete("1.0", "end")
        draft = self.drafts.latest(self.current.id)
        self.editor.insert("end", draft if draft else self.current.starter_code)
        self.output.delete("1.0", "end")
        self.highlighter.highlight_all()

    def _save_draft(self):
        if not self.current: 
            messagebox.showinfo("Select", "Choose a challenge first.")
            return
        code = self.editor.get("1.0", "end")
        self.drafts.save_draft(self.current.id, code)
        messagebox.showinfo("Saved", "Draft saved.")

    def _run_tests(self):
        if not self.current: 
            messagebox.showinfo("Select", "Please choose a challenge first.")
            return
        code = self.editor.get("1.0", "end")
        self.output.delete("1.0", "end")
        self.status_var.set("Running tests...")
        self.run_btn.config(state="disabled")

        def worker():
            res = self.runner.run_challenge_tests(self.current, code, timeout=3)
            self.after(0, self._show_results, res)

        threading.Thread(target=worker, daemon=True).start()

    def _show_results(self, res):
        self.run_btn.config(state="normal")
        if res.timed_out:
            self.status_var.set("Timed out.")
        elif res.ok:
            self.status_var.set("All tests passed ✅")
        else:
            self.status_var.set("Some tests failed ❌")

        lines = []
        if res.tests_summary:
            for t in res.tests_summary:
                status = "PASS" if t.get("ok") else "FAIL"
                msg = t.get("message", "")
                lines.append(f"[{status}] {t.get('name')} {('- ' + msg) if msg else ''}")

        if res.stderr.strip():
            lines.append("\n[stderr]")
            lines.append(res.stderr.strip())
        if res.stdout.strip():
            display = res.stdout.split("__TEST_RESULTS__:", 1)[0]
            if display.strip():
                lines.append("\n[stdout]")
                lines.append(display.strip())

        self.output.insert("end", "\n".join(lines) if lines else "(no output)")

        # Save progress
        passed = sum(1 for t in (res.tests_summary or []) if t.get("ok"))
        total = len(res.tests_summary or [])
        if total:
            self.progress.record_challenge(self.current.id, passed, total)