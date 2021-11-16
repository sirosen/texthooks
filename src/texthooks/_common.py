#
# common tools/utilities
#
import argparse
import collections
import glob
import re
import typing as t

import identify

_ANSI_RE = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")
_ANSI_COLORS = {
    "yellow": 33,
    "bright_red": 91,
    "bright_green": 92,
    "bright_cyan": 96,
}
_ANSI_ESCAPE = "\033"
_ANSI_RESET = f"{_ANSI_ESCAPE}[0m"


def strip_ansi(s: str):
    return _ANSI_RE.sub("", s)


def colorize(s: str, *, color: str, bold: bool = False):
    colorcode = _ANSI_COLORS[color]
    boldcode = "1" if bold else "0"
    ansi_start = f"{_ANSI_ESCAPE}[{boldcode};{colorcode}m"
    return f"{ansi_start}{s}{_ANSI_RESET}"


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


def _gen_change_caret_line(
    original, updated, charwidth: t.Optional[t.Callable[[str], int]]
):
    shift = 0
    indices = []
    for idx, c in enumerate(original):
        if c != updated[idx + shift]:
            indices.append(idx)
            if charwidth is not None:
                shift += charwidth(c) - 1
    gen = ""
    cur = 0
    for idx in indices:
        gen += " " * (idx - cur)
        gen += "^"
        cur = idx
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

    def print_changes(
        self,
        show_changes: bool,
        ansi_colors: bool,
        *,
        charwidth: t.Optional[t.Callable[[str], int]] = None,
    ) -> None:
        print("Changes were made in these files:")
        for filename, changeset in self.items():
            if ansi_colors:
                filename_c = colorize(filename, color="yellow")
            else:
                filename_c = filename
            print(f"  {filename_c}")
            if show_changes:
                for (original, updated, lineno) in changeset:
                    original = "-" + original.rstrip()
                    updated = "+" + updated.rstrip()
                    caret_line = " " + _gen_change_caret_line(
                        original[1:], updated[1:], charwidth
                    )

                    if ansi_colors:
                        original = colorize(original, color="bright_red")
                        updated = colorize(updated, color="bright_green")
                        caret_line = colorize(caret_line, color="bright_cyan")
                    print(f"  line {lineno}:")
                    print(f"    {original}")
                    print(f"    {updated}")
                    print(f"    {caret_line}")


class ColorParseAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, nargs=1, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values == "on")


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
    parser.add_argument(
        "--color",
        type=str.lower,
        action=ColorParseAction,
        default="on",
        # TODO: add 'auto' with tty detection
        choices=("off", "on"),
        help="Enable or disable ANSI colors. Defaults to 'on'",
    )
    return parser
