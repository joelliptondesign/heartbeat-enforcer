"""Tests for baseline mode validation."""

import json
import os
import tempfile
import unittest

from heartbeat_enforcer.validate import validate


def make_event(timestamp):
    """Build a valid event with a deterministic timestamp."""
    return {
        "timestamp": timestamp,
        "event_type": "change_ops",
        "actor": "system-agent",
        "payload": {
            "summary": "Valid summary",
            "operations": [
                {
                    "mode": "autonomous",
                    "files": ["a.py"],
                    "action": "updated",
                    "reason": "Valid reason",
                }
            ],
        },
    }


class TestValidateBaselineMode(unittest.TestCase):
    """Test baseline mode line-count requirements."""

    def write_events(self, events):
        """Write events to a temp JSONL file."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".jsonl"
        ) as heartbeat_file:
            for event in events:
                heartbeat_file.write(json.dumps(event) + "\n")
            return heartbeat_file.name

    def test_zero_appended_lines_should_fail(self):
        """Matching baseline and current count should FAIL."""
        heartbeat_path = self.write_events([make_event("2026-03-31T10:00:00Z")])
        try:
            result = validate(heartbeat_path, baseline_count=1)
            self.assertEqual(result["status"], "FAIL")
        finally:
            os.unlink(heartbeat_path)

    def test_exactly_one_appended_line_should_pass(self):
        """Exactly one new line after the baseline should PASS."""
        heartbeat_path = self.write_events(
            [
                make_event("2026-03-31T10:00:00Z"),
                make_event("2026-03-31T10:01:00Z"),
            ]
        )
        try:
            result = validate(heartbeat_path, baseline_count=1)
            self.assertEqual(result["status"], "PASS")
        finally:
            os.unlink(heartbeat_path)

    def test_more_than_one_appended_line_should_fail(self):
        """More than one appended line should FAIL."""
        heartbeat_path = self.write_events(
            [
                make_event("2026-03-31T10:00:00Z"),
                make_event("2026-03-31T10:01:00Z"),
                make_event("2026-03-31T10:02:00Z"),
            ]
        )
        try:
            result = validate(heartbeat_path, baseline_count=1)
            self.assertEqual(result["status"], "FAIL")
        finally:
            os.unlink(heartbeat_path)


if __name__ == "__main__":
    unittest.main()
