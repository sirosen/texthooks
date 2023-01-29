# texthooks

A collection of `pre-commit` hooks for handling text files.

In particular, hooks for handling unicode characters which may be undesirable
in a repository.

## Usage with pre-commit

To use with `pre-commit`, include this repo and the desired hooks in
`.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/sirosen/texthooks
  rev: 0.5.0
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

## Hook Summary

| **Hook**               | **Description**                                  |
| ---------------------- | ------------------------------------------------ |
| `fix-smartquotes`      | Replace curly quotes with ASCII quotes.          |
| `fix-spaces`           | Normalize special space markers to ASCII spaces. |
| `fix-ligatures`        | Convert stylistic ligatures to ASCII text.       |
| `forbid-bidi-controls` | Check for bi-directional text.                   |
| `macro-expand`         | A simple way to write text formatting macros.    |

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
  rev: 0.5.0
  hooks:
    - id: fix-smartquotes
      # replace default single quote chars with this set:
      # apostrophe, fullwidth apostrophe, left single quote, single high
      # reversed-9 quote, right single quote
      args: ["--single-quote-codepoints", "0027,FF07,2018,201B,2019"]
```

### `fix-spaces`

Replace various unicode space characters with `" "`.

This normalizes No-Break Space and similar characters to ensure that your files
render the same way in all contexts. It does not modify newlines, carriage
returns, or other whitespace characters outside of the Space Separator
category.

#### Overriding Space Characters

An option is available for specifying exactly which characters will be
replaced. For ease of use, they are specified as hex-encoded unicode
codepoints.

Suppose you wanted to *only* replace Thin Space (codepoint `2009`).
You could override the space codepoints as follows:

```yaml
- repo: https://github.com/sirosen/texthooks
  rev: 0.5.0
  hooks:
    - id: fix-spaces
      args: ["--separator-codepoints", "2009"]
```

### `fix-ligatures`

Automatically find and replace ligature characters with their ascii equivalents.

This replaces liguatures which may be created by programs like LaTeX for
presentation with their strictly-equivalent ASCII counterparts. For example,
`fi` and `ff` may be ligature-ized.

This hook converts these back into ASCII so that tools like `grep` will behave
as expected.

### `forbid-bidi-controls`

This is checker which forbids the use of unicode bidirectional text control
characters.

These are directional formatting characters which can be used to construct text
with unexpected or unclear semantics. For example, in programming languages
which allow bidirectional text in statements, `"X" = ייִדיש` can be written
with right-to-left reversal to mean that the variable `ייִדיש` is assigned a
value of `"X"`.

### `macro-expand`

Replace simple "macro" strings in text. This fixer is a no-op if no macro
arguments are supplied. Add `--macro` to arguments to do replacements.

For example, convert `issue:NNN` to an issue link in markdown with the
following sample config:

```yaml
- repo: https://github.com/sirosen/texthooks
  rev: 0.5.0
  hooks:
    - id: macro-expand
      args:
        - "--macro"
        - "issue:"
        - '[texthooks#$VALUE](https://github.com/sirosen/texthooks/issues/$VALUE)'
```

## CHANGELOG

### Unreleased

<!-- bumpversion-changelog -->

### 0.5.0

- Fix a bug in fixers when running on Windows which could cause data to be
  written with the wrong encoding
- Add `-v/--verbose` and `-q/--quiet` flags to tune output verbosity

### 0.4.0

- Add `fix-spaces` fixer

### 0.3.1

- Minor fixes to docstrings

### 0.3.0

- Add the macro-expand fixer

### 0.2.2

- Fix a bug in CLI argument handling for all hooks

### 0.2.1

- Fix a typo in `forbid-bidi-controls` entrypoint

### 0.2.0

- Add the `forbid-bidi-controls` hook
- Adjust the handling of file encodings. Files will be read with UTF-8 encoding
  by default in most cases.

### 0.1.0

- Initial release with `fix-ligatures` and `fix-smartquotes` hooks
