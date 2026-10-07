import tkinter as tk
from backend.models import RunResult
from backend.services import RunService
from utils.syntax_highlight import PythonHighlighter
from .background import run_in_background

class PlaygroundView(tk.Frame):
    def __init__(self, parent, runner: RunService, theme):
        super().__init__(parent, bg=theme["bg"])
        self.runner = runner
        self.theme = theme
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(5, weight=1)

        tk.Label(self, text="Playground", font=("Segoe UI", 16, "bold"), bg=self.theme["bg"], fg=self.theme["text"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.editor = tk.Text(self, height=14, font=("Consolas", 11), bg=self.theme["panel"], fg=self.theme["text"], insertbackground=self.theme["text"])
        self.editor.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.editor.insert("end", "# Write code and press Run.\nprint('Hello, world!')\n")
        self.highlighter = PythonHighlighter(self.editor, self.theme)
        self.highlighter.highlight_all()

        tk.Label(self, text="Input for input() (optional, one line for each call):", bg=self.theme["bg"], fg=self.theme["text"]).grid(row=2, column=0, sticky="w", padx=10)
        self.stdin_text = tk.Text(self, height=3, font=("Consolas", 11), bg=self.theme["panel"], fg=self.theme["text"], insertbackground=self.theme["text"])
        self.stdin_text.grid(row=3, column=0, sticky="ew", padx=10, pady=(0,10))

        out_frame = tk.Frame(self, bg=self.theme["bg"])
        out_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(0,5))
        self.run_btn = tk.Button(out_frame, text="Run", bg=self.theme["accent"], fg="white", font=("Segoe UI", 11), command=self._run)
        self.run_btn.pack(side="left")
        tk.Label(out_frame, text="Output:", bg=self.theme["bg"], fg=self.theme["text"]).pack(side="left", padx=(12,0))
        self.status_var = tk.StringVar(value="")
        tk.Label(out_frame, textvariable=self.status_var, bg=self.theme["bg"], fg="#888").pack(side="left", padx=10)

        self.output = tk.Text(self, height=10, font=("Consolas", 11), bg=self.theme["panel"], fg=self.theme["text"])
        self.output.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0,10))

    def _run(self):
        code = self.editor.get("1.0", "end")
        stdin = self.stdin_text.get("1.0", "end-1c")
        self.output.delete("1.0", "end")
        self.status_var.set("Running...")
        self.run_btn.config(state="disabled")
        run_in_background(
            self,
            lambda: self.runner.run_arbitrary(code, stdin=stdin, timeout=3),
            self._show,
        )

    def _show(self, res):
        self.run_btn.config(state="normal")
        if isinstance(res, Exception):
            # Something unexpected went wrong in the runner itself; say so rather than hang.
            res = RunResult(ok=False, stdout="", stderr=f"Could not run the code: {res}", timed_out=False)
        if res.timed_out:
            self.status_var.set("Timed out")
        else:
            self.status_var.set("OK" if res.ok else "Error")
        text = []
        if res.stderr.strip():
            text.append("[stderr]\n" + res.stderr.strip())
        if res.stdout.strip():
            text.append("[stdout]\n" + res.stdout.strip())
        if res.timed_out:
            text.append("The code was stopped because it ran for more than 3 seconds.")
        if not text:
            text = ["(no output)"]
        self.output.delete("1.0", "end")
        self.output.insert("end", "\n\n".join(text))
