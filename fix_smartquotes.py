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
import argparse
import collections
import glob
import re
import sys

from identify import identify


def codepoints2chars(codepoints):
    return [chr(int(c, 16)) for c in codepoints]


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


class DiffRecorder:
    def __init__(self):
        # in py3.6+ the dict builtin maintains order, but being explicit is
        # slightly safer since we're being explicit about the fact that we want
        # to retain key order
        self.by_fname = collections.OrderedDict()

    def add(self, fname, original, updated, lineno):
        if fname not in self.by_fname:
            self.by_fname[fname] = []
        self.by_fname[fname].append((original, updated, lineno))

    def hasdiff(self, fname):
        return bool(self.by_fname.get(fname))

    def changed_filenames(self):
        return list(self.by_name.keys())

    def __bool__(self):
        return bool(self.by_fname)

    def items(self):
        return self.by_fname.items()


def all_filenames(files):
    if not files:
        for fn in glob.iglob("**/*", recursive=True):
            tags = identify.tags_from_path(fn)
            if "text" in tags:
                yield fn
    else:
        for fn in files:
            yield fn


def do_replacements(
    recorder: DiffRecorder, filename, single_quote_regex, double_quote_regex
):
    """Given a filename, replace content and write *if* changes were made

    Returns True if changes were made, False if none were made"""
    with open(filename, "r") as f:
        content = f.readlines()

    newcontent = []
    for lineno, line in enumerate(content, 1):
        updated = single_quote_regex.sub("'", double_quote_regex.sub('"', line))
        newcontent.append(updated)
        if updated != line:
            recorder.add(filename, line, updated, lineno)

    if recorder.hasdiff(filename):
        with open(filename, "w") as f:
            f.write("".join(newcontent))
        return True
    return False


def do_all_replacements(files, single_quote_regex, double_quote_regex) -> DiffRecorder:
    """Do replacements over a set of filenames, and return a list of filenames
    where changes were made."""
    recorder = DiffRecorder()
    for fn in all_filenames(files):
        do_replacements(recorder, fn, single_quote_regex, double_quote_regex)
    return recorder


def _gen_change_caret_line(original, updated):
    indices = []
    for idx, c in enumerate(original):
        if c != updated[idx]:
            indices.append(idx)
    gen = ""
    cur = 0
    for idx in indices:
        gen += " " * (idx - cur)
        gen += "^"
        cur = idx + 1
    return gen


def print_changes(args, recorder: DiffRecorder):
    print("Changes were made in these files:")
    for filename, changeset in recorder.items():
        print(f"  \033[0;33m{filename}\033[0m")
        if args.show_changes:
            for (original, updated, lineno) in changeset:
                original, updated = original.rstrip(), updated.rstrip()
                print(f"  line {lineno}:")
                print(f"  \033[0;91m-{original}\033[0m")
                print(f"  \033[0;92m+{updated}\033[0m")
                print(
                    f"  \033[1;96m {_gen_change_caret_line(original, updated)}\033[0m"
                )


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="default: all text files in current directory (recursive)",
    )
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
    parser.add_argument(
        "--show-changes",
        action="store_true",
        default=False,
        help="Show the lines which were changed",
    )

    args = parser.parse_args()

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


def main():
    args = parse_args()

    double_quote_regex = codepoints2regex(args.double_quote_codepoints)
    single_quote_regex = codepoints2regex(args.single_quote_codepoints)

    changes = do_all_replacements(
        all_filenames(args.files), single_quote_regex, double_quote_regex
    )
    if changes:
        print_changes(args, changes)
        sys.exit(1)


if __name__ == "__main__":
    main()
