# tox-uv

[![PyPI version](https://badge.fury.io/py/tox-uv.svg)](https://badge.fury.io/py/tox-uv)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/tox-uv.svg)](https://pypi.python.org/pypi/tox-uv/)
[![check](https://github.com/tox-dev/tox-uv/actions/workflows/check.yml/badge.svg)](https://github.com/tox-dev/tox-uv/actions/workflows/check.yml)
[![Downloads](https://static.pepy.tech/badge/tox-uv/month)](https://pepy.tech/project/tox-uv)

**tox-uv** is a tox plugin which replaces virtualenv and pip with uv your tox environments.
Note that you will get both the benefits (performance) or downsides (bugs) of uv.

Simply install `tox-uv` into the environment your tox is installed and will replace virtualenv and pip in the tox
run environments with uv.

Note: currently we haven't implemented uv support for packaging environments, so only your run tox environments will
use uv.

## Configuration

### uv_seed

This flag controls if the created virtual environment injects pip/setuptools/wheel into the created virtual environment
or not. By default, is off.
