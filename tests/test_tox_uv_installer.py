from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from tox.pytest import ToxProjectCreator


def test_uv_install_in_ci_list(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CI", "1")
    project = tox_project({"tox.ini": "[testenv]\ndeps = tomli\npackage=skip"})
    result = project.run()
    result.assert_success()
    report = {i.split("=")[0] for i in result.out.splitlines()[-3][4:].split(",")}
    assert report == {"tomli"}


def test_uv_install_in_ci_seed(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CI", "1")
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\nuv_seed = true"})
    result = project.run()
    result.assert_success()
    report = {i.split("=")[0] for i in result.out.splitlines()[-3][4:].split(",")}
    if sys.version_info >= (3, 12):  # pragma: >=3.12 cover
        assert report == {"pip"}
    else:  # pragma: <3.12 cover
        assert report == {"pip", "setuptools", "wheel"}


def test_uv_install_with_pre(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\ndeps = tomli\npip_pre = true\npackage=skip"})
    result = project.run("-vv")
    result.assert_success()


def test_uv_install_with_pre_custom_install_cmd(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    deps = tomli
    pip_pre = true
    package = skip
    install_command = uv pip install {packages}
    """
    })
    result = project.run("-vv")
    result.assert_success()


def test_uv_install_without_pre_custom_install_cmd(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    deps = tomli
    package = skip
    install_command = uv pip install {packages}
    """
    })
    result = project.run("-vv")
    result.assert_success()


@pytest.mark.parametrize("strategy", ["highest", "lowest", "lowest-direct"])
def test_uv_install_with_resolution_strategy(tox_project: ToxProjectCreator, strategy: str) -> None:
    project = tox_project({"tox.ini": f"[testenv]\ndeps = tomli>=2.0.1\npackage = skip\nuv_resolution = {strategy}"})
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)

    result = project.run("-vv")
    result.assert_success()

    assert execute_calls.call_args[0][3].cmd[2:] == ["install", "--resolution", strategy, "tomli>=2.0.1", "-v"]


def test_uv_install_with_invalid_resolution_strategy(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\ndeps = tomli>=2.0.1\npackage = skip\nuv_resolution = invalid"})

    result = project.run("-vv")
    result.assert_failed(code=1)

    assert "Invalid value for uv_resolution: 'invalid'." in result.out


def test_uv_install_with_resolution_strategy_custom_install_cmd(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    deps = tomli>=2.0.1
    package = skip
    uv_resolution = lowest-direct
    install_command = uv pip install {packages}
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)

    result = project.run("-vv")
    result.assert_success()

    assert execute_calls.call_args[0][3].cmd[2:] == ["install", "tomli>=2.0.1", "--resolution", "lowest-direct"]
