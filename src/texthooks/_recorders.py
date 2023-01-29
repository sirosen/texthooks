import codecs
import collections
import sys
import typing as t

from ._common import colorize


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
    def __init__(self, verbosity: int):
        self.verbosity = verbosity

    def out(self, message: str, verbosity: int = 1, end: str = "\n") -> None:
        if not self.verbosity >= verbosity:
            return
        print(message, end=end)


class DiffRecorder:
    def __init__(self, verbosity: int):
        self._printer = _VPrinter(verbosity)
        # in py3.6+ the dict builtin maintains order, but being explicit is
        # slightly safer since we're being explicit about the fact that we want
        # to retain key order
        self.by_fname: t.MutableMapping[
            str, t.List[t.Tuple[str, str, int]]
        ] = collections.OrderedDict()
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
        content = _readlines(filename, self._file_encoding)

        newcontent = []
        for lineno, line in enumerate(content, 1):
            newline = line_fixer(line)
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
                    self._printer.out(f"  line {lineno}:")
                    self._printer.out(f"    {original}")
                    self._printer.out(f"    {updated}")
                    self._printer.out(f"    {caret_line}")


class CheckRecorder:
    def __init__(self, verbosity: int):
        self._printer = _VPrinter(verbosity)
        self.by_fname: t.MutableMapping[
            str, t.List[t.Tuple[str, str, int]]
        ] = collections.OrderedDict()
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
