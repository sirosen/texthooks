# texthooks

A collection of `pre-commit` hooks for handling text files.

In particular, hooks for handling unicode characters which may be undesirable
in a repository.

## Usage with pre-commit

To use with `pre-commit`, include this repo and the desired hooks in
`.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/sirosen/texthooks
  rev: 0.1.0
  hooks:
    - id: fix-smartquotes
    - id: fix-ligatures
```

## Standalone Usage

Each hook is usable as a CLI script. Simply

```bash
pip install texthooks
```

and then invoke, e.g.

```bash
fix-smartquotes FILENAME
```

## Supported Hooks

### `fix-smartquotes`

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

#### Overriding Quotation Characters

Two options are available for specifying exactly which characters will be
replaced. For ease of use, they are specified as hex-encoded unicode
codepoints.

Suppose you wanted to *avoid* replacing the "Heavy single comma quotation
mark ornament" (`275C`) and the "Heavy single turned comma quotation mark
ornament" (`275B`) characters. You could override the single quote codepoints
as follows:

```yaml
- repo: https://github.com/sirosen/texthooks
  rev: 0.1.0
  hooks:
    - id: fix-smartquotes
      # replace default single quote chars with this set:
      # apostrophe, fullwidth apostrophe, left single quote, single high
      # reversed-9 quote, right single quote
      args: ["--single-quote-codepoints", "0027,FF07,2018,201B,2019"]
```

### fix-ligatures

Automatically find and replace ligature characters with their ascii equivalents.

This replaces liguatures which may be created by programs like LaTeX for
presentation with their strictly-equivalent ASCII counterparts. For example,
`fi` and `ff` may be ligature-ized.

This hook converts these back into ASCII so that tools like `grep` will behave
as expected.

### forbid-bidi-controls

This is checker which forbids the use of unicode bidirectional text control
characters.

These are directional formatting characters which can be used to construct text
with unexpected or unclear semantics. For example, in programming languages
which allow bidirectional text in statements, `True = ייִדיש` can be written
with right-to-left reversal to mean that the variable `ייִדיש` is assigned a
value of `True`.

## CHANGELOG

### 0.2.1

- Fix a typo in `forbid-bidi-controls` entrypoint

### 0.2.0

- Add the `forbid-bidi-controls` hook
- Adjust the handling of file encodings. Files will be read with UTF-8 encoding
  by default in most cases.

### 0.1.0

- Initial release with `fix-ligatures` and `fix-smartquotes` hooks
