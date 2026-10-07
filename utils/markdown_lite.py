"""A very small Markdown reader for lesson text.

It understands only what the lessons use: headings, fenced code blocks, bullet
points and `inline code`. Anything else is shown as plain text.
"""

from typing import List, Tuple

HEADING = "heading"
CODE = "code"
INLINE = "inline"
TEXT = "text"

BULLET = "  • "


def parse(markdown: str) -> List[Tuple[str, str]]:
    """Split Markdown into (text, style) pieces, in the order they are shown."""
    pieces: List[Tuple[str, str]] = []
    in_code_block = False
    for line in markdown.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            pieces.append((line + "\n", CODE))
            continue
        if stripped.startswith("#"):
            title = stripped.lstrip("#")
            if title.startswith(" "):  # "# Heading", but not "#hashtag"
                pieces.append((title.strip() + "\n", HEADING))
                continue
        if stripped.startswith("- "):
            line = BULLET + stripped[2:]
        pieces.extend(_split_inline_code(line))
        pieces.append(("\n", TEXT))
    return _merge_neighbours(pieces)


def _split_inline_code(line: str) -> List[Tuple[str, str]]:
    """Turn `backticked` parts of a line into INLINE pieces."""
    parts = line.split("`")
    if len(parts) % 2 == 0:
        # An odd number of backticks: there is no way to pair them, so keep the line as it is.
        return [(line, TEXT)]
    pieces = []
    for index, part in enumerate(parts):
        if part:
            pieces.append((part, INLINE if index % 2 else TEXT))
    return pieces


def _merge_neighbours(pieces: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Join pieces that sit next to each other and share a style."""
    merged: List[Tuple[str, str]] = []
    for text, style in pieces:
        if merged and merged[-1][1] == style:
            merged[-1] = (merged[-1][0] + text, style)
        else:
            merged.append((text, style))
    return merged


def show(text_widget, markdown: str) -> None:
    """Replace a Tk Text widget's contents with the rendered Markdown.

    The widget needs a tag configured for each style name above.
    """
    text_widget.delete("1.0", "end")
    for text, style in parse(markdown):
        text_widget.insert("end", text, style)
