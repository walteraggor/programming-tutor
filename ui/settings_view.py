import tkinter as tk
from tkinter import messagebox
from backend.services import SettingsService, ResetService

class SettingsView(tk.Frame):
    def __init__(self, parent, settings: SettingsService, reset_service: ResetService, apply_theme_callback, theme):
        super().__init__(parent, bg=theme["bg"])
        self.settings = settings
        self.reset_service = reset_service
        self.apply_theme_callback = apply_theme_callback
        self.theme = theme
        self._build()

    def _build(self):
        tk.Label(self, text="Settings", font=("Segoe UI", 16, "bold"), bg=self.theme["bg"], fg=self.theme["text"]).pack(anchor="w", padx=10, pady=10)

        # Theme
        theme_box = tk.LabelFrame(self, text="Appearance", bg=self.theme["bg"], fg=self.theme["text"])
        theme_box.pack(fill="x", padx=10, pady=10)
        tk.Label(theme_box, text="Theme:", bg=self.theme["bg"], fg=self.theme["text"]).pack(side="left", padx=10, pady=8)
        self.theme_var = tk.StringVar(value=self.settings.get("theme","light"))
        for label, val in [("Light","light"),("Dark","dark")]:
            tk.Radiobutton(theme_box, text=label, variable=self.theme_var, value=val, command=self._save_theme,
                           bg=self.theme["bg"], fg=self.theme["text"], selectcolor=self.theme["bg"]).pack(side="left", padx=6)

        # Danger Zone
        box = tk.LabelFrame(self, text="Danger Zone", bg=self.theme["bg"], fg=self.theme["text"])
        box.pack(fill="x", padx=10, pady=10)
        tk.Label(box, text="Reset ALL data (lessons, quizzes, challenges, notes, cards, settings, achievements).", bg=self.theme["bg"], fg=self.theme["text"]).pack(anchor="w", padx=10, pady=5)
        tk.Button(box, text="Reset EVERYTHING", bg="#e63946", fg="white", command=self._reset_all).pack(anchor="w", padx=10, pady=5)

    def _save_theme(self):
        v = self.theme_var.get()
        self.settings.set("theme", v)
        self.apply_theme_callback()

    def _reset_all(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to reset ALL data?"):
            self.reset_service.reset_all()
            messagebox.showinfo("Done", "All data reset.")