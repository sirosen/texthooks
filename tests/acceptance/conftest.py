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

    def __str__(self):
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


@pytest.fixture
def runner(tmp_path, capsys):
    def func(
        fixer_main: t.Callable,
        data: str,
        *,
        add_args: t.Optional[t.List[str]] = None,
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

        old_cwd = pathlib.Path.cwd()
        try:
            os.chdir(tmp_path)
            result = _CLIResult(filename)
            result.exit_code = fixer_main(argv=[filename] + add_args)
        finally:
            os.chdir(old_cwd)

        with open(newfile, encoding=encoding) as fp:
            result.file_data = fp.read()

        captured = capsys.readouterr()
        result.stdout = captured.out
        result.stderr = captured.err

        return result

    return func
