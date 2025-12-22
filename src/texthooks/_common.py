#
# common tools/utilities
#
import argparse
import glob
import re
import sys
import typing as t

from identify import identify

_ANSI_RE = re.compile(r"\033\[[;?0-9]*[a-zA-Z]")
_ANSI_COLORS = {
    "yellow": 33,
    "bright_red": 91,
    "bright_green": 92,
    "bright_cyan": 96,
}
_ANSI_ESCAPE = "\033"
_ANSI_RESET = f"{_ANSI_ESCAPE}[0m"


def strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)


def colorize(s: str, *, color: str, bold: bool = False) -> str:
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


class ColorParseAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: t.Any,
        option_string: str | None = None,
    ) -> None:
        setattr(namespace, self.dest, values == "on")


def _standard_cli_parser(
    doc: str, fixer: bool, disable_args: t.Iterable[str] | None = None
) -> argparse.ArgumentParser:
    if disable_args is None:
        disable_args = []

    parser = argparse.ArgumentParser(
        description=doc, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    def _maybe_add_arg(*args: t.Any, **kwargs: t.Any) -> None:
        if any(arg in disable_args for arg in args):
            return
        parser.add_argument(*args, **kwargs)

    _maybe_add_arg(
        "files",
        nargs="*",
        help="default: all text files in current directory (recursive)",
    )
    _maybe_add_arg(
        "--show-changes",
        action="store_true",
        default=False,
        help="Show the lines which were changed",
    )
    _maybe_add_arg(
        "-v", "--verbose", action="count", help="Increase output verbosity", default=0
    )
    _maybe_add_arg(
        "-q", "--quiet", action="count", help="Decrease output verbosity", default=0
    )
    _maybe_add_arg(
        "--color",
        type=str.lower,
        nargs=1,
        action=ColorParseAction,
        default="on",
        # TODO: add 'auto' with tty detection
        choices=("off", "on"),
        help="Enable or disable ANSI colors. Defaults to 'on'",
    )
    return parser


def parse_cli_args(
    doc: str,
    *,
    fixer: bool,
    argv: list[str] | None = None,
    modify_parser: t.Callable[[argparse.ArgumentParser], None] | None = None,
    postprocess: t.Callable[[argparse.Namespace], t.Any] | None = None,
    disable_args: t.Iterable[str] | None = None,
) -> argparse.Namespace:
    parser = _standard_cli_parser(doc, fixer, disable_args)
    if modify_parser:
        modify_parser(parser)

    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)

    args.verbosity = 1 + args.verbose - args.quiet

    if postprocess:
        args = postprocess(args)
    return args
