#!/usr/bin/env python3
"""
A fixer script which crawls text files and replaces Unicode Ligatures with
non-ligature (mostly ASCII) two-character representations.

This intentionally limits itself to ligatures which are no semantically different from
the non-ligature representations (e.g. 'ff' vs 'U+FB00'). The reason being that
the fixers is intended to fix text which has been ligature-ized for
presentation (e.g. by LaTeX) but was originally input as ASCII-friendly latin
text.
"""
import re
import sys

from ._common import all_filenames, codepoint2char, parse_cli_args
from ._recorders import DiffRecorder

# map unicode codepoints to non-ligature versions of those chars
CODEPOINT_MAP = {
    "FB00": "ff",
    "FB01": "fi",
    "FB02": "fl",
    "FB03": "ffi",
    "FB04": "ffl",
}
CHAR_MAP = {  # remap in terms of chars
    codepoint2char(k): v for k, v in CODEPOINT_MAP.items()
}
REPLACEMENT_PATTERN = re.compile("(" + "|".join(CHAR_MAP.keys()) + ")")


def _re_subfunc(match):
    x = match.group(0)
    return CHAR_MAP.get(x, x)


def charwidth(c: str) -> int:
    return len(CHAR_MAP.get(c, c))


def replace_ligatures_str(s: str) -> str:
    return REPLACEMENT_PATTERN.sub(_re_subfunc, s)


def do_all_replacements(files, verbosity) -> DiffRecorder:
    """Do replacements over a set of filenames, and return a list of filenames
    where changes were made."""
    recorder = DiffRecorder(verbosity)

    for fn in all_filenames(files):
        recorder.run_line_fixer(replace_ligatures_str, fn)
    return recorder


def parse_args(argv):
    return parse_cli_args(__doc__, argv=argv, fixer=True)


def main(*, argv=None) -> int:
    args = parse_args(argv)
    changes = do_all_replacements(all_filenames(args.files), args.verbosity)
    if changes:
        changes.print_changes(args.show_changes, args.color, charwidth=charwidth)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
