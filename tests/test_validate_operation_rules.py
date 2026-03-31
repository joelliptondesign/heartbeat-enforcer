"""Tests for operation-level validation rules."""

import json
import os
import tempfile
import unittest

from heartbeat_enforcer.validate import validate


def make_event(files=None, mode="autonomous", action="updated", reason="Valid reason"):
    """Build a minimally valid heartbeat event."""
    return {
        "timestamp": "2026-03-31T10:00:00Z",
        "event_type": "change_ops",
        "actor": "system-agent",
        "payload": {
            "summary": "Valid summary",
            "operations": [
                {
                    "mode": mode,
                    "files": ["a.py"] if files is None else files,
                    "action": action,
                    "reason": reason,
                }
            ],
        },
    }


class TestValidateOperationRules(unittest.TestCase):
    """Test operation validation rules."""

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

    def test_invalid_mode_should_fail(self):
        """Operation mode outside the allowed set should FAIL."""
        result = self.run_validate(make_event(mode="invalid"))
        self.assertEqual(result["status"], "FAIL")

    def test_empty_files_should_fail(self):
        """Empty files list should FAIL."""
        result = self.run_validate(make_event(files=[]))
        self.assertEqual(result["status"], "FAIL")

    def test_empty_action_should_fail(self):
        """Empty action should FAIL."""
        result = self.run_validate(make_event(action=""))
        self.assertEqual(result["status"], "FAIL")

    def test_empty_reason_should_fail(self):
        """Empty reason should FAIL."""
        result = self.run_validate(make_event(reason=""))
        self.assertEqual(result["status"], "FAIL")

    def test_duplicate_files_should_fail(self):
        """Duplicate files in a single operation should FAIL."""
        result = self.run_validate(make_event(files=["a.py", "a.py"]))
        self.assertEqual(result["status"], "FAIL")

    def test_non_string_file_entry_should_fail(self):
        """Non-string file entries should FAIL."""
        result = self.run_validate(make_event(files=["a.py", 123]))
        self.assertEqual(result["status"], "FAIL")

    def test_empty_string_file_entry_should_fail(self):
        """Empty string file entries should FAIL."""
        result = self.run_validate(make_event(files=["a.py", ""]))
        self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
