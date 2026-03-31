"""Tests against the sample repository heartbeat file."""

import json
import os
import tempfile
import unittest

from heartbeat_enforcer.validate import validate


class TestSampleRepo(unittest.TestCase):
    """Test deterministic sample repo scenarios."""

    def setUp(self):
        """Set up sample repo paths."""
        self.heartbeat_path = os.path.join(
            os.path.dirname(__file__), "..", "sample_repo", "telemetry", "executor_heartbeat.jsonl"
        )

    def test_validate_first_event_should_pass(self):
        """The first sample event alone should PASS."""
        with open(self.heartbeat_path, "r") as heartbeat_file:
            first_line = heartbeat_file.readline()

        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".jsonl"
        ) as temp_heartbeat:
            temp_heartbeat.write(first_line)
            temp_path = temp_heartbeat.name

        try:
            result = validate(temp_path)
            self.assertEqual(result["status"], "PASS")
        finally:
            os.unlink(temp_path)

    def test_validate_second_event_should_fail(self):
        """The second sample event should FAIL in tail mode."""
        result = validate(self.heartbeat_path)
        self.assertEqual(result["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
