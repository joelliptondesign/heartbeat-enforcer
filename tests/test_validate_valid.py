"""Tests for validate.py with valid heartbeat."""

import unittest
import os
from heartbeat_enforcer.validate import validate


class TestValidateValid(unittest.TestCase):
    """Test cases for valid heartbeat validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.examples_dir = os.path.join(
            os.path.dirname(__file__), "..", "examples"
        )
    
    def test_valid_heartbeat_with_coverage(self):
        """Valid heartbeat with matching file coverage should PASS."""
        result = validate(
            os.path.join(self.examples_dir, "valid_heartbeat.jsonl"),
            changed_files_path=os.path.join(self.examples_dir, "changed_files.txt"),
        )
        self.assertEqual(result["status"], "PASS")
        self.assertNotIn("failure_reasons", result)


if __name__ == "__main__":
    unittest.main()
