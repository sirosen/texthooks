#!/usr/bin/env python
import os
import sys

ROOTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_FILE = os.path.join(ROOTDIR, ".pre-commit-hooks.yaml")


def iter_hook_names():
    with open(HOOK_FILE) as fp:
        for line in fp:
            line = line.strip()
            if line.startswith(("name: ", "- name: ")):
                name = line.partition(":")[2].strip()
                if name.startswith("'"):
                    yield name.strip("'")
                elif name.startswith('"'):
                    yield name.strip('"')
                else:
                    yield name


def main():
    success = True
    for hook_name in iter_hook_names():
        if len(hook_name) > 50:
            print(f"ERROR: hook name too long: '{hook_name}'")
            success = False
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
