import tkinter as tk
from tkinter import ttk
from backend.services import ProgressService, AchievementsService

class ProgressView(tk.Frame):
    def __init__(self, parent, progress: ProgressService, achievements: AchievementsService, theme):
        super().__init__(parent, bg=theme["bg"])
        self.progress = progress
        self.achievements = achievements
        self.theme = theme
        self._build()
        self._refresh()

    def _build(self):
        self.columnconfigure(0, weight=1)
        tk.Label(self, text="Progress", font=("Segoe UI", 16, "bold"), bg=self.theme["bg"], fg=self.theme["text"]).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.summary_var = tk.StringVar(value="")
        tk.Label(self, textvariable=self.summary_var, bg=self.theme["bg"], fg=self.theme["text"], font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", padx=10)

        self.tree = ttk.Treeview(self, columns=("type", "id", "status", "score", "max", "when"), show="headings", height=14)
        self.tree.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        for col, w, txt in [
            ("type", 100, "Type"), ("id", 240, "Item ID"), ("status", 120, "Status"),
            ("score", 80, "Score"), ("max", 80, "Max"), ("when", 200, "Date")
        ]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor="w")
        self.rowconfigure(2, weight=1)

        # Achievements
        box = tk.LabelFrame(self, text="Achievements", bg=self.theme["bg"], fg=self.theme["text"])
        box.grid(row=3, column=0, sticky="ew", padx=10, pady=(0,10))
        self.ach_var = tk.StringVar(value="")
        tk.Label(box, textvariable=self.ach_var, bg=self.theme["bg"], fg=self.theme["text"]).pack(anchor="w", padx=10, pady=6)

        foot = tk.Frame(self, bg=self.theme["bg"])
        foot.grid(row=4, column=0, sticky="ew", padx=10, pady=(0,10))
        tk.Button(foot, text="Refresh", command=self._refresh, bg=self.theme["accent"], fg="white").pack(side="left")

    def _refresh(self):
        totals = self.progress.totals()
        score = totals.get("score", 0)
        max_score = totals.get("max_score", 0)
        self.summary_var.set(f"Total points: {score}/{max_score}")

        for row in self.tree.get_children():
            self.tree.delete(row)
        for item_type, item_id, status, score, max_score, when in self.progress.list_progress():
            self.tree.insert("", "end", values=(item_type, item_id, status, score, max_score, when))

        achs = self.achievements.list()
        if not achs:
            self.ach_var.set("No achievements yet — keep going!")
        else:
            done = [a for a in achs if a.get("achieved_at")]
            locked = [a for a in achs if not a.get("achieved_at")]
            lines = []
            if done:
                lines.append("🏆 Unlocked:")
                for a in done:
                    lines.append(f"  • {a['name']} (at {a['achieved_at']})")
            if locked:
                lines.append("\n🔒 Locked:")
                for a in locked:
                    lines.append(f"  • {a['name']}")
            self.ach_var.set("\n".join(lines))