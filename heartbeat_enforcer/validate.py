"""Heartbeat validation logic."""

import json
from pathlib import Path


# Phrases that indicate external context references
BANNED_PHRASES = [
    "as discussed",
    "see above",
    "per earlier",
    "previous chat",
    "prior context",
    "as instructed earlier",
    "from the brief above",
    "based on earlier discussion",
]


def contains_banned_phrase(text):
    """
    Check if text contains any banned phrases (case-insensitive).
    
    Args:
        text: Text to check.
        
    Returns:
        True if text contains a banned phrase, False otherwise.
    """
    text_lower = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase.lower() in text_lower:
            return True
    return False


def parse_jsonl(file_path):
    """
    Parse a JSONL file.
    
    Args:
        file_path: Path to JSONL file.
        
    Returns:
        Tuple of (list of parsed records, list of error messages).
    """
    records = []
    errors = []
    
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    errors.append(f"Invalid JSON on line {line_num}: {str(e)}")
    except FileNotFoundError:
        errors.append(f"Heartbeat file not found: {file_path}")
    except IOError as e:
        errors.append(f"Error reading heartbeat file: {str(e)}")
    
    return records, errors


def read_changed_files(file_path):
    """
    Read changed files list.
    
    Args:
        file_path: Path to changed_files.txt.
        
    Returns:
        Tuple of (set of file paths, list of error messages).
    """
    files = set()
    errors = []
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    files.add(line)
    except FileNotFoundError:
        errors.append(f"Changed files list not found: {file_path}")
    except IOError as e:
        errors.append(f"Error reading changed files: {str(e)}")
    
    return files, errors


def validate_event(event):
    """
    Validate a single heartbeat event.
    
    Args:
        event: Event record to validate.
        
    Returns:
        List of validation error messages.
    """
    errors = []
    
    # Check timestamp exists
    if "timestamp" not in event:
        errors.append("Event missing required field: timestamp")
    
    # Check event_type
    if event.get("event_type") != "change_ops":
        errors.append(f"Invalid event_type: expected 'change_ops', got '{event.get('event_type')}'")
    
    # Check actor
    actor = event.get("actor")
    if not isinstance(actor, str) or not actor:
        errors.append("Actor must be a non-empty string")
    
    # Check payload exists
    if "payload" not in event:
        errors.append("Event missing required field: payload")
        return errors
    
    payload = event["payload"]
    
    # Check summary exists
    if "summary" not in payload:
        errors.append("Payload missing required field: summary")
    elif contains_banned_phrase(payload["summary"]):
        errors.append(f"Summary contains external context reference: {payload['summary']}")
    
    # Check operations
    if "operations" not in payload:
        errors.append("Payload missing required field: operations")
        return errors
    
    operations = payload["operations"]
    if not isinstance(operations, list) or len(operations) == 0:
        errors.append("Operations must be a non-empty list")
        return errors
    
    # Validate each operation
    for op_idx, operation in enumerate(operations):
        op_errors = validate_operation(operation, op_idx)
        errors.extend(op_errors)
    
    return errors


def validate_operation(operation, op_idx):
    """
    Validate a single operation within an event.
    
    Args:
        operation: Operation record to validate.
        op_idx: Index of operation in the operations list.
        
    Returns:
        List of validation error messages.
    """
    errors = []
    op_prefix = f"Operation {op_idx}"
    
    # Check mode
    if operation.get("mode") not in {"planned", "autonomous"}:
        errors.append(f"{op_prefix}: mode must be 'planned' or 'autonomous', got '{operation.get('mode')}'")
    
    # Check files
    if "files" not in operation:
        errors.append(f"{op_prefix}: missing required field: files")
    else:
        files = operation["files"]
        if not isinstance(files, list) or len(files) == 0:
            errors.append(f"{op_prefix}: files must be a non-empty list")
        else:
            for file_entry in files:
                if not isinstance(file_entry, str) or not file_entry:
                    errors.append(
                        f"{op_prefix}: each file must be a non-empty string"
                    )
                    break
            # Check for duplicates
            if len(files) != len(set(files)):
                errors.append(f"{op_prefix}: duplicate files detected in files list")
    
    # Check action
    action = operation.get("action")
    if not isinstance(action, str) or not action:
        errors.append(f"{op_prefix}: action must be a non-empty string")
    
    # Check reason
    reason = operation.get("reason")
    if not isinstance(reason, str) or not reason:
        errors.append(f"{op_prefix}: reason must be a non-empty string")
    elif contains_banned_phrase(reason):
        errors.append(f"{op_prefix}: reason contains external context reference: {reason}")
    
    return errors


def validate_coverage(event, expected_files):
    """
    Validate that operations cover exactly the expected files.
    
    Args:
        event: Heartbeat event.
        expected_files: Set of expected changed files.
        
    Returns:
        List of validation error messages.
    """
    errors = []
    
    # Collect all files from all operations
    actual_files = set()
    
    if "payload" in event and "operations" in event["payload"]:
        for operation in event["payload"]["operations"]:
            if "files" in operation and isinstance(operation["files"], list):
                for file in operation["files"]:
                    actual_files.add(file)
    
    if actual_files != expected_files:
        missing = expected_files - actual_files
        extra = actual_files - expected_files
        
        if missing:
            errors.append(f"File coverage mismatch - missing from operations: {sorted(missing)}")
        if extra:
            errors.append(f"File coverage mismatch - extra in operations: {sorted(extra)}")
    
    return errors


def validate(
    heartbeat_path,
    baseline_count=None,
    changed_files_path=None,
):
    """
    Validate a heartbeat record.
    
    Args:
        heartbeat_path: Path to heartbeat JSONL file.
        baseline_count: Baseline line count (optional). If provided, validates baseline mode.
        changed_files_path: Path to changed_files.txt (optional, required for coverage checks).
        
    Returns:
        Dict with "status" and optional "failure_reasons".
    """
    errors = []
    
    # Check if heartbeat file exists
    if not Path(heartbeat_path).exists():
        return {
            "status": "FAIL",
            "failure_reasons": [f"Heartbeat file not found: {heartbeat_path}"],
        }
    
    # Parse JSONL
    records, parse_errors = parse_jsonl(heartbeat_path)
    errors.extend(parse_errors)
    
    if not records:
        if errors:
            return {"status": "FAIL", "failure_reasons": errors}
        else:
            return {"status": "FAIL", "failure_reasons": ["Heartbeat file is empty"]}
    
    # Baseline mode validation
    if baseline_count is not None:
        current_count = len(records)
        if current_count != baseline_count + 1:
            return {
                "status": "FAIL",
                "failure_reasons": [
                    f"Baseline mode: expected {baseline_count + 1} total lines, "
                    f"got {current_count}. Expected exactly one new line appended."
                ],
            }
        # Validate only the last (new) event
        event_to_validate = records[-1]
    else:
        # Tail mode: validate only the last event
        event_to_validate = records[-1]
    
    # Validate the event
    event_errors = validate_event(event_to_validate)
    errors.extend(event_errors)
    
    # Coverage validation if changed_files_path is provided
    if changed_files_path:
        changed_files, file_read_errors = read_changed_files(changed_files_path)
        errors.extend(file_read_errors)
        
        if not file_read_errors:  # Only check coverage if file was read successfully
            coverage_errors = validate_coverage(event_to_validate, changed_files)
            errors.extend(coverage_errors)
    
    # Return result
    if errors:
        return {"status": "FAIL", "failure_reasons": errors}
    else:
        return {"status": "PASS"}
