from __future__ import annotations

import sys
from subprocess import check_output


def test_version() -> None:
    from tox_uv import __version__  # noqa: PLC0415

    assert __version__


def test_tox_version() -> None:
    output = check_output([sys.executable, "-m", "tox", "--version"], text=True)
    assert " with uv==" in output
