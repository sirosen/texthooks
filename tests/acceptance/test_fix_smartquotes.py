from texthooks._common import strip_ansi
from texthooks.fix_smartquotes import main as fix_smartquotes_main


def test_fix_smartquotes_no_changes(runner):
    result = runner(fix_smartquotes_main, "foo")
    assert result.exit_code == 0
    assert result.file_data == "foo"


def test_fix_smartquotes_simple_double_quote(runner):
    result = runner(
        fix_smartquotes_main,
        """
“some data”
""",
    )
    assert result.exit_code == 1
    assert (
        result.file_data
        == """
"some data"
"""
    )


def test_fix_smartquotes_fullwidth_apostrophe(runner):
    result = runner(
        fix_smartquotes_main,
        """
don＇t write like this
""",
    )
    assert result.exit_code == 1
    assert (
        result.file_data
        == """
don't write like this
"""
    )


def test_fix_smartquotes_showchanges(runner):
    result = runner(
        fix_smartquotes_main,
        """
don＇t write like this
""",
        add_args=["--show-changes"],
    )
    assert result.exit_code == 1
    assert (
        result.file_data
        == """
don't write like this
"""
    )
    assert (
        strip_ansi(result.stdout)
        == f"""\
Changes were made in these files:
  {result.filename}
  line 2:
    -don＇t write like this
    +don't write like this
        ^
"""
    )
