import tkinter as tk
from tkinter import ttk, messagebox
from backend.services import NotesService, CatalogService
from utils.timefmt import to_local

class NotesView(tk.Frame):
    def __init__(self, parent, notes: NotesService, catalog: CatalogService, theme):
        super().__init__(parent, bg=theme["bg"])
        self.notes = notes
        self.catalog = catalog
        self.theme = theme
        self._build()
        self._refresh()

    def _build(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left = tk.Frame(self, bg=self.theme["bg"])
        left.grid(row=0, column=0, sticky="ns")
        left.config(width=320)

        tk.Label(left, text="Notes", font=("Segoe UI", 14, "bold"), bg=self.theme["bg"], fg=self.theme["text"]).pack(anchor="w", padx=10, pady=10)

        qf = tk.Frame(left, bg=self.theme["bg"])
        qf.pack(fill="x", padx=10)
        self.q_entry = tk.Entry(qf)
        self.q_entry.pack(side="left", expand=True, fill="x")
        tk.Button(qf, text="Search", bg=self.theme["accent"], fg="white", command=self._refresh).pack(side="left", padx=5)
        tk.Button(qf, text="New", bg=self.theme["accent"], fg="white", command=self._new).pack(side="left", padx=5)

        self.listbox = tk.Listbox(left, font=("Segoe UI", 11), width=34, exportselection=False, bg=self.theme["card"], fg=self.theme["text"], selectbackground=self.theme["accent"], selectforeground="white")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self._show_selected)

        # right
        right = tk.Frame(self, bg=self.theme["card"], bd=1, relief="solid")
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        self.title_var = tk.StringVar(value="Select a note")
        tk.Label(right, textvariable=self.title_var, bg=self.theme["card"], fg=self.theme["text"], font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.content_t = tk.Text(right, wrap="word", bg=self.theme["panel"], fg=self.theme["text"], font=("Consolas", 11))
        self.content_t.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        btns = tk.Frame(right, bg=self.theme["card"])
        btns.grid(row=2, column=0, sticky="e", padx=10, pady=(0,10))
        self.del_btn = tk.Button(btns, text="Delete", command=self._delete, bg="#e63946", fg="white")
        self.del_btn.pack(side="right")

        self._rows = []

    def _refresh(self):
        q = self.q_entry.get().strip()
        self._rows = self.notes.list(q if q else None)
        self.listbox.delete(0,"end")
        for r in self._rows:
            ttl = r["title"]
            when = r["created_at"]
            self.listbox.insert("end", f"{ttl} — {to_local(when)}")

    def _show_selected(self, _evt=None):
        idx = self.listbox.curselection()
        if not idx: return
        row = self._rows[idx[0]]
        self.title_var.set(row["title"])
        self.content_t.delete("1.0","end")
        self.content_t.insert("end", row["content"])

    def _new(self):
        dlg = tk.Toplevel(self)
        dlg.title("New Note")
        tk.Label(dlg, text="Title:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        title_e = tk.Entry(dlg, width=60)
        title_e.grid(row=0, column=1, padx=8, pady=8)
        tk.Label(dlg, text="Content:").grid(row=1, column=0, sticky="nw", padx=8, pady=8)
        body_t = tk.Text(dlg, width=60, height=12)
        body_t.grid(row=1, column=1, padx=8, pady=8)

        lessons = self.catalog.get_lessons()
        tk.Label(dlg, text="Related lesson (optional):").grid(row=2, column=0, sticky="w", padx=8)
        rel_var = tk.StringVar(value="")
        cmb = ttk.Combobox(dlg, textvariable=rel_var, values=[""] + [l.id for l in lessons], width=40)
        cmb.grid(row=2, column=1, sticky="w", padx=8, pady=8)

        def save():
            t = title_e.get().strip()
            c = body_t.get("1.0","end").strip()
            rel = rel_var.get().strip() or None
            if not t or not c:
                messagebox.showerror("Missing", "Title and content required.")
                return
            self.notes.add(t, c, rel)
            dlg.destroy()
            self._refresh()

        tk.Button(dlg, text="Save", command=save).grid(row=3, column=1, sticky="e", padx=8, pady=8)

    def _delete(self):
        idx = self.listbox.curselection()
        if not idx: return
        row = self._rows[idx[0]]
        rid = int(row["id"])
        if messagebox.askyesno("Confirm", f"Delete note #{rid}?"):
            self.notes.delete(rid)
            self._refresh()
            self.title_var.set("Select a note")
            self.content_t.delete("1.0","end")