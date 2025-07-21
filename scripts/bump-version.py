#!/usr/bin/env python
import re
import shutil
import subprocess
import sys


def mddj_write_version(new_version):
    subprocess.run(["uvx", "mddj", "write", "version", new_version], check=True)


def get_old_version() -> str:
    read_proc = subprocess.run(
        ["uvx", "mddj", "read", "version"], check=True, capture_output=True, text=True
    )
    return read_proc.stdout.strip()


def replace_version(filename, prefix, old_version, new_version):
    print(f"updating {filename}")
    with open(filename) as fp:
        content = fp.read()
    old_str = prefix + old_version
    new_str = prefix + new_version
    content = content.replace(old_str, new_str)
    with open(filename, "w") as fp:
        fp.write(content)


def update_changelog(new_version):
    print("updating changelog in README.md")
    with open("README.md") as fp:
        content = fp.read()

    insert_marker = "<!-- bumpversion-changelog -->"

    content = re.sub(
        r"\#\#\#\s+Unreleased(\s*\n)+" + re.escape(insert_marker),
        f"""\
### Unreleased

{insert_marker}

### {new_version}
""",
        content,
    )
    with open("README.md", "w") as fp:
        fp.write(content)


def parse_version(s):
    vals = s.split(".")
    assert len(vals) == 3
    return tuple(int(x) for x in vals)


def comparse_versions(old_version, new_version):
    assert parse_version(new_version) > parse_version(old_version)


def main():
    if len(sys.argv) != 2:
        sys.exit(2)

    has_uvx = bool(shutil.which("uvx"))
    if not has_uvx:
        print("this script requires uvx", file=sys.stderr)
        sys.exit(2)

    new_version = sys.argv[1]
    old_version = get_old_version()
    print(f"old = {old_version}, new = {new_version}")
    comparse_versions(old_version, new_version)

    replace_version("README.md", "rev: ", old_version, new_version)
    update_changelog(new_version)
    mddj_write_version(new_version)


if __name__ == "__main__":
    main()
