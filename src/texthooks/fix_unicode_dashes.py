#!/usr/bin/env python3
"""
A fixer script which crawls text files and replaces Unicode dash characters
with ASCII equivalents.

This fixes copy-paste from some applications which replace hyphens with
Unicode dash characters like en-dash (–), em-dash (—), minus sign (−),
and fullwidth hyphen (－).

The following Unicode characters are replaced:
- U+2013 EN DASH (–) → ASCII hyphen (-)
- U+2014 EM DASH (—) → ASCII double hyphen (--)
- U+2212 MINUS SIGN (−) → ASCII hyphen (-)
- U+FF0D FULLWIDTH HYPHEN-MINUS (－) → ASCII hyphen (-)

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
DEFAULT_HYPHEN_CODEPOINTS = (
    "2013",  # EN DASH (–)
    "2212",  # MINUS SIGN (−)
    "FF0D",  # FULLWIDTH HYPHEN-MINUS (－)
)

# Unicode codepoints for dash characters that should be replaced with
# ASCII double hyphens
DEFAULT_EMDASH_CODEPOINTS = ("2014",)  # EM DASH (—)


def gen_line_fixer(hyphen_regex, emdash_regex):
    def line_fixer(line):
        # Replace em-dashes first, then hyphens
        line = emdash_regex.sub("--", line)
        line = hyphen_regex.sub("-", line)
        return line

    return line_fixer


def do_all_replacements(files, hyphen_regex, emdash_regex, verbosity) -> DiffRecorder:
    """Do replacements over a set of filenames, and return a list of filenames
    where changes were made."""
    recorder = DiffRecorder(verbosity)
    line_fixer = gen_line_fixer(hyphen_regex, emdash_regex)
    for fn in all_filenames(files):
        recorder.run_line_fixer(line_fixer, fn)
    return recorder


def modify_cli_parser(parser):
    parser.add_argument(
        "--hyphen-codepoints",
        type=str,
        help=(
            "A comma-delimited list of unicode codepoints for characters "
            "which should be treated as hyphens and replaced with single hyphens. "
            f"default: {','.join(DEFAULT_HYPHEN_CODEPOINTS)}"
        ),
    )
    parser.add_argument(
        "--emdash-codepoints",
        type=str,
        help=(
            "A comma-delimited list of unicode codepoints for characters "
            "which should be treated as em-dashes and replaced with double hyphens. "
            f"default: {','.join(DEFAULT_EMDASH_CODEPOINTS)}"
        ),
    )


def postprocess_cli_args(args):
    # convert comma delimited lists manually
    if args.hyphen_codepoints:
        args.hyphen_codepoints = args.hyphen_codepoints.split(",")
    else:
        args.hyphen_codepoints = DEFAULT_HYPHEN_CODEPOINTS
    if args.emdash_codepoints:
        args.emdash_codepoints = args.emdash_codepoints.split(",")
    else:
        args.emdash_codepoints = DEFAULT_EMDASH_CODEPOINTS
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

    hyphen_regex = codepoints2regex(args.hyphen_codepoints)
    emdash_regex = codepoints2regex(args.emdash_codepoints)

    changes = do_all_replacements(
        all_filenames(args.files),
        hyphen_regex,
        emdash_regex,
        args.verbosity,
    )
    if changes:
        changes.print_changes(args.show_changes, args.color)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
