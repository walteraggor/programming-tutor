import keyword
import re

class PythonHighlighter:
    def __init__(self, text_widget, theme):
        self.text = text_widget
        self.theme = theme
        self.text.tag_configure("kw", foreground="#d73a49")  # keywords
        self.text.tag_configure("str", foreground="#a6e22e") # strings (visible in dark)
        self.text.tag_configure("com", foreground="#6a737d") # comments
        self.text.bind("<KeyRelease>", self._on_change)

    def highlight_all(self):
        txt = self.text.get("1.0","end-1c")
        self._apply(txt)

    def _on_change(self, event=None):
        self.highlight_all()

    def _apply(self, txt: str):
        for tag in ("kw","str","com"):
            self.text.tag_remove(tag, "1.0","end")

        # Very simple regex-based pass
        for match in re.finditer(r"#.*", txt):
            start = match.start()
            end = match.end()
            self._tag_range(start, end, "com")

        kwds = r"\b(" + "|".join(keyword.kwlist) + r")\b"
        for match in re.finditer(kwds, txt):
            self._tag_range(match.start(), match.end(), "kw")

        # strings: "..." or '...'
        for match in re.finditer(r"('([^'\\]|\\.)*'|\"([^\"\\]|\\.)*\")", txt, re.MULTILINE):
            self._tag_range(match.start(), match.end(), "str")

    def _tag_range(self, start_idx, end_idx, tag):
        start = "1.0 + %dc" % start_idx
        end = "1.0 + %dc" % end_idx
        self.text.tag_add(tag, start, end)