#
# common tools/utilities
#
import argparse
import collections
import glob
import typing as t

import identify


def codepoint2char(codepoint: str) -> str:
    return chr(int(codepoint, 16))


def codepoints2chars(codepoints: t.Sequence[str]) -> t.List[str]:
    return [chr(int(c, 16)) for c in codepoints]


def all_filenames(files: t.Optional[t.Iterable[str]]) -> t.Iterator[str]:
    if not files:
        for fn in glob.iglob("**/*", recursive=True):
            tags = identify.tags_from_path(fn)
            if "text" in tags:
                yield fn
    else:
        for fn in files:
            yield fn


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

    def run_line_fixer(self, line_fixer: t.Callable[[str], str], filename: str):
        """Given a filename, replace content and write *if* changes were made, using a
        line-fixer function which takes lines as input and produces lines as output.

        Returns True if changes were made, False if none were made"""
        with open(filename, "r") as f:
            content = f.readlines()

        newcontent = []
        for lineno, line in enumerate(content, 1):
            newline = line_fixer(line)
            newcontent.append(newline)
            if newline != line:
                self.add(filename, line, newline, lineno)

        if self.hasdiff(filename):
            with open(filename, "w") as f:
                f.write("".join(newcontent))
            return True
        return False

    def print_changes(self, show_changes: bool) -> None:
        print("Changes were made in these files:")
        for filename, changeset in self.items():
            print(f"  \033[0;33m{filename}\033[0m")
            if show_changes:
                for (original, updated, lineno) in changeset:
                    original, updated = original.rstrip(), updated.rstrip()
                    caret_line = _gen_change_caret_line(original, updated)
                    print(f"  line {lineno}:")
                    print(f"  \033[0;91m-{original}\033[0m")
                    print(f"  \033[0;92m+{updated}\033[0m")
                    print(f"  \033[1;96m {caret_line}\033[0m")


def standard_cli_parser(doc):
    parser = argparse.ArgumentParser(
        description=doc, formatter_class=argparse.RawDescriptionHelpFormatter
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

    return parser
