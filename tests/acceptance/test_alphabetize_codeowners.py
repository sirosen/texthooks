from texthooks.alphabetize_codeowners import main as alphabetize_codeowners_main


def test_alphabetize_codeowners_no_changes(runner):
    result = runner(alphabetize_codeowners_main, "foo")
    assert result.exit_code == 0
    assert result.file_data == "foo"

    result = runner(alphabetize_codeowners_main, "/foo/bar.txt @alice @bob")
    assert result.exit_code == 0
    assert result.file_data == "/foo/bar.txt @alice @bob"


def test_alphabetize_codeowners_normalizes_spaces(runner):
    result = runner(alphabetize_codeowners_main, "/foo/bar.txt   @alice @bob")
    assert result.exit_code == 1
    assert result.file_data == "/foo/bar.txt @alice @bob"


def test_alphabetize_codeowners_sorts(runner):
    result = runner(alphabetize_codeowners_main, "/foo/bar.txt @bob @alice")
    assert result.exit_code == 1
    assert result.file_data == "/foo/bar.txt @alice @bob"
