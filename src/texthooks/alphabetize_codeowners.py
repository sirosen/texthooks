#!/usr/bin/env python
"""
Alphabetize the list of owners for each path in .github/CODEOWNERS

Ignores empty lines and comments, but normalizes whitespace on semantically significant
lines.

Use '--dialect=gitlab' in order to support GitLab's extended CODEOWNERS syntax.
"""

import re
import sys
import typing as t

from ._common import parse_cli_args
from ._recorders import DiffRecorder

GITLAB_SECTION_TITLE_PATTERN = re.compile(r"\^?\[[^\]]+\]")
GITLAB_SECTION_N_APPROVALS_PATTERN = re.compile(r"\[\d+\]")


def main(*, argv=None) -> int:
    args = parse_cli_args(
        __doc__,
        fixer=True,
        argv=argv,
        disable_args=["files"],
        modify_parser=_add_args,
    )
    filenames = args.files
    if not filenames:
        filenames = [".github/CODEOWNERS"]

    line_fixer = make_line_fixer(args.dialect)

    recorder = DiffRecorder(args.verbosity)
    missing_file = False
    for fn in filenames:
        try:
            recorder.run_line_fixer(line_fixer, fn)
        except FileNotFoundError:
            missing_file = True
    if recorder or missing_file:
        if recorder:
            recorder.print_changes(args.show_changes, args.color)
        return 1
    return 0


def _add_args(parser):
    parser.add_argument("files", nargs="*", help="default: .github/CODEOWNERS")
    parser.add_argument(
        "--dialect",
        default="standard",
        choices=(
            "standard",
            "gitlab",
        ),
        help=(
            "A dialect of codeowners parsing to use. "
            "Defaults to the common syntax ('standard')."
        ),
    )


def make_line_fixer(dialect: str) -> t.Callable[[str], str]:
    if dialect == "standard":
        return sort_line_standard
    elif dialect == "gitlab":
        return sort_line_gitlab
    else:
        raise NotImplementedError(f"Unrecognized dialect: {dialect}")


def sort_line_standard(line: str) -> str:
    # sort a line's list of owners; also normalizes whitespace
    if line.strip() == "" or line.strip().startswith("#"):
        return line
    return _sort_owners_line(line)


def sort_line_gitlab(line: str) -> str:
    if line.strip() == "" or line.strip().startswith("#"):
        return line

    title_match = GITLAB_SECTION_TITLE_PATTERN.match(line)
    if title_match:
        after_section = line[title_match.end() :]
        n_approvals_match = GITLAB_SECTION_N_APPROVALS_PATTERN.match(after_section)
        if n_approvals_match:
            cut_point = title_match.end() + n_approvals_match.end()
        else:
            cut_point = title_match.end()
        section = line[:cut_point]
        default_owners = line[cut_point:].split()
        if not default_owners:
            return line
        return " ".join([section] + sorted(default_owners, key=str.casefold))
    else:
        return _sort_owners_line(line)


def _sort_owners_line(line: str) -> str:
    data_part, comment_marker, comment_part = line.partition("#")
    path, *owners = data_part.split()
    if not owners:
        return line

    data_part = " ".join([path] + sorted(owners, key=str.casefold))
    if comment_marker:
        return f"{data_part}  #{comment_part}"
    return data_part


if __name__ == "__main__":
    sys.exit(main())
