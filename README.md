# fix-smartquotes

A pre-commit hook for automatically finding and replacing smartquote
characters with the standard ascii `"` and `'` characters.

This fixes copy-paste from some applications which replace double-quotes with curly
quotes.
It does *not* convert corner brackets, braile quotation marks, or angle
quotation marks. Those characters are not typically the result of copy-paste
errors, so they are allowed.

Low quotation marks vary in usage and meaning by language, and some languages
use quotation marks which are facing "outwards" (opposite facing from english).
For the most part, these and exotic characters (double-prime quotes) are
ignored.

In files with the offending marks, they are replaced and the run is marked as
failed.

## Supported Hooks

Only one hook is provided, `fix-smartquotes`.

Use it in `.pre-commit-config.yaml` like so:

```yaml
- repo: https://github.com/sirosen/fix-smartquotes
  rev: 0.1.1
  hooks:
    - id: fix-smartquotes
```

## Overriding Quotation Characters

Two options are available for specifying exactly which characters will be
replaced. For ease of use, they are specified as hex-encoded unicode
codepoints.

Suppose you wanted to *avoid* replacing the "Heavy single comma quotation
mark ornament" (`275C`) and the "Heavy single turned comma quotation mark
ornament" (`275B`) characters. You could override the single quote codepoints
as follows:

```yaml
- repo: https://github.com/sirosen/fix-smartquotes
  rev: 0.1.1
  hooks:
    - id: fix-smartquotes
      # replace default single quote chars with this set:
      # apostrophe, fullwidth apostrophe, left single quote, single high
      # reversed-9 quote, right single quote
      args: ["--single-quote-codepoints", "0027,FF07,2018,201B,2019"]
```

## Standalone Usage

You can also `pip install fix-smartquotes` to run the tool manually.

For full usage info:

```bash
fix-smartquotes --help
```
