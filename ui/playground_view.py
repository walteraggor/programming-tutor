import threading
import tkinter as tk
from tkinter import ttk
from backend.services import RunService

class PlaygroundView(tk.Frame):
    def __init__(self, parent, runner: RunService, theme):
        super().__init__(parent, bg=theme["bg"])
        self.runner = runner
        self.theme = theme
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        tk.Label(self, text="Playground", font=("Segoe UI", 16, "bold"), bg=self.theme["bg"], fg=self.theme["text"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        ed_frame = tk.Frame(self, bg=self.theme["bg"])
        ed_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,5))
        tk.Label(ed_frame, text="stdin (optional):", bg=self.theme["bg"], fg=self.theme["text"]).pack(side="left")
        self.stdin_entry = tk.Entry(ed_frame, width=60)
        self.stdin_entry.pack(side="left", padx=6)
        tk.Button(ed_frame, text="Run", bg=self.theme["accent"], fg="white", command=self._run).pack(side="left", padx=6)

        self.editor = tk.Text(self, height=16, font=("Consolas", 11), bg=self.theme["panel"], fg=self.theme["text"])
        self.editor.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.editor.insert("end", "# Write code and press Run.\nprint('Hello, world!')\n")

        out_frame = tk.Frame(self, bg=self.theme["bg"])
        out_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0,5))
        tk.Label(out_frame, text="Output:", bg=self.theme["bg"], fg=self.theme["text"]).pack(side="left")
        self.status_var = tk.StringVar(value="")
        tk.Label(out_frame, textvariable=self.status_var, bg=self.theme["bg"], fg="#888").pack(side="left", padx=10)

        self.output = tk.Text(self, height=10, font=("Consolas", 11), bg=self.theme["panel"], fg=self.theme["text"])
        self.output.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0,10))

    def _run(self):
        code = self.editor.get("1.0","end")
        stdin = self.stdin_entry.get()
        self.output.delete("1.0","end")
        self.status_var.set("Running...")

        def worker():
            res = self.runner.run_arbitrary(code, stdin=stdin, timeout=3)
            self.after(0, lambda: self._show(res))

        threading.Thread(target=worker, daemon=True).start()

    def _show(self, res):
        self.status_var.set("OK" if res.ok else "Error")
        text = []
        if res.stderr.strip():
            text.append("[stderr]\n" + res.stderr.strip())
        if res.stdout.strip():
            text.append("[stdout]\n" + res.stdout.strip())
        if not text:
            text = ["(no output)"]
        self.output.insert("end", "\n\n".join(text))
