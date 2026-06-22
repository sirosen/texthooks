from textwrap import dedent as d

from texthooks.fix_arrows import main as fix_arrows_main


def test_fix_arrows_no_changes(runner):
    result = runner(fix_arrows_main, "foo")
    assert result.exit_code == 0
    assert result.file_data == "foo"


def test_fix_arrows_no_changes_verbose(runner):
    result = runner(fix_arrows_main, "foo", add_args=["-v"])
    assert result.exit_code == 0
    assert result.file_data == "foo"
    assert "checking file.txt...ok" in result.stdout


def test_fix_arrows_rightwards_arrow(runner):
    result = runner(
        fix_arrows_main,
        """
        a → b
        """,
    )
    assert result.exit_code == 1
    assert result.file_data == d("""
        a -> b
        """)
    assert "checking file.txt..." not in result.stdout


def test_fix_arrows_rightwards_arrow_verbose(runner):
    result = runner(fix_arrows_main, "a → b\n", add_args=["-v"])
    assert result.exit_code == 1
    assert result.file_data == "a -> b\n"
    assert "checking file.txt...fail" in result.stdout


def test_fix_arrows_multiple_kinds(runner):
    result = runner(
        fix_arrows_main,
        """
        ← → ↔ ⇐ ⇒ ⇔ ⟶ ⟺ ↦
        """,
    )
    assert result.exit_code == 1
    assert result.file_data == d("""
        <- -> <-> <= => <=> --> <==> |->
        """)


def test_fix_arrows_check_does_not_modify(runner):
    result = runner(fix_arrows_main, "a → b\n", add_args=["--check"])
    assert result.exit_code == 1
    assert result.file_data == "a → b\n"


def test_fix_arrows_ignores_vertical_arrows(runner):
    result = runner(fix_arrows_main, "up ↑ down ↓\n")
    assert result.exit_code == 0
    assert result.file_data == "up ↑ down ↓\n"


def test_fix_arrows_showchanges_nocolor(runner):
    result = runner(
        fix_arrows_main,
        "a → b → c\n",
        add_args=["--show-changes", "--color=off"],
    )
    assert result.exit_code == 1
    assert result.file_data == "a -> b -> c\n"
    assert result.stdout == d(f"""\
        Changes were made in these files:
          {result.filename}
          line 1:
            - a → b → c
            + a -> b -> c
        """)
