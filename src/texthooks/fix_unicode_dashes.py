#!/usr/bin/env python3
"""
A fixer script which crawls text files and replaces Unicode dash characters
with ASCII equivalents.

This normalizes various dash, and minus signs to single hyphens, and
treats several longer dashes like the em dash as double-hyphens.

A variety of language-specific hyphen-like marks, like the Japanese long sound
mark (U+30FC), are ignored.

In files with the offending characters, they are replaced and the run is
marked as failed. This makes the script suitable as a pre-commit fixer.
"""
import re
import sys

from ._common import all_filenames, codepoints2chars, parse_cli_args
from ._recorders import DiffRecorder


def codepoints2regex(codepoints):
    return re.compile("(" + "|".join(codepoints2chars(codepoints)) + ")")


# Unicode codepoints for dash characters, commented with their unicode names
DEFAULT_SINGLE_HYPHEN_CODEPOINTS = (
    # hyphens
    "2010",  # Hyphen
    "2011",  # Non-Breaking Hyphen
    "FE63",  # Small Hyphen-Minus
    # standalone punctuation
    "2012",  # Figure Dash
    "2013",  # En Dash
    # minus signs
    "2212",  # Minus Sign
    "02D7",  # Modifier Letter Minus Sign
    "2796",  # Heavy Minus Sign
)

# Unicode codepoints for long-dash characters, commented with their unicode names
DEFAULT_DOUBLE_HYPHEN_CODEPOINTS = (
    # wide hyphens
    "FF0D",  # Fullwidth Hyphen-Minus
    # standalone long-dash punctuation
    "2014",  # Em Dash
    "FE58",  # Small Em Dash
)


def gen_line_fixer(single_hyphen_codepoints, double_hyphen_codepoints):
    single_hyphen_regex = (
        codepoints2regex(single_hyphen_codepoints) if single_hyphen_codepoints else None
    )
    double_hyphen_regex = (
        codepoints2regex(double_hyphen_codepoints) if double_hyphen_codepoints else None
    )

    if single_hyphen_regex and double_hyphen_regex:

        def line_fixer(line):
            return single_hyphen_regex.sub("-", double_hyphen_regex.sub("--", line))

    elif single_hyphen_regex:

        def line_fixer(line):
            return single_hyphen_regex.sub("-", line)

    elif double_hyphen_regex:

        def line_fixer(line):
            return double_hyphen_regex.sub("--", line)

    else:
        raise NotImplementedError("Both replacement modes were disabled.")

    return line_fixer


def do_all_replacements(
    files, single_hyphen_codepoints, double_hyphen_codepoints, verbosity
) -> DiffRecorder:
    """Do replacements over a set of filenames, and return a list of filenames
    where changes were made."""
    recorder = DiffRecorder(verbosity)
    line_fixer = gen_line_fixer(single_hyphen_codepoints, double_hyphen_codepoints)
    for fn in all_filenames(files):
        recorder.run_line_fixer(line_fixer, fn)
    return recorder


def modify_cli_parser(parser):
    parser.add_argument(
        "--single-hyphen-codepoints",
        type=str,
        help=(
            "A comma-delimited list of unicode codepoints for characters "
            "which should be replaced with single hyphens. "
            f"default: {','.join(DEFAULT_SINGLE_HYPHEN_CODEPOINTS)}"
        ),
    )
    parser.add_argument(
        "--double-hyphen-codepoints",
        type=str,
        help=(
            "A comma-delimited list of unicode codepoints for characters "
            "which should be replaced with double hyphens. "
            f"default: {','.join(DEFAULT_DOUBLE_HYPHEN_CODEPOINTS)}"
        ),
    )


def postprocess_cli_args(args):
    # convert comma delimited lists manually

    if args.single_hyphen_codepoints is None:
        args.single_hyphen_codepoints = DEFAULT_SINGLE_HYPHEN_CODEPOINTS
    elif args.single_hyphen_codepoints == "":
        args.single_hyphen_codepoints = []
    else:
        args.single_hyphen_codepoints = args.hyphen_codepoints.split(",")

    if args.double_hyphen_codepoints is None:
        args.double_hyphen_codepoints = DEFAULT_DOUBLE_HYPHEN_CODEPOINTS
    elif args.double_hyphen_codepoints == "":
        args.double_hyphen_codepoints = []
    else:
        args.double_hyphen_codepoints = args.double_hyphen_codepoints.split(",")

    if not (bool(args.single_hyphen_codepoints) or bool(args.double_hyphen_codepoints)):
        print(
            "fix-unicode-dashes cannot run when both sets of codepoints are empty.",
            file=sys.stderr,
        )
        raise SystemExit(2)

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

    changes = do_all_replacements(
        all_filenames(args.files),
        args.single_hyphen_codepoints,
        args.double_hyphen_codepoints,
        args.verbosity,
    )
    if changes:
        changes.print_changes(args.show_changes, args.color)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
