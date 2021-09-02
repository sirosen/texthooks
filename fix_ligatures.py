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
import argparse
import collections
import glob
import re
import sys

from identify import identify


def codepoint2char(codepoint):
    return chr(int(codepoint, 16))


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


def replace_ligatures_str(s: str) -> str:
    return REPLACEMENT_PATTERN.sub(_re_subfunc, s)


class DiffRecorder:
    def __init__(self):
        # in py3.6+ the dict builtin maintains order, but being explicit is
        # slightly safer since we're being clear about the fact that we want
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


def do_replacements(recorder: DiffRecorder, filename):
    """Given a filename, replace content and write *if* changes were made

    Returns True if changes were made, False if none were made"""
    with open(filename, "r") as f:
        content = f.readlines()

    newcontent = []
    for lineno, line in enumerate(content, 1):
        if not REPLACEMENT_PATTERN.search(line):
            newcontent.append(line)
        else:
            updated = replace_ligatures_str(line)
            newcontent.append(updated)
            if updated != line:
                recorder.add(filename, line, updated, lineno)

    if recorder.hasdiff(filename):
        with open(filename, "w") as f:
            f.write("".join(newcontent))
        return True
    return False


def do_all_replacements(files) -> DiffRecorder:
    """Do replacements over a set of filenames, and return a list of filenames
    where changes were made."""
    recorder = DiffRecorder()

    for fn in all_filenames(files):
        do_replacements(recorder, fn)
    return recorder


def _gen_change_caret_line(original, updated):
    indices = []
    shift = 0
    for idx, c in enumerate(original):
        if c != updated[idx + shift]:
            indices.append(idx)
            shift += len(CHAR_MAP.get(c, c)) - 1
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
        "--show-changes",
        action="store_true",
        default=False,
        help="Show the lines which were changed",
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    changes = do_all_replacements(all_filenames(args.files))
    if changes:
        print_changes(args, changes)
        sys.exit(1)


if __name__ == "__main__":
    main()
