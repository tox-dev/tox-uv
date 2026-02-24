from __future__ import annotations

import sys
from subprocess import check_output


def test_version() -> None:
    from tox_uv import __version__  # noqa: PLC0415

    assert __version__


def test_tox_version() -> None:
    output = check_output([sys.executable, "-m", "tox", "--version"], text=True)
    assert "tox-uv" in output


def test_plugin_version_info_without_uv_package() -> None:
    from tox_uv.plugin import tox_append_version_info  # noqa: PLC0415

    result = tox_append_version_info()
    assert not result
