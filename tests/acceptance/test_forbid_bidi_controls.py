from texthooks._common import strip_ansi
from texthooks.forbid_bidi_controls import main as forbid_bidi_controls_main


def test_forbid_bidi_controls_negative(runner):
    result = runner(forbid_bidi_controls_main, "foo")
    assert result.exit_code == 0


def test_forbid_bidi_controls_positive(runner):
    result = runner(
        forbid_bidi_controls_main,
        """
s = "x\u200f" * 100 #    "\u200fx" is assigned
""",
    )
    assert result.exit_code == 1
    assert (
        strip_ansi(result.stdout)
        == f"""\
These files failed the forbid-bidi-controls check:
  {result.filename}
  lineno: 2
"""
    )


def test_forbid_bidi_controls_multiline(runner):
    result = runner(
        forbid_bidi_controls_main,
        """
s = "x\u200f" * 100 #    "\u200fx" is assigned
s = "x\u200f" * 100 #    "\u200fx" is assigned
""",
    )
    assert result.exit_code == 1
    assert (
        strip_ansi(result.stdout)
        == f"""\
These files failed the forbid-bidi-controls check:
  {result.filename}
  line numbers: 2,3
"""
    )
