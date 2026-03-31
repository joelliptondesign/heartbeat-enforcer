"""Tests for validate.py with bad shape."""

import unittest
import os
from heartbeat_enforcer.validate import validate


class TestValidateBadShape(unittest.TestCase):
    """Test cases for bad shape validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.examples_dir = os.path.join(
            os.path.dirname(__file__), "..", "examples"
        )
    
    def test_bad_shape_should_fail(self):
        """Heartbeat with missing required fields should FAIL."""
        result = validate(
            os.path.join(self.examples_dir, "invalid_bad_shape.jsonl"),
            changed_files_path=os.path.join(self.examples_dir, "changed_files.txt"),
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("failure_reasons", result)
        self.assertTrue(len(result["failure_reasons"]) > 0)
        # Should have schema validation errors
        schema_errors = [
            reason for reason in result["failure_reasons"]
            if any(term in reason.lower() for term in ["missing", "required", "reason"])
        ]
        self.assertTrue(len(schema_errors) > 0)


if __name__ == "__main__":
    unittest.main()
