# fix-ligatures

A pre-commit hook for automatically finding and replacing ligature
characters with their ascii equivalents.

## Supported Hooks

Only one hook is provided, `fix-ligatures`.

Use it in `.pre-commit-config.yaml` like so:

```yaml
- repo: https://github.com/sirosen/fix-ligatures
  rev: 0.1.0
  hooks:
    - id: fix-ligatures
```

## Standalone Usage

You can also `pip install fix-ligatures` to run the tool manually.

For full usage info:

```bash
fix-ligatures --help
```
