from textwrap import dedent as d

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
    assert result.file_data == d("""
        foo-bar--baz
        """)


def test_fix_unicode_dashes_fullwidth_and_minus(runner):
    # U+FF0D (fullwidth hyphen-minus), U+2212 (minus sign)
    result = runner(
        fix_unicode_dashes_main,
        """
        foo－bar−baz
        """,
    )
    assert result.exit_code == 1
    assert result.file_data == d("""
        foo--bar-baz
        """)


def test_fix_unicode_dashes_showchanges(runner):
    result = runner(
        fix_unicode_dashes_main,
        """
        foo–bar
        """,
        add_args=["--show-changes"],
    )
    assert result.exit_code == 1
    assert result.file_data == d("""
        foo-bar
        """)
    assert strip_ansi(result.stdout) == d(f"""\
        Changes were made in these files:
          {result.filename}
          line 2:
            - foo–bar
                 ^
            + foo-bar
                 ^
        """)


def test_fix_unicode_dashes_emdash_only(runner):
    result = runner(
        fix_unicode_dashes_main,
        """
        foo—bar
        """,
    )
    assert result.exit_code == 1
    assert result.file_data == d("""
        foo--bar
        """)


def test_fix_unicode_dashes_mixed_dashes(runner):
    result = runner(
        fix_unicode_dashes_main,
        """
        foo–bar—baz–qux—quux
        """,
    )
    assert result.exit_code == 1
    assert result.file_data == d("""
        foo-bar--baz-qux--quux
        """)


def test_fix_unicode_dashes_new_characters(runner):
    # Test the new characters added based on reviewer feedback
    # U+2012 (figure dash), U+02D7 (modifier letter minus), U+2796 (heavy minus)
    # U+2010 (hyphen), U+2011 (non-breaking hyphen), U+FE63 (small hyphen-minus)
    result = runner(
        fix_unicode_dashes_main,
        """
        foo‒bar˗baz➖qux‐quux‑corge﹣grault
        """,
    )
    assert result.exit_code == 1
    assert result.file_data == d("""
        foo-bar-baz-qux-quux-corge-grault
        """)


def test_fix_unicode_dashes_small_em_dash(runner):
    # U+FE58 (SMALL EM DASH)
    result = runner(
        fix_unicode_dashes_main,
        """
        foo﹘bar
        """,
    )
    assert result.exit_code == 1
    assert result.file_data == d("""
        foo--bar
        """)


def test_fix_unicode_dashes_can_have_a_rule_disabled(runner):
    # pass `""` for a list of codepoints to disable the rule
    result = runner(
        fix_unicode_dashes_main,
        """
        foo—bar
        """,
        add_args=["--double-hyphen-codepoints", ""],
    )
    assert result.exit_code == 0

    # run again on double-hyphen case
    result = runner(
        fix_unicode_dashes_main,
        """
        foo–bar
        """,
        add_args=["--single-hyphen-codepoints", ""],
    )
    assert result.exit_code == 0
