#!/usr/bin/env python3
"""
A fixer script which crawls text files and replaces Unicode arrow characters
with ASCII equivalents.

This converts arrows which have unambiguous ASCII representations, such as the
rightwards arrow (U+2192) to ``->`` and the leftwards double arrow (U+21D0) to
``<=``.

Vertical and diagonal arrows (e.g. the upwards arrow, U+2191) are intentionally
ignored, as they have no unambiguous ASCII form.
"""

import re
import sys
import typing as t

from ._common import all_filenames, codepoint2char, parse_cli_args
from ._recorders import DiffRecorder

# map unicode codepoints to ASCII versions of those arrows
CODEPOINT_MAP = {
    # single-line arrows
    "2190": "<-",  # Leftwards Arrow
    "2192": "->",  # Rightwards Arrow
    "2194": "<->",  # Left Right Arrow
    "21A6": "|->",  # Rightwards Arrow From Bar
    # double-line arrows
    "21D0": "<=",  # Leftwards Double Arrow
    "21D2": "=>",  # Rightwards Double Arrow
    "21D4": "<=>",  # Left Right Double Arrow
    # long arrows
    "27F5": "<--",  # Long Leftwards Arrow
    "27F6": "-->",  # Long Rightwards Arrow
    "27F7": "<-->",  # Long Left Right Arrow
    "27F8": "<==",  # Long Leftwards Double Arrow
    "27F9": "==>",  # Long Rightwards Double Arrow
    "27FA": "<==>",  # Long Left Right Double Arrow
}
CHAR_MAP = {  # remap in terms of chars
    codepoint2char(k): v for k, v in CODEPOINT_MAP.items()
}
REPLACEMENT_PATTERN = re.compile("(" + "|".join(CHAR_MAP.keys()) + ")")


def _re_subfunc(match: re.Match) -> str:
    x = match.group(0)
    return CHAR_MAP.get(x, x)


def charwidth(c: str) -> int:
    return len(CHAR_MAP.get(c, c))


def replace_arrows_str(s: str) -> str:
    return REPLACEMENT_PATTERN.sub(_re_subfunc, s)


def do_all_replacements(
    files: t.Iterable[str] | None, verbosity: int, check: bool
) -> DiffRecorder:
    """Do replacements over a set of filenames, and return a list of filenames
    where changes were made."""
    recorder = DiffRecorder(verbosity, check=check)

    for fn in all_filenames(files):
        recorder.run_line_fixer(replace_arrows_str, fn)
    return recorder


def parse_args(argv: list[str] | None) -> t.Any:
    return parse_cli_args(__doc__, argv=argv, fixer=True)


def main(*, argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    changes = do_all_replacements(
        all_filenames(args.files), args.verbosity, check=args.check
    )
    if changes:
        changes.print_changes(args.show_changes, args.color, charwidth=charwidth)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
