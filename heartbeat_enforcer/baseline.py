"""Baseline functionality for establishing initial state."""


def get_line_count(file_path):
    """
    Count the number of lines in a file.
    
    Args:
        file_path: Path to the file to count lines in.
        
    Returns:
        Number of lines in the file, or 0 if file does not exist.
    """
    try:
        with open(file_path, 'r') as f:
            return sum(1 for _ in f)
    except (FileNotFoundError, IOError):
        return 0
