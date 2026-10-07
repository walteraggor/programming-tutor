"""Colors Python code in a Tk Text widget as it is typed."""

import io
import keyword
import tokenize
from typing import List, Tuple

KEYWORD = "kw"
STRING = "str"
COMMENT = "com"

# Used when a theme does not say which colors to use.
DEFAULT_COLORS = {"code_keyword": "#d73a49", "code_string": "#22863a", "code_comment": "#6a737d"}

Position = Tuple[int, int]  # (line counted from 1, column counted from 0), as Tk counts too


def find_spans(code: str) -> List[Tuple[str, Position, Position]]:
    """Find the keywords, strings and comments in some Python code.

    Python's own tokenizer does the reading, so a '#' inside a string is not
    mistaken for a comment and a keyword inside a comment is left alone.
    """
    spans = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(code).readline):
            kind = tokenize.tok_name.get(token.type, "")
            if kind == "COMMENT":
                spans.append((COMMENT, token.start, token.end))
            elif "STRING" in kind:  # ordinary strings and the parts of f-strings
                spans.append((STRING, token.start, token.end))
            elif kind == "NAME" and keyword.iskeyword(token.string):
                spans.append((KEYWORD, token.start, token.end))
    except (tokenize.TokenError, SyntaxError):
        # Half-typed code, such as an unclosed quote: keep what was found so far.
        pass
    return spans


class PythonHighlighter:
    def __init__(self, text_widget, theme):
        self.text = text_widget
        self.theme = theme
        colors = {name: theme.get(name, default) for name, default in DEFAULT_COLORS.items()}
        self.text.tag_configure(KEYWORD, foreground=colors["code_keyword"])
        self.text.tag_configure(STRING, foreground=colors["code_string"])
        self.text.tag_configure(COMMENT, foreground=colors["code_comment"])
        self.text.bind("<KeyRelease>", self._on_change)

    def highlight_all(self):
        code = self.text.get("1.0", "end-1c")
        for tag in (KEYWORD, STRING, COMMENT):
            self.text.tag_remove(tag, "1.0", "end")
        for tag, (start_line, start_col), (end_line, end_col) in find_spans(code):
            self.text.tag_add(tag, f"{start_line}.{start_col}", f"{end_line}.{end_col}")

    def _on_change(self, event=None):
        self.highlight_all()
