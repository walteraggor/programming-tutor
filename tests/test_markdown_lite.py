"""Tests for the small Markdown reader used to show lessons."""

import unittest

from backend.repository import LESSONS
from utils.markdown_lite import BULLET, CODE, HEADING, INLINE, TEXT, parse


class ParseTests(unittest.TestCase):
    def test_plain_text(self):
        self.assertEqual(parse("Just a sentence."), [("Just a sentence.\n", TEXT)])

    def test_heading_loses_its_hashes(self):
        self.assertEqual(parse("### Variables & Types"), [("Variables & Types\n", HEADING)])

    def test_a_hash_without_a_space_is_not_a_heading(self):
        self.assertEqual(parse("#hashtag"), [("#hashtag\n", TEXT)])

    def test_inline_code(self):
        self.assertEqual(
            parse("Use `def` and `return`."),
            [("Use ", TEXT), ("def", INLINE), (" and ", TEXT), ("return", INLINE), (".\n", TEXT)],
        )

    def test_an_unpaired_backtick_is_left_alone(self):
        self.assertEqual(parse("A stray ` mark"), [("A stray ` mark\n", TEXT)])

    def test_code_block_keeps_its_lines_and_indentation(self):
        markdown = "Before\n```python\nif x:\n    print(x)\n```\nAfter"
        self.assertEqual(
            parse(markdown),
            [("Before\n", TEXT), ("if x:\n    print(x)\n", CODE), ("After\n", TEXT)],
        )

    def test_backticks_inside_a_code_block_are_not_inline_code(self):
        self.assertEqual(parse("```\nx = `y`\n```"), [("x = `y`\n", CODE)])

    def test_bullet_points(self):
        self.assertEqual(
            parse("- A list: `[1, 2]`"),
            [(BULLET + "A list: ", TEXT), ("[1, 2]", INLINE), ("\n", TEXT)],
        )


class LessonTextTests(unittest.TestCase):
    def test_no_markup_is_left_showing_in_any_lesson(self):
        for lesson in LESSONS:
            with self.subTest(lesson=lesson.id):
                pieces = parse(lesson.body_markdown)
                shown = "".join(text for text, _style in pieces)
                self.assertNotIn("```", shown)
                self.assertNotIn("###", shown)
                prose = "".join(text for text, style in pieces if style == TEXT)
                self.assertNotIn("`", prose)

    def test_every_lesson_has_a_heading_and_some_code(self):
        for lesson in LESSONS:
            with self.subTest(lesson=lesson.id):
                styles = {style for _text, style in parse(lesson.body_markdown)}
                self.assertIn(HEADING, styles)
                self.assertIn(CODE, styles)
                self.assertTrue(lesson.sample_code.strip())
