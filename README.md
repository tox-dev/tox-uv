# tox-uv

[![PyPI version](https://badge.fury.io/py/tox-uv.svg)](https://badge.fury.io/py/tox-uv)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/tox-uv.svg)](https://pypi.python.org/pypi/tox-uv/)
[![check](https://github.com/tox-dev/tox-uv/actions/workflows/check.yml/badge.svg)](https://github.com/tox-dev/tox-uv/actions/workflows/check.yml)
[![Downloads](https://static.pepy.tech/badge/tox-uv/month)](https://pepy.tech/project/tox-uv)

**tox-uv** is a tox plugin which replaces virtualenv and pip with uv your tox environments.
Note that you will get both the benefits (performance) or downsides (bugs) of uv.

## How to use

Install `tox-uv` into the environment of your tox and will replace virtualenv and pip for all runs:

```bash
python -m pip install tox tox-uv
python -m tox r -e py312 # will use uv
```

## Configuration

- `uv-venv-runner` is the ID for the tox environments [runner](https://tox.wiki/en/4.12.1/config.html#runner).
- `uv-venv-pep-517` is the ID for the PEP-517 packaging environment.
- `uv-venv-cmd-builder` is the ID for the external cmd builder.

### uv_seed

This flag, set on a tox environment level, controls if the created virtual environment injects pip/setuptools/wheel into
the created virtual environment or not. By default, is off. You will need to set this if you have a project that uses
the old legacy editable mode, or your project does not support the `pyprooject.toml` powered isolated build model.
