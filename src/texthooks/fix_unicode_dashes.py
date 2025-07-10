#!/usr/bin/env python3
"""
A fixer script which crawls text files and replaces Unicode dash characters
with ASCII hyphens.

This fixes copy-paste from some applications which replace hyphens with
Unicode dash characters like en-dash (–), em-dash (—), minus sign (−),
and fullwidth hyphen (－).

The following Unicode characters are replaced with ASCII hyphens (-):
- U+2013 EN DASH (–)
- U+2014 EM DASH (—)
- U+2212 MINUS SIGN (−)
- U+FF0D FULLWIDTH HYPHEN-MINUS (－)

In files with the offending characters, they are replaced and the run is
marked as failed. This makes the script suitable as a pre-commit fixer.
"""
import re
import sys

from ._common import all_filenames, codepoints2chars, parse_cli_args
from ._recorders import DiffRecorder


def codepoints2regex(codepoints):
    return re.compile("(" + "|".join(codepoints2chars(codepoints)) + ")")


# Unicode codepoints for dash characters that should be replaced with ASCII hyphens
DEFAULT_DASH_CODEPOINTS = (
    "2013",  # EN DASH (–)
    "2014",  # EM DASH (—)
    "2212",  # MINUS SIGN (−)
    "FF0D",  # FULLWIDTH HYPHEN-MINUS (－)
)


def gen_line_fixer(dash_regex):
    def line_fixer(line):
        return dash_regex.sub("-", line)

    return line_fixer


def do_all_replacements(files, dash_regex, verbosity) -> DiffRecorder:
    """Do replacements over a set of filenames, and return a list of filenames
    where changes were made."""
    recorder = DiffRecorder(verbosity)
    line_fixer = gen_line_fixer(dash_regex)
    for fn in all_filenames(files):
        recorder.run_line_fixer(line_fixer, fn)
    return recorder


def modify_cli_parser(parser):
    parser.add_argument(
        "--dash-codepoints",
        type=str,
        help=(
            "A comma-delimited list of unicode codepoints for characters "
            "which should be treated as dashes and replaced with hyphens. "
            f"default: {','.join(DEFAULT_DASH_CODEPOINTS)}"
        ),
    )


def postprocess_cli_args(args):
    # convert comma delimited lists manually
    if args.dash_codepoints:
        args.dash_codepoints = args.dash_codepoints.split(",")
    else:
        args.dash_codepoints = DEFAULT_DASH_CODEPOINTS
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

    dash_regex = codepoints2regex(args.dash_codepoints)

    changes = do_all_replacements(
        all_filenames(args.files),
        dash_regex,
        args.verbosity,
    )
    if changes:
        changes.print_changes(args.show_changes, args.color)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main()) 