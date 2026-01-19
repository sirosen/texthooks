from textwrap import dedent as d

import pytest

from texthooks.alphabetize_codeowners import main as alphabetize_codeowners_main


@pytest.mark.parametrize("dialect", ("standard", "gitlab"))
def test_alphabetize_codeowners_no_changes(runner, dialect):
    result = runner(alphabetize_codeowners_main, "foo", add_args=["--dialect", dialect])
    assert result.exit_code == 0
    assert result.file_data == "foo"

    result = runner(alphabetize_codeowners_main, "/foo/bar.txt @alice @bob")
    assert result.exit_code == 0
    assert result.file_data == "/foo/bar.txt @alice @bob"


@pytest.mark.parametrize("dialect", ("standard", "gitlab"))
def test_alphabetize_codeowners_normalizes_spaces(runner, dialect):
    result = runner(
        alphabetize_codeowners_main,
        " /foo/bar.txt @alice\t@bob ",
        add_args=["--dialect", dialect],
    )
    assert result.exit_code == 1
    assert result.file_data == "/foo/bar.txt @alice @bob"


@pytest.mark.parametrize("dialect", ("standard", "gitlab"))
def test_alphabetize_codeowners_sorts(runner, dialect):
    result = runner(
        alphabetize_codeowners_main,
        "/foo/bar.txt @Bob @alice @charlie",
        add_args=["--dialect", dialect],
    )
    assert result.exit_code == 1
    assert result.file_data == "/foo/bar.txt @alice @Bob @charlie"


@pytest.mark.parametrize("dialect", ("standard", "gitlab"))
def test_alphabetize_codeowners_sorts_other(runner, dialect):
    result = runner(
        alphabetize_codeowners_main,
        "/foo/bar.txt @Andy @adam @Bob @alice @charlie @groß @grost @grose",
        add_args=["--dialect", dialect],
    )
    assert result.exit_code == 1
    assert (
        result.file_data
        == "/foo/bar.txt @adam @alice @Andy @Bob @charlie @grose @groß @grost"
    )


@pytest.mark.parametrize("dialect", ("standard", "gitlab"))
def test_alphabetize_codeowners_ignores_non_semantic_lines(runner, dialect):
    result = runner(
        alphabetize_codeowners_main,
        """
        # comment 1: some comment

        # comment 2: some non-alphabetized strings
        # d c b a
        /foo/bar.txt @alice @charlie
        """,
        add_args=["--dialect", dialect],
    )
    assert result.exit_code == 0


def test_gitlab_alphabetize_codeowners_alphabetizes_default_owners(runner):
    result = runner(
        alphabetize_codeowners_main,
        """\
        # section
        [D A C B]
        # optional section
        ^[D A C B E]
        # section with owners
        [D A C B] @mallory @alice
        /foo/bar.txt
        /foo/baz.txt""",
        add_args=["--dialect", "gitlab"],
    )
    assert result.exit_code == 1
    assert result.file_data == d("""\
        # section
        [D A C B]
        # optional section
        ^[D A C B E]
        # section with owners
        [D A C B] @alice @mallory
        /foo/bar.txt
        /foo/baz.txt""")


def test_gitlab_alphabetize_codeowners_alphabetizes_default_owners_with_min_reviewers(
    runner,
):
    result = runner(
        alphabetize_codeowners_main,
        """\
        [D A C B][2] @bob @mallory @alice
        /foo/bar.txt
        /foo/baz.txt""",
        add_args=["--dialect", "gitlab"],
    )
    assert result.exit_code == 1
    assert result.file_data == d("""\
        [D A C B][2] @alice @bob @mallory
        /foo/bar.txt
        /foo/baz.txt""")


@pytest.mark.parametrize("dialect", ("standard", "gitlab"))
def test_alphabetize_codeowners_accepts_inline_comments(runner, dialect):
    result = runner(
        alphabetize_codeowners_main,
        """\
        # some non-alphabetized strings will follow
        /foo/bar.txt @charlie @alice  # d b a c""",
        add_args=["--dialect", dialect],
    )
    assert result.exit_code == 1
    assert result.file_data == d("""\
        # some non-alphabetized strings will follow
        /foo/bar.txt @alice @charlie  # d b a c""")


# a regression test for https://github.com/sirosen/texthooks/issues/111
def test_space_removal_will_align_in_show_changes_output(runner):
    result = runner(
        alphabetize_codeowners_main,
        """\
        /foo/bar.txt    @alice      @bob
        """,
        add_args=["--show-changes", "--color=off"],
    )
    assert result.exit_code == 1
    assert result.stdout == d(f"""\
        Changes were made in these files:
          {result.filename}
          line 1:
            - /foo/bar.txt    @alice      @bob
                           ---       -----
            + /foo/bar.txt @alice @bob
        """)
    assert result.file_data == "/foo/bar.txt @alice @bob\n"
