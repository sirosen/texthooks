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
