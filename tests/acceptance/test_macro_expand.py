from texthooks.macro_expand import main as macro_expand_main


def test_macro_expand_no_changes(runner):
    result = runner(macro_expand_main, "foo")
    assert result.exit_code == 0
    assert result.file_data == "foo"


def test_macro_expand_simple(runner):
    result = runner(macro_expand_main, "f:bar", add_args=["--macro", "f:", "f($VALUE)"])
    assert result.exit_code == 1
    assert result.file_data == "f(bar)"


def test_macro_expand_value_appears_twice(runner):
    result = runner(
        macro_expand_main, "l:bar", add_args=["--macro", "l:", "l($VALUE) - $VALUE"]
    )
    assert result.exit_code == 1
    assert result.file_data == "l(bar) - bar"
