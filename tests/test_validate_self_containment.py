"""Tests for self-containment phrase detection."""

import json
import os
import tempfile
import unittest

from heartbeat_enforcer.validate import validate


def make_event(summary="Valid summary", reason="Valid reason"):
    """Build a valid event with configurable summary and reason."""
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


class TestValidateSelfContainment(unittest.TestCase):
    """Test banned phrase rejection."""

    def run_validate(self, event):
        """Write one event to a temp JSONL file and validate it."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".jsonl"
        ) as heartbeat_file:
            heartbeat_file.write(json.dumps(event) + "\n")
            heartbeat_path = heartbeat_file.name

        try:
            return validate(heartbeat_path)
        finally:
            os.unlink(heartbeat_path)

    def test_banned_phrase_in_summary_should_fail(self):
        """Banned phrase in summary should FAIL."""
        result = self.run_validate(make_event(summary="See above for details"))
        self.assertEqual(result["status"], "FAIL")

    def test_banned_phrase_in_reason_should_fail(self):
        """Banned phrase in reason should FAIL."""
        result = self.run_validate(make_event(reason="Per earlier discussion, updated auth"))
        self.assertEqual(result["status"], "FAIL")

    def test_case_insensitive_banned_phrase_should_fail(self):
        """Case-insensitive banned phrase detection should FAIL."""
        result = self.run_validate(make_event(summary="As Discussed, the module was updated"))
        self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
