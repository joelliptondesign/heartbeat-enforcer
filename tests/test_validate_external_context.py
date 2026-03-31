"""Tests for validate.py with external context."""

import unittest
import os
from heartbeat_enforcer.validate import validate


class TestValidateExternalContext(unittest.TestCase):
    """Test cases for external context validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.examples_dir = os.path.join(
            os.path.dirname(__file__), "..", "examples"
        )
    
    def test_external_context_should_fail(self):
        """Heartbeat with banned phrases should FAIL."""
        result = validate(
            os.path.join(self.examples_dir, "invalid_external_context.jsonl"),
            changed_files_path=os.path.join(self.examples_dir, "changed_files.txt"),
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("failure_reasons", result)
        self.assertTrue(len(result["failure_reasons"]) > 0)
        # Should have external context error
        context_errors = [
            reason for reason in result["failure_reasons"]
            if "external context" in reason.lower()
        ]
        self.assertTrue(len(context_errors) > 0)


if __name__ == "__main__":
    unittest.main()
