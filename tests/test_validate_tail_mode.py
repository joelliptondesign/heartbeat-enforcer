"""Tests for tail mode validation."""

import json
import os
import tempfile
import unittest

from heartbeat_enforcer.validate import validate


def make_event(summary, reason):
    """Build a valid event with configurable content."""
    return {
        "timestamp": "2026-03-31T10:00:00Z",
        "event_type": "change_ops",
        "actor": "system-agent",
        "payload": {
            "summary": summary,
            "operations": [
                {
                    "mode": "autonomous",
                    "files": ["a.py"],
                    "action": "updated",
                    "reason": reason,
                }
            ],
        },
    }


class TestValidateTailMode(unittest.TestCase):
    """Test tail-mode last-event behavior."""

    def write_events(self, events):
        """Write events to a temp JSONL file."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".jsonl"
        ) as heartbeat_file:
            for event in events:
                heartbeat_file.write(json.dumps(event) + "\n")
            return heartbeat_file.name

    def test_last_event_valid_should_pass(self):
        """Tail mode should PASS when the last event is valid."""
        heartbeat_path = self.write_events(
            [
                make_event("See above for details", "Per earlier discussion, changed auth flow"),
                make_event("Valid summary", "Valid reason"),
            ]
        )
        try:
            result = validate(heartbeat_path)
            self.assertEqual(result["status"], "PASS")
        finally:
            os.unlink(heartbeat_path)

    def test_last_event_invalid_should_fail(self):
        """Tail mode should FAIL when the last event is invalid."""
        heartbeat_path = self.write_events(
            [
                make_event("Valid summary", "Valid reason"),
                make_event("See above for details", "Per earlier discussion, changed auth flow"),
            ]
        )
        try:
            result = validate(heartbeat_path)
            self.assertEqual(result["status"], "FAIL")
        finally:
            os.unlink(heartbeat_path)


if __name__ == "__main__":
    unittest.main()
