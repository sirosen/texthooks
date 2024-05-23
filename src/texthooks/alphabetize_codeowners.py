#!/usr/bin/env python
"""
Alphabetize the list of owners for each path in .github/CODEOWNERS

Ignores empty lines and comments, but normalizes whitespace on semantically significant
lines
"""

import sys

from ._common import parse_cli_args
from ._recorders import DiffRecorder


def main(*, argv=None) -> int:
    args = parse_cli_args(
        __doc__,
        fixer=True,
        argv=argv,
        disable_args=["files"],
        modify_parser=_add_files_arg,
    )
    filenames = args.files
    if not filenames:
        filenames = [".github/CODEOWNERS"]

    recorder = DiffRecorder(args.verbosity)
    missing_file = False
    for fn in filenames:
        try:
            recorder.run_line_fixer(sort_line, fn)
        except FileNotFoundError:
            missing_file = True
    if recorder or missing_file:
        if recorder:
            recorder.print_changes(args.show_changes, args.color)
        return 1
    return 0


def _add_files_arg(parser):
    parser.add_argument("files", nargs="*", help="default: .github/CODEOWNERS")


def sort_line(line: str) -> str:
    if line.strip() == "" or line.strip().startswith("#"):
        return line
    # also normalizes whitespace
    path, *owners = line.split()
    if not owners:
        return line
    return " ".join([path] + sorted(owners, key=str.casefold))


if __name__ == "__main__":
    sys.exit(main())
