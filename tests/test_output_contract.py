"""Tests for the validator output contract."""

import json
import os
import tempfile
import unittest

from heartbeat_enforcer.validate import validate


def make_event(summary="Valid summary", reason="Valid reason"):
    """Build a valid event with configurable text."""
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


class TestOutputContract(unittest.TestCase):
    """Test PASS and FAIL response shapes."""

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

    def test_pass_result_should_match_contract(self):
        """PASS output should be exactly the PASS contract."""
        result = self.run_validate(make_event())
        self.assertEqual(result, {"status": "PASS"})

    def test_fail_result_should_match_contract(self):
        """FAIL output should include failure_reasons as a list."""
        result = self.run_validate(make_event(summary="See above for details"))
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("failure_reasons", result)
        self.assertIsInstance(result["failure_reasons"], list)


if __name__ == "__main__":
    unittest.main()
