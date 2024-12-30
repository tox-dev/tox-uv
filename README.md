# tox-uv

[![PyPI version](https://badge.fury.io/py/tox-uv.svg)](https://badge.fury.io/py/tox-uv)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/tox-uv.svg)](https://pypi.python.org/pypi/tox-uv/)
[![check](https://github.com/tox-dev/tox-uv/actions/workflows/check.yaml/badge.svg)](https://github.com/tox-dev/tox-uv/actions/workflows/check.yaml)
[![Downloads](https://static.pepy.tech/badge/tox-uv/month)](https://pepy.tech/project/tox-uv)

**tox-uv** is a `tox` plugin, which replaces `virtualenv` and pip with `uv` in your `tox` environments. Note that you
will get both the benefits (performance) or downsides (bugs) of `uv`.

<!--ts-->

- [How to use](#how-to-use)
- [tox environment types provided](#tox-environment-types-provided)
- [uv.lock support](#uvlock-support)
  - [extras](#extras)
  - [with_dev](#with_dev)
  - [External package support](#external-package-support)
- [Environment creation](#environment-creation)
  - [uv_seed](#uv_seed)
  - [uv_python_preference](#uv_python_preference)
- [Package installation](#package-installation)
  - [uv_resolution](#uv_resolution)
  <!--te-->

## How to use

Install `tox-uv` into the environment of your tox, and it will replace `virtualenv` and `pip` for all runs:

```bash
uv tool install tox --with tox-uv # use uv to install
tox --version # validate you are using the installed tox
tox r -e py312 # will use uv
tox --runner virtualenv r -e py312 # will use virtualenv+pip
```

## tox environment types provided

This package will provide the following new tox environments:

- `uv-venv-runner` is the ID for the tox environments [runner](https://tox.wiki/en/4.12.1/config.html#runner) for
  environments not using a lock file.
- `uv-venv-lock-runner` is the ID for the tox environments [runner](https://tox.wiki/en/4.12.1/config.html#runner) for
  environments using `uv.lock` (note we can’t detect the presence of the `uv.lock` file to enable this because that
  would break environments not using the lock file - such as your linter).
- `uv-venv-pep-517` is the ID for the PEP-517 packaging environment.
- `uv-venv-cmd-builder` is the ID for the external cmd builder.

## uv.lock support

If you want for a tox environment to use `uv sync` with a `uv.lock` file you need to change for that tox environment the
`runner` to `uv-venv-lock-runner`. Furthermore, should in such environments you use the `extras` config to instruct `uv`
to install the specified extras, for example:

```ini

[testenv:fix]
description = run code formatter and linter (auto-fix)
skip_install = true
deps =
    pre-commit-uv>=4.1.1
commands =
    pre-commit run --all-files --show-diff-on-failure

[testenv:type]
runner = uv-venv-lock-runner
description = run type checker via mypy
commands =
    mypy {posargs:src}

[testenv:dev]
runner = uv-venv-lock-runner
description = dev environment
extras =
    dev
    test
    type
commands =
    uv pip tree
```

In this example:

- `fix` will use the `uv-venv-runner` and use `uv pip install` to install dependencies to the environment.
- `type` will use the `uv-venv-lock-runner` and use `uv sync` to install dependencies to the environment without any
  extra group.
- `dev` will use the `uv-venv-lock-runner` and use `uv sync` to install dependencies to the environment with the `dev`,
  `test` and `type` extra groups.

Note that when using `uv-venv-lock-runner`, _all_ dependencies will come from the lock file, controlled by `extras`.
Therefore, options like `deps` are ignored (and all others
[enumerated here](https://tox.wiki/en/stable/config.html#python-run) as Python run flags).

### `extras`

A list of string that selects, which extra groups you want to install with `uv sync`. By default, it is empty.

### `with_dev`

A boolean flag to toggle installation of the `uv` development dependencies. By default, it is false.

### `dependency_groups`

Specify [PEP 735 – Dependency Groups](https://peps.python.org/pep-0735/) to install.

### `uv_sync_flags`

A list of strings, containing additional flags to pass to uv sync (useful because some flags are not configurable via
environment variables). For example, if you want to install the package in non editable mode and keep extra packages
installed into the environment you can do:

```ini
uv_sync_flags = --no-editable, --inexact
```

### External package support

Should tox be invoked with the [`--installpkg`](https://tox.wiki/en/stable/cli_interface.html#tox-run---installpkg) flag
(the argument **must** be either a wheel or source distribution) the sync operation will run with `--no-install-project`
and `uv pip install` will be used afterward to install the provided package.

## Environment creation

We use `uv venv` to create virtual environments. This process can be configured with the following options:

### `uv_seed`

This flag, set on a tox environment level, controls if the created virtual environment injects `pip`, `setuptools` and
`wheel` into the created virtual environment or not. By default, it is off. You will need to set this if you have a
project that uses the old legacy-editable mode, or your project doesn’t support the `pyproject.toml` powered isolated
build model.

### `uv_python_preference`

This flag, set on a tox environment level, controls how `uv` select the Python interpreter.

By default, `uv` will attempt to use Python versions found on the system and only download managed interpreters when
necessary. However, It is possible to adjust `uv`'s Python version selection preference with the
[python-preference](https://docs.astral.sh/uv/concepts/python-versions/#adjusting-python-version-preferences) option.

### `system_site_packages` (`sitepackages`)

Create virtual environments that also have access to globally installed packages. Note the default value may be
overwritten by the VIRTUALENV_SYSTEM_SITE_PACKAGES environment variable. This flag works the same way as the one from
[tox native virtualenv implementation](https://tox.wiki/en/latest/config.html#system_site_packages).

## Package installation

We use `uv pip` to install packages into the virtual environment. The behavior of this can be configured via the
following options:

### `uv_resolution`

This flag, set on a tox environment level, informs `uv` of the desired [resolution strategy]:

- `highest` - (default) selects the highest version of a package satisfying the constraints.
- `lowest` - install the **lowest** compatible versions for all dependencies, both **direct** and **transitive**.
- `lowest-direct` - opt for the **lowest** compatible versions for all **direct** dependencies, while using the
  **latest** compatible versions for all **transitive** dependencies.

This is an `uv` specific feature that may be used as an alternative to frozen constraints for test environments if the
intention is to validate the lower bounds of your dependencies during test executions.

[resolution strategy]: https://github.com/astral-sh/uv/blob/0.1.20/README.md#resolution-strategy
