version := `uvx mddj read version`
default_py_minor_version := `python -c 'import sys;print(sys.version_info[1],end="")'`
git_remote_name := `git rev-parse --abbrev-ref @{push} | cut -d '/' -f1`

# show help
default:
    just --list
    @echo
    just --evaluate

# setup a project-level virtualenv + pre-commit hooks
install:
    python -m venv --upgrade-deps .venv
    .venv/bin/pip install -e .
    pre-commit install --install-hooks

# run a command provided by the package
run command *FLAGS:
    .venv/bin/{{command}} {{FLAGS}}

# run lint tools
lint:
    pre-commit run --skip black --skip isort --skip slyp --skip pyupgrade
    tox r -e mypy
# run autofixers and formatters
format:
    pre-commit run black isort slyp pyupgrade

# run primary testsuite via tox
test *FLAGS:
    tox run -e test-py3.{{default_py_minor_version}} {{FLAGS}}

# run all of the standard tests via tox (in parallel)
test-all *FLAGS:
    tox run-parallel {{FLAGS}}

# tag and publish a release
release:
    git tag -a "{{version}}" -m "v{{version}}"
    git push {{git_remote_name}} refs/tags/{{version}}
    tox r -e publish-release

# cleanup caches and ephemeral files
clean:
    rm -rf dist *.egg-info .tox .venv
    find . -type d -name '__pycache__' -exec rm -r {} +
