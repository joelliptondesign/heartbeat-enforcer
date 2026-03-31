"""Command-line interface for heartbeat-enforcer."""

import sys
import json
import argparse
from . import baseline, validate


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Heartbeat Enforcer - Autonomous system change validation"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # baseline command
    baseline_parser = subparsers.add_parser(
        "baseline",
        help="Get baseline line count for a heartbeat file"
    )
    baseline_parser.add_argument(
        "heartbeat",
        help="Path to heartbeat file"
    )
    
    # validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a heartbeat record"
    )
    validate_parser.add_argument(
        "--heartbeat",
        required=True,
        help="Path to heartbeat file"
    )
    validate_parser.add_argument(
        "--baseline",
        type=int,
        help="Baseline line count for baseline mode validation"
    )
    validate_parser.add_argument(
        "--changed-files",
        help="Path to changed_files.txt for coverage validation"
    )
    
    args = parser.parse_args()
    
    if args.command == "baseline":
        count = baseline.get_line_count(args.heartbeat)
        print(count)
        sys.exit(0)
    
    elif args.command == "validate":
        result = validate.validate(
            args.heartbeat,
            baseline_count=args.baseline,
            changed_files_path=args.changed_files,
        )
        print(json.dumps(result))
        sys.exit(0 if result["status"] == "PASS" else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
