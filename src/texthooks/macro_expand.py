"""
Modify text files in-place with expansions of "macros"
Each macro is supplied as a pair, a prefix and a format string.

The 'prefix' will be found and replaced anywhere in the file. The string immediately
following the prefix, limited to word characters, will be replaced using the format
string. The format string supports `$VALUE` to represent the replaced text.

For example, if you want a macro of the form

   issue:num  (github issue link)

in markdown, then specify

   --macro 'issue:' '[texthooks#$VALUE](https://github.com/sirosen/texthooks/issues/$VALUE)'
"""  # noqa: E501
import re

from ._common import all_filenames, parse_cli_args
from ._recorders import DiffRecorder


def macroexpand(content, prefix, fmt):
    match_pattern = r"(^|\W)(" + re.escape(prefix) + r")(\w+)(\W|$)"
    replace_pattern = r"\1" + fmt.replace("$VALUE", r"\3") + r"\4"
    return re.sub(match_pattern, replace_pattern, content)


def gen_line_fixer(macro_list):
    def line_fixer(line):
        if macro_list is None:
            return line

        for macro in macro_list:
            line = macroexpand(line, macro[0], macro[1])
        return line

    return line_fixer


def do_all_replacements(files, macro_list, verbosity) -> DiffRecorder:
    """Do replacements over a set of filenames, and return a list of filenames
    where changes were made."""
    recorder = DiffRecorder(verbosity)
    line_fixer = gen_line_fixer(macro_list)
    for fn in all_filenames(files):
        recorder.run_line_fixer(line_fixer, fn)
    return recorder


def modify_cli_parser(parser):
    parser.add_argument(
        "--macro", nargs=2, action="append", metavar=("PREFIX", "FORMAT")
    )


def parse_args(argv):
    return parse_cli_args(
        __doc__,
        fixer=True,
        modify_parser=modify_cli_parser,
        argv=argv,
    )


def main(*, argv=None):
    args = parse_args(argv)
    changes = do_all_replacements(all_filenames(args.files), args.macro, args.verbosity)
    if changes:
        changes.print_changes(args.show_changes, args.color)
        return 1
    return 0


if __name__ == "__main__":
    main()
