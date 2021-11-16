import typing as t

import pytest


class _CLIResult:
    def __init__(self, filename: str):
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
    ):
        if not add_args:
            add_args = []
        newfile = tmp_path / filename
        newfile.write_text(data, encoding=encoding)

        result = _CLIResult(newfile)
        result.exit_code = fixer_main(argv=[str(newfile)] + add_args)

        with open(newfile) as fp:
            result.file_data = fp.read()

        captured = capsys.readouterr()
        result.stdout = captured.out
        result.stderr = captured.err

        return result

    return func
