# tox-uv

[![PyPI version](https://badge.fury.io/py/tox-uv.svg)](https://badge.fury.io/py/tox-uv)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/tox-uv.svg)](https://pypi.python.org/pypi/tox-uv/)
[![check](https://github.com/tox-dev/tox-uv/actions/workflows/check.yaml/badge.svg)](https://github.com/tox-dev/tox-uv/actions/workflows/check.yaml)
[![Downloads](https://static.pepy.tech/badge/tox-uv/month)](https://pepy.tech/project/tox-uv)

**tox-uv** is a tox plugin which replaces virtualenv and pip with uv in your tox environments.
Note that you will get both the benefits (performance) or downsides (bugs) of uv.

## How to use

Install `tox-uv` into the environment of your tox and it will replace virtualenv and pip for all runs:

```bash
python -m pip install tox-uv
python -m tox r -e py312 # will use uv
```

## Configuration

- `uv-venv-runner` is the ID for the tox environments [runner](https://tox.wiki/en/4.12.1/config.html#runner).
- `uv-venv-pep-517` is the ID for the PEP-517 packaging environment.
- `uv-venv-cmd-builder` is the ID for the external cmd builder.

### uv_seed

This flag, set on a tox environment level, controls if the created virtual environment injects pip/setuptools/wheel into
the created virtual environment or not. By default, is off. You will need to set this if you have a project that uses
the old legacy editable mode, or your project does not support the `pyproject.toml` powered isolated build model.

### uv_resolution

This flag, set on a tox environment level, informs uv of the desired [resolution strategy]:

- `highest` - (default) selects the highest version of a package that satisfies the constraints
- `lowest` - install the **lowest** compatible versions for all dependencies, both **direct** and **transitive**
- `lowest-direct` - opt for the **lowest** compatible versions for all **direct** dependencies, while using the
  **latest** compatible versions for all **transitive** dependencies

This is a uv specific feature that may be used as an alternative to frozen constraints for test environments, if the
intention is to validate the lower bounds of your dependencies during test executions.

[resolution strategy]: https://github.com/astral-sh/uv/blob/0.1.20/README.md#resolution-strategy

### uv_python_preference

This flag, set on a tox environment level, controls how uv select the Python
interpreter.

By default, uv will attempt to use Python versions found on the system and only
download managed interpreters when necessary. However, It's possible to adjust
uv's Python version selection preference with the
[python-preference](https://docs.astral.sh/uv/concepts/python-versions/#adjusting-python-version-preferences)
option.
