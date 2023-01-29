#!/usr/bin/env python3
"""
A fixer script which crawls text files and replaces smartquotes with
normal quote characters.

This fixes copy-paste from some applications which replace double-quotes with curly
quotes.

For extra credit, it handles alternate encodings of quotation marks and
dingbats.

It does *not* convert corner brackets, braile quotation marks, or angle
quotation marks. Those characters are not typically the result of copy-paste
errors, so they are allowed.

Low quotation marks vary in usage and meaning by language, and some languages
use quotation marks which are facing "outwards" (opposite facing from english).
For the most part, these and exotic characters (double-prime quotes) are
ignored.

In files with the offending marks, they are replaced and the run is marked as
failed. This makes the script suitable as a pre-commit fixer.
"""
import re
import sys

from ._common import all_filenames, codepoints2chars, parse_cli_args
from ._recorders import DiffRecorder


def codepoints2regex(codepoints):
    return re.compile("(" + "|".join(codepoints2chars(codepoints)) + ")")


# lists of unicode codepoints, commented with their unicode names
DEFAULT_DOUBLE_QUOTE_CODEPOINTS = (
    # STRAIGHT DOUBLE QUOTES
    "0022",  # Quotation mark
    "FF02",  # Fullwidth quotation mark
    # LEFT DOUBLE QUOTES
    "201C",  # Left double quotation mark
    "201F",  # Double high-reversed-9 quotation mark
    "275D",  # Heavy double turned comma quotation mark ornament
    "1F676",  # Sans-serif heavy double turned comma quotation mark ornament
    # RIGHT DOUBLE QUOTES
    "201D",  # Right double quotation mark
    "275E",  # Heavy double comma quotation mark ornament
    "1F677",  # Sans-serif heavy double comma quotation mark ornament
)
DEFAULT_SINGLE_QUOTE_CODEPOINTS = (
    # STRAIGHT SINGLE QUOTES
    "0027",  # Apostrophe
    "FF07",  # Fullwidth apostrophe
    # LEFT SINGLE QUOTES
    "2018",  # Left single quotation mark
    "201B",  # Single high-reversed-9 quotation mark
    "275B",  # Heavy single turned comma quotation mark ornament
    # RIGHT SINGLE QUOTES
    "2019",  # Right single quotation mark
    "275C",  # Heavy single comma quotation mark ornament
)


def gen_line_fixer(single_quote_regex, double_quote_regex):
    def line_fixer(line):
        return single_quote_regex.sub("'", double_quote_regex.sub('"', line))

    return line_fixer


def do_all_replacements(
    files, single_quote_regex, double_quote_regex, verbosity
) -> DiffRecorder:
    """Do replacements over a set of filenames, and return a list of filenames
    where changes were made."""
    recorder = DiffRecorder(verbosity)
    line_fixer = gen_line_fixer(single_quote_regex, double_quote_regex)
    for fn in all_filenames(files):
        recorder.run_line_fixer(line_fixer, fn)
    return recorder


def modify_cli_parser(parser):
    parser.add_argument(
        "--double-quote-codepoints",
        type=str,
        help=(
            "A comma-delimited list of unicode codepoints for characters "
            "which should be treated as double quotes. "
            f"default: {','.join(DEFAULT_DOUBLE_QUOTE_CODEPOINTS)}"
        ),
    )
    parser.add_argument(
        "--single-quote-codepoints",
        type=str,
        help=(
            "A comma-delimited list of unicode codepoints for characters "
            "which should be treated as single quotes. "
            f"default: {','.join(DEFAULT_SINGLE_QUOTE_CODEPOINTS)}"
        ),
    )


def postprocess_cli_args(args):
    # convert comma delimited lists manually
    if args.double_quote_codepoints:
        args.double_quote_codepoints = args.double_quote_codepoints.split(",")
    else:
        args.double_quote_codepoints = DEFAULT_DOUBLE_QUOTE_CODEPOINTS
    if args.single_quote_codepoints:
        args.single_quote_codepoints = args.single_quote_codepoints.split(",")
    else:
        args.single_quote_codepoints = DEFAULT_SINGLE_QUOTE_CODEPOINTS
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

    double_quote_regex = codepoints2regex(args.double_quote_codepoints)
    single_quote_regex = codepoints2regex(args.single_quote_codepoints)

    changes = do_all_replacements(
        all_filenames(args.files),
        single_quote_regex,
        double_quote_regex,
        args.verbosity,
    )
    if changes:
        changes.print_changes(args.show_changes, args.color)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
