"""Tests for finding the parts of Python code that get colored."""

import unittest

from utils.syntax_highlight import COMMENT, KEYWORD, STRING, find_spans


def kinds(code):
    return [kind for kind, _start, _end in find_spans(code)]


class FindSpansTests(unittest.TestCase):
    def test_keywords_with_their_positions(self):
        self.assertEqual(
            find_spans("def f():\n    return 1\n"),
            [(KEYWORD, (1, 0), (1, 3)), (KEYWORD, (2, 4), (2, 10))],
        )

    def test_a_hash_inside_a_string_is_not_a_comment(self):
        self.assertEqual(
            find_spans("x = '#1'  # note"),
            [(STRING, (1, 4), (1, 8)), (COMMENT, (1, 10), (1, 16))],
        )

    def test_keywords_inside_strings_and_comments_are_left_alone(self):
        self.assertEqual(kinds("s = 'if else'  # return for"), [STRING, COMMENT])

    def test_names_that_merely_contain_a_keyword(self):
        self.assertEqual(kinds("format = 1\nisinstance(x, int)\nimportant = notify"), [])

    def test_a_string_over_several_lines(self):
        self.assertEqual(find_spans('s = """a\nb"""'), [(STRING, (1, 4), (2, 4))])

    def test_f_strings_count_as_strings(self):
        found = kinds("f'{total} items'")
        self.assertTrue(found)
        self.assertEqual(set(found), {STRING})

    def test_half_typed_code_keeps_what_was_found_so_far(self):
        found = find_spans("def f():\n    x = 'never closed")
        self.assertIn((KEYWORD, (1, 0), (1, 3)), found)

    def test_empty_code(self):
        self.assertEqual(find_spans(""), [])
