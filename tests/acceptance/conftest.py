import contextlib
import os
import pathlib
import textwrap
import typing as t

import pytest


class _CLIResult:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.file_data = None
        self.exit_code = 0
        self.stdout = ""
        self.stderr = ""

    def __str__(self):  # pragma: no cover
        return f"""\
<CLIResult>
exit_code: {self.exit_code}
<stdout>
{self.stdout}
</stdout>
<stderr>
{self.stderr}
</stderr>
</CLIResult>
"""

    @contextlib.contextmanager
    def trap_system_exit(self) -> t.Iterator[None]:
        try:
            yield
        except SystemExit as e:
            self.exit_code = e.code


@contextlib.contextmanager
def _pushd(dir: pathlib.Path) -> t.Iterator[None]:
    old_cwd = pathlib.Path.cwd()
    try:
        os.chdir(dir)
        yield
    finally:
        os.chdir(old_cwd)


@pytest.fixture
def runner(tmp_path, capsys):
    def func(
        fixer_main: t.Callable,
        data: str,
        *,
        add_args: list[str] | None = None,
        filename: str = "file.txt",
        encoding: str = "utf-8",
        dedent: bool = True,
    ):
        if not add_args:
            add_args = []
        if dedent:
            data = textwrap.dedent(data)
        newfile = tmp_path / filename
        newfile.write_text(data, encoding=encoding)

        result = _CLIResult(filename)
        with _pushd(tmp_path), result.trap_system_exit():
            fixer_main(argv=[filename] + add_args)

        with open(newfile, encoding=encoding) as fp:
            result.file_data = fp.read()

        captured = capsys.readouterr()
        result.stdout = captured.out
        result.stderr = captured.err

        return result

    return func
