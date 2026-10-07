"""Tests for showing stored UTC timestamps in local time."""

import os
import time
import unittest

from utils.timefmt import to_local


class ToLocalTests(unittest.TestCase):
    def test_nothing_gives_an_empty_string(self):
        self.assertEqual(to_local(None), "")

    def test_text_that_is_not_a_timestamp_is_left_alone(self):
        self.assertEqual(to_local("not a time"), "not a time")

    @unittest.skipUnless(hasattr(time, "tzset"), "the time zone can only be switched like this on Linux and macOS")
    def test_utc_is_converted_to_the_local_time_zone(self):
        previous = os.environ.get("TZ")

        def restore():
            if previous is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = previous
            time.tzset()

        self.addCleanup(restore)
        os.environ["TZ"] = "TEST-9"  # a zone nine hours ahead of UTC, with no summer time
        time.tzset()

        self.assertEqual(to_local("2026-01-15 20:30:00"), "2026-01-16 05:30")
        self.assertEqual(to_local("2026-01-15 20:30:00", "%H:%M:%S"), "05:30:00")
