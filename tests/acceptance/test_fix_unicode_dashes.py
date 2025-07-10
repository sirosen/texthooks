from texthooks._common import strip_ansi
from texthooks.fix_unicode_dashes import main as fix_unicode_dashes_main


def test_fix_unicode_dashes_no_changes(runner):
    result = runner(fix_unicode_dashes_main, "foo-bar")
    assert result.exit_code == 0
    assert result.file_data == "foo-bar"


def test_fix_unicode_dashes_en_em_dash(runner):
    result = runner(
        fix_unicode_dashes_main,
        """
foo–bar—baz
""",
    )
    assert result.exit_code == 1
    assert (
        result.file_data
        == """
foo-bar-baz
"""
    )


def test_fix_unicode_dashes_fullwidth_and_minus(runner):
    # U+FF0D (fullwidth hyphen-minus), U+2212 (minus sign)
    result = runner(
        fix_unicode_dashes_main,
        """
foo－bar−baz
""",
    )
    assert result.exit_code == 1
    assert (
        result.file_data
        == """
foo-bar-baz
"""
    )


def test_fix_unicode_dashes_showchanges(runner):
    result = runner(
        fix_unicode_dashes_main,
        """
foo–bar
""",
        add_args=["--show-changes"],
    )
    assert result.exit_code == 1
    assert (
        result.file_data
        == """
foo-bar
"""
    )
    assert (
        strip_ansi(result.stdout)
        == f"""\
Changes were made in these files:
  {result.filename}
  line 2:
    -foo–bar
    +foo-bar
        ^
"""
    )
