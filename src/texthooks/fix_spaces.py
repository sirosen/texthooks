#!/usr/bin/env python3
"""
A fixer script which crawls text files and replaces various unicode space
separators with the space character.

This normalizes No-Break Space and similar characters to ensure that your files
render the same way in all contexts. It does not modify newlines, carriage returns, or
other whitespace characters outside of the Space Separator category.

Of the various space separators, only U1680 (Ogham Space Mark) is typically represented
in a visually distinct way, and is therefore ignored.

In files with the offending characters, they are replaced and the run is marked as
failed. This makes the script suitable as a pre-commit fixer.
"""
import re
import sys

from ._common import all_filenames, codepoints2chars, parse_cli_args
from ._recorders import DiffRecorder


def codepoints2regex(codepoints):
    return re.compile("(" + "|".join(codepoints2chars(codepoints)) + ")")


# lists of unicode codepoints, commented with their unicode names
DEFAULT_SEPARATOR_CODEPOINTS = (
    # non-breaking
    "00A0",  # No-Break Space
    "202F",  # Narrow No-Break Space
    # various sized spaces
    "2000",  # En Quad
    "2001",  # Em Quad
    "2002",  # En Space
    "2003",  # Em Space
    "2004",  # Three-Per-Em Space
    "2005",  # Four-Per-Em Space
    "2006",  # Six-Per-Em Space
    "2007",  # Figure Space
    "2008",  # Punctuation Space
    "2009",  # Thin Space
    "200A",  # Hair Space
    # other...
    "205F",  # Medium Mathematical Space
    "3000",  # Ideographic Space
)


def gen_line_fixer(separator_regex):
    def line_fixer(line):
        return separator_regex.sub(" ", line)

    return line_fixer


def do_all_replacements(files, separator_regex, verbosity) -> DiffRecorder:
    """Do replacements over a set of filenames, and return a list of filenames
    where changes were made."""
    recorder = DiffRecorder(verbosity)
    line_fixer = gen_line_fixer(separator_regex)
    for fn in all_filenames(files):
        recorder.run_line_fixer(line_fixer, fn)
    return recorder


def modify_cli_parser(parser):
    parser.add_argument(
        "--separator-codepoints",
        type=str,
        help=(
            "A comma-delimited list of unicode codepoints for characters "
            "which should be treated as single quotes. "
            f"default: {','.join(DEFAULT_SEPARATOR_CODEPOINTS)}"
        ),
    )


def postprocess_cli_args(args):
    # convert comma delimited lists manually
    if args.separator_codepoints:
        args.separator_codepoints = args.separator_codepoints.split(",")
    else:
        args.separator_codepoints = DEFAULT_SEPARATOR_CODEPOINTS
    return args


def parse_args(argv):
    return parse_cli_args(
        __doc__,
        fixer=True,
        argv=argv,
        modify_parser=modify_cli_parser,
        postprocess=postprocess_cli_args,
    )


def main(*, argv=None):
    args = parse_args(argv)

    separator_regex = codepoints2regex(args.separator_codepoints)

    changes = do_all_replacements(
        all_filenames(args.files), separator_regex, verbosity=args.verbosity
    )
    if changes:
        changes.print_changes(args.show_changes, args.color)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
