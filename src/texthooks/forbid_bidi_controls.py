#!/usr/bin/env python3
"""
A checker script which crawls text files looking for Unicode Bidirectional control
characters (BiDi characters).

This checker only examines the BiDi controls, no other format control characters or
other sources
"""
import sys

from ._common import all_filenames, codepoint2char, parse_cli_args
from ._recorders import CheckRecorder

# see: http://www.unicode.org/reports/tr9/#Directional_Formatting_Characters
BIDI_CONTROL_CHARS = {
    codepoint2char("202A"),  # LRE
    codepoint2char("202B"),  # RLE
    codepoint2char("202C"),  # PDF
    codepoint2char("202D"),  # LRO
    codepoint2char("202E"),  # RLO
    codepoint2char("2066"),  # LRI
    codepoint2char("2067"),  # RLI
    codepoint2char("2068"),  # FSI
    codepoint2char("2069"),  # PDI
    codepoint2char("200E"),  # LRM
    codepoint2char("200F"),  # RLM
    codepoint2char("061C"),  # ALM
}


def check_bidi_str(line: str) -> bool:
    for c in line:
        if c in BIDI_CONTROL_CHARS:
            return False
    return True


def do_all_checks(files, verbosity) -> CheckRecorder:
    recorder = CheckRecorder(verbosity)

    for fn in all_filenames(files):
        recorder.run_line_checker(check_bidi_str, fn)
    return recorder


def parse_args(argv):
    return parse_cli_args(__doc__, fixer=False, argv=argv)


def main(*, argv=None) -> int:
    args = parse_args(argv)
    findings = do_all_checks(all_filenames(args.files), args.verbosity)
    if findings:
        findings.print_failures("forbid-bidi-controls", args.color)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
