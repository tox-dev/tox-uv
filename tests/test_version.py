from __future__ import annotations

import sys
from subprocess import check_output
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


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


def test_plugin_version_info_with_uv_package(mocker: MockerFixture) -> None:
    from tox_uv.plugin import tox_append_version_info  # noqa: PLC0415

    mocker.patch("tox_uv.plugin.version", return_value="0.10.5")
    result = tox_append_version_info()
    assert result == "with uv==0.10.5"
