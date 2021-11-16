import pytest

from texthooks.fix_ligatures import parse_args as fix_ligatures_parse_args
from texthooks.fix_smartquotes import (
    DEFAULT_DOUBLE_QUOTE_CODEPOINTS,
    DEFAULT_SINGLE_QUOTE_CODEPOINTS,
)
from texthooks.fix_smartquotes import parse_args as fix_smartquotes_parse_args


def test_fix_ligatures_arg_parsing():
    args1 = fix_ligatures_parse_args(argv=["foo", "bar"])
    assert list(args1.files) == ["foo", "bar"]
    assert args1.show_changes is False

    args2 = fix_ligatures_parse_args(argv=["foo", "--show-changes"])
    assert list(args2.files) == ["foo"]
    assert args2.show_changes is True


def test_fix_smartquotes_arg_parsing():
    args1 = fix_smartquotes_parse_args(argv=["foo", "bar"])
    assert list(args1.files) == ["foo", "bar"]
    assert args1.show_changes is False
    assert args1.double_quote_codepoints == DEFAULT_DOUBLE_QUOTE_CODEPOINTS
    assert args1.single_quote_codepoints == DEFAULT_SINGLE_QUOTE_CODEPOINTS

    args2 = fix_smartquotes_parse_args(argv=["foo", "--show-changes"])
    assert list(args2.files) == ["foo"]
    assert args2.show_changes is True
    assert args2.double_quote_codepoints == DEFAULT_DOUBLE_QUOTE_CODEPOINTS
    assert args2.single_quote_codepoints == DEFAULT_SINGLE_QUOTE_CODEPOINTS

    args3 = fix_smartquotes_parse_args(
        argv=["foo", "--double-quote-codepoints", "FF02,201C"]
    )
    assert list(args3.files) == ["foo"]
    assert args3.show_changes is False
    assert list(args3.double_quote_codepoints) == ["FF02", "201C"]
    assert args3.single_quote_codepoints == DEFAULT_SINGLE_QUOTE_CODEPOINTS

    args4 = fix_smartquotes_parse_args(
        argv=["foo", "--single-quote-codepoints", "FF07,201B"]
    )
    assert list(args4.files) == ["foo"]
    assert args4.show_changes is False
    assert args2.double_quote_codepoints == DEFAULT_DOUBLE_QUOTE_CODEPOINTS
    assert list(args4.single_quote_codepoints) == ["FF07", "201B"]


@pytest.mark.parametrize(
    "parse_func", [fix_ligatures_parse_args, fix_smartquotes_parse_args]
)
def test_invalid_color_opt(parse_func):
    with pytest.raises(SystemExit) as excinfo:
        parse_func(argv=["foo", "--color", "bar"])
    err = excinfo.value
    assert err.code == 2
