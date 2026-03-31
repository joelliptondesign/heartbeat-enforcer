"""Tests for baseline.py."""

import unittest
import tempfile
import os
from heartbeat_enforcer.baseline import get_line_count


class TestBaseline(unittest.TestCase):
    """Test cases for baseline line counting."""
    
    def test_get_line_count_empty_file(self):
        """Empty file should return 0."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            count = get_line_count(temp_path)
            self.assertEqual(count, 0)
        finally:
            os.unlink(temp_path)
    
    def test_get_line_count_single_line(self):
        """File with single line should return 1."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("line 1\n")
            temp_path = f.name
        
        try:
            count = get_line_count(temp_path)
            self.assertEqual(count, 1)
        finally:
            os.unlink(temp_path)
    
    def test_get_line_count_multiple_lines(self):
        """File with multiple lines should return correct count."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("line 1\n")
            f.write("line 2\n")
            f.write("line 3\n")
            temp_path = f.name
        
        try:
            count = get_line_count(temp_path)
            self.assertEqual(count, 3)
        finally:
            os.unlink(temp_path)
    
    def test_get_line_count_nonexistent_file(self):
        """Nonexistent file should return 0."""
        count = get_line_count("/nonexistent/file/path/that/should/not/exist.txt")
        self.assertEqual(count, 0)
    
    def test_baseline_mode_expectation(self):
        """Test baseline +1 expectation."""
        # Create file with 5 lines
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.jsonl') as f:
            for i in range(5):
                f.write('{"line": %d}\n' % i)
            temp_path = f.name
        
        try:
            baseline_count = get_line_count(temp_path)
            self.assertEqual(baseline_count, 5)
            
            # Simulate adding one line
            with open(temp_path, 'a') as f:
                f.write('{"line": 5}\n')
            
            new_count = get_line_count(temp_path)
            self.assertEqual(new_count, baseline_count + 1)
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
