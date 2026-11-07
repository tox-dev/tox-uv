from __future__ import annotations

import sys
from subprocess import check_output
from typing import TYPE_CHECKING

from tox_uv import __version__
from tox_uv.plugin import tox_append_version_info

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_version() -> None:
    assert __version__


def test_tox_version() -> None:
    output = check_output([sys.executable, "-m", "tox", "--version"], text=True)
    assert "tox-uv" in output


def test_plugin_version_info_without_uv_package() -> None:

    result = tox_append_version_info()
    assert not result


def test_plugin_version_info_with_uv_package(mocker: MockerFixture) -> None:

    mocker.patch("tox_uv.plugin.version", autospec=True, return_value="0.10.5")
    result = tox_append_version_info()
    assert result == "with uv==0.10.5"
