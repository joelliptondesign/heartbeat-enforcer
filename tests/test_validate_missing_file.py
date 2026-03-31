"""Tests for validate.py with missing file."""

import unittest
import os
from heartbeat_enforcer.validate import validate


class TestValidateMissingFile(unittest.TestCase):
    """Test cases for missing file validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.examples_dir = os.path.join(
            os.path.dirname(__file__), "..", "examples"
        )
    
    def test_missing_file_coverage_should_fail(self):
        """Heartbeat missing a file from changed_files.txt should FAIL."""
        result = validate(
            os.path.join(self.examples_dir, "invalid_missing_file.jsonl"),
            changed_files_path=os.path.join(self.examples_dir, "changed_files.txt"),
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("failure_reasons", result)
        self.assertTrue(len(result["failure_reasons"]) > 0)
        # Should have coverage mismatch error
        coverage_errors = [
            reason for reason in result["failure_reasons"]
            if "file coverage" in reason.lower() or "external context" in reason.lower()
        ]
        self.assertTrue(len(coverage_errors) > 0)


if __name__ == "__main__":
    unittest.main()
