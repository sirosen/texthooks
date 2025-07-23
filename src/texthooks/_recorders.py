from __future__ import annotations

import codecs
import collections
import difflib
import sys
import typing as t

from ._common import colorize


def create_comparison_lines(old: str, new: str) -> list[str]:
    """Compare two lines to make diff output to show changes."""
    differ = difflib.Differ()
    return [_clean_q(line).rstrip("\n") for line in differ.compare([old], [new])]


# simplify the format produced by Differ (for single-line comparison)
def _clean_q(s: str) -> str:
    if s.startswith("?"):
        return " " + s[1:]
    return s


def colorize_comparison(comparison: list[str]) -> list[str]:
    result = []
    for line in comparison:
        if line.startswith("-"):
            result.append(colorize(line, color="bright_red"))
        elif line.startswith("+"):
            result.append(colorize(line, color="bright_green"))
        elif line.startswith("?"):
            result.append(colorize(line, color="bright_cyan"))
        else:
            result.append(line)
    return result


def _determine_encoding() -> str:
    # determine encoding from defaults, but convert "ascii" to "utf-8"
    encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
    try:
        is_ascii = codecs.lookup(encoding).name == "ascii"
    except LookupError:
        is_ascii = False
    if is_ascii:
        encoding = "utf-8"

    return encoding


def _readlines(filename: str, encoding: str) -> t.List[str]:
    with open(filename, "r", encoding=encoding) as f:
        return f.readlines()


class _VPrinter:
    def __init__(self, verbosity: int) -> None:
        self.verbosity = verbosity

    def out(self, message: str, verbosity: int = 1, end: str = "\n") -> None:
        if not self.verbosity >= verbosity:
            return
        print(message, end=end)


class DiffRecorder:
    def __init__(self, verbosity: int) -> None:
        self._printer = _VPrinter(verbosity)
        # in py3.6+ the dict builtin maintains order, but being explicit is
        # slightly safer since we're being explicit about the fact that we want
        # to retain key order
        self.by_fname: t.MutableMapping[str, t.List[t.Tuple[str, str, int]]] = (
            collections.OrderedDict()
        )
        self._file_encoding = _determine_encoding()

    def add(self, fname, original, updated, lineno):
        if fname not in self.by_fname:
            self.by_fname[fname] = []
        self.by_fname[fname].append((original, updated, lineno))

    def hasdiff(self, fname):
        return bool(self.by_fname.get(fname))

    def __bool__(self):
        return bool(self.by_fname)

    def items(self):
        return self.by_fname.items()

    def run_line_fixer(self, line_fixer: t.Callable[[str], str], filename: str):
        """Given a filename, replace content and write *if* changes were made, using a
        line-fixer function which takes lines as input and produces lines as output.

        Returns True if changes were made, False if none were made"""
        self._printer.out(f"checking {filename}...", end="", verbosity=2)
        try:
            content = _readlines(filename, self._file_encoding)
        except FileNotFoundError:
            self._printer.out(f"fail, FileNotFound: {filename}", verbosity=1)
            raise

        newcontent = []
        for lineno, line in enumerate(content, 1):
            newline = line_fixer(line)
            # re-add newline if it was stripped by the fixer
            if line.endswith("\n") and not newline.endswith("\n"):
                newline += "\n"
            newcontent.append(newline)
            if newline != line:
                self.add(filename, line, newline, lineno)

        if self.hasdiff(filename):
            self._printer.out("fail", verbosity=2)
            with open(filename, "w", encoding=self._file_encoding) as f:
                f.write("".join(newcontent))
            return True
        self._printer.out("ok", verbosity=2)
        return False

    def print_changes(
        self,
        show_changes: bool,
        ansi_colors: bool,
        *,
        charwidth: t.Optional[t.Callable[[str], int]] = None,
    ) -> None:
        self._printer.out("Changes were made in these files:")
        for filename, changeset in self.items():
            if ansi_colors:
                filename_c = colorize(filename, color="yellow")
            else:
                filename_c = filename
            self._printer.out(f"  {filename_c}")
            if show_changes:
                for original, updated, lineno in changeset:
                    comparison = create_comparison_lines(original, updated)
                    if ansi_colors:
                        comparison = colorize_comparison(comparison)
                    self._printer.out(f"  line {lineno}:")
                    for line in comparison:
                        self._printer.out(f"    {line}")


class CheckRecorder:
    def __init__(self, verbosity: int) -> None:
        self._printer = _VPrinter(verbosity)
        self.by_fname: t.MutableMapping[str, t.List[t.Tuple[str, str, int]]] = (
            collections.OrderedDict()
        )
        self._file_encoding = _determine_encoding()

    def add(self, fname, lineno):
        if fname not in self.by_fname:
            self.by_fname[fname] = []
        self.by_fname[fname].append(lineno)

    def __bool__(self):
        return bool(self.by_fname)

    def items(self):
        return self.by_fname.items()

    def run_line_checker(
        self, line_checker: t.Callable[[str], bool], filename: str
    ) -> bool:
        self._printer.out(f"checking {filename}...", end="", verbosity=2)
        content = _readlines(filename, self._file_encoding)

        for lineno, line in enumerate(content, 1):
            if not line_checker(line):
                self.add(filename, lineno)

        if filename in self.by_fname:
            self._printer.out("fail", verbosity=2)
            return True
        self._printer.out("ok", verbosity=2)
        return False

    def print_failures(self, checkname: str, ansi_colors: bool) -> None:
        self._printer.out(f"These files failed the {checkname} check:")
        for filename, linenos in self.items():
            if ansi_colors:
                filename_c = colorize(filename, color="yellow")
            else:
                filename_c = filename
            self._printer.out(f"  {filename_c}")
            commasep_linenos = ",".join(str(x) for x in linenos)
            if len(linenos) == 1:
                prefix = "lineno"
            else:
                prefix = "line numbers"
            self._printer.out(f"  {prefix}: {commasep_linenos}")
