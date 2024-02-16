from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tox.pytest import ToxProjectCreator


def test_uv_venv_self(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip"})
    result = project.run("-vv")
    result.assert_success()


def test_uv_venv_spec(tox_project: ToxProjectCreator) -> None:
    ver = sys.version_info
    project = tox_project({"tox.ini": f"[testenv]\npackage=skip\nbase_python={ver.major}.{ver.minor}"})
    result = project.run("-vv")
    result.assert_success()


def test_uv_venv_na(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\nbase_python=1.0"})
    result = project.run("-vv")
    result.assert_failed(code=1)


def test_uv_venv_platform_check(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": f"[testenv]\nplatform={sys.platform}\npackage=skip"})
    result = project.run("-vv")
    result.assert_success()


def test_uv_env_bin_dir(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python -c 'print(\"{env_bin_dir}\")'"})
    result = project.run("-vv")
    result.assert_success()

    env_bin_dir = str(project.path / ".tox" / "py" / ".venv" / ("Scripts" if sys.platform == "win32" else "bin"))
    assert env_bin_dir in result.out


def test_uv_env_python(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python -c 'print(\"{env_python}\")'"})
    result = project.run("-vv")
    result.assert_success()

    exe = "python.exe" if sys.platform == "win32" else "python"
    env_bin_dir = str(project.path / ".tox" / "py" / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / exe)
    assert env_bin_dir in result.out


def test_uv_env_site_package_dir(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python -c 'print(\"{envsitepackagesdir}\")'"})
    result = project.run("-vv")
    result.assert_success()

    env_dir = project.path / ".tox" / "py" / ".venv"
    ver = sys.version_info
    if sys.platform == "win32":  # pragma: win32 cover
        path = str(env_dir / "Lib" / "site-packages")
    else:  # pragma: win32 no cover
        path = str(env_dir / "lib" / f"python{ver.major}.{ver.minor}" / "site-packages")
    assert path in result.out
