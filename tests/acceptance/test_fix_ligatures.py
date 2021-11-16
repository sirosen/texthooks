from texthooks.fix_ligatures import main as fix_ligatures_main


def test_fix_ligature_no_changes(runner):
    result = runner(fix_ligatures_main, "foo")
    assert result.exit_code == 0
    assert result.file_data == "foo"


def test_fix_ligature_fi_stylistic_ligature(runner):
    result = runner(
        fix_ligatures_main,
        """
conﬁg
""",
    )
    assert result.exit_code == 1
    assert (
        result.file_data
        == """
config
"""
    )


def test_fix_ligature_showchanges_nocolor(runner):
    result = runner(
        fix_ligatures_main,
        """
conﬁg conﬁg
""",
        add_args=["--show-changes", "--color=off"],
    )
    assert result.exit_code == 1
    assert (
        result.file_data
        == """
config config
"""
    )
    assert (
        result.stdout
        == f"""\
Changes were made in these files:
  {result.filename}
  line 2:
    -conﬁg conﬁg
    +config config
        ^      ^
"""
    )
