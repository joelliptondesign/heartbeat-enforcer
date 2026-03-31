"""Tests for invalid JSON heartbeat input."""

import os
import tempfile
import unittest

from heartbeat_enforcer.validate import validate


class TestValidateInvalidJson(unittest.TestCase):
    """Test invalid JSON handling."""

    def test_invalid_json_should_fail(self):
        """Malformed JSON should FAIL validation."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".jsonl"
        ) as heartbeat_file:
            heartbeat_file.write("{ invalid json\n")
            heartbeat_path = heartbeat_file.name

        try:
            result = validate(heartbeat_path)
            self.assertEqual(result["status"], "FAIL")
            self.assertIn("failure_reasons", result)
            self.assertTrue(
                any("invalid json" in reason.lower() for reason in result["failure_reasons"])
            )
        finally:
            os.unlink(heartbeat_path)


if __name__ == "__main__":
    unittest.main()
