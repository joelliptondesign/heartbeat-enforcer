"""Tests for exact file coverage validation."""

import json
import os
import tempfile
import unittest

from heartbeat_enforcer.validate import validate


def make_event(files):
    """Build a valid event with specified file coverage."""
    return {
        "timestamp": "2026-03-31T10:00:00Z",
        "event_type": "change_ops",
        "actor": "system-agent",
        "payload": {
            "summary": "Valid summary",
            "operations": [
                {
                    "mode": "autonomous",
                    "files": files,
                    "action": "updated",
                    "reason": "Valid reason",
                }
            ],
        },
    }


class TestValidateCoverage(unittest.TestCase):
    """Test changed-files coverage matching."""

    def write_heartbeat(self, event):
        """Write one heartbeat event to a temp JSONL file."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".jsonl"
        ) as heartbeat_file:
            heartbeat_file.write(json.dumps(event) + "\n")
            return heartbeat_file.name

    def write_changed_files(self, files):
        """Write expected changed files to a temp text file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as changed_file:
            for file_name in files:
                changed_file.write(file_name + "\n")
            return changed_file.name

    def test_exact_match_should_pass(self):
        """Exact file coverage should PASS."""
        heartbeat_path = self.write_heartbeat(make_event(["a.py", "b.py"]))
        changed_files_path = self.write_changed_files(["a.py", "b.py"])
        try:
            result = validate(heartbeat_path, changed_files_path=changed_files_path)
            self.assertEqual(result["status"], "PASS")
        finally:
            os.unlink(heartbeat_path)
            os.unlink(changed_files_path)

    def test_missing_file_should_fail(self):
        """Missing a changed file should FAIL."""
        heartbeat_path = self.write_heartbeat(make_event(["a.py"]))
        changed_files_path = self.write_changed_files(["a.py", "b.py"])
        try:
            result = validate(heartbeat_path, changed_files_path=changed_files_path)
            self.assertEqual(result["status"], "FAIL")
        finally:
            os.unlink(heartbeat_path)
            os.unlink(changed_files_path)

    def test_extra_file_should_fail(self):
        """Including an extra file should FAIL."""
        heartbeat_path = self.write_heartbeat(make_event(["a.py", "b.py"]))
        changed_files_path = self.write_changed_files(["a.py"])
        try:
            result = validate(heartbeat_path, changed_files_path=changed_files_path)
            self.assertEqual(result["status"], "FAIL")
        finally:
            os.unlink(heartbeat_path)
            os.unlink(changed_files_path)


if __name__ == "__main__":
    unittest.main()
