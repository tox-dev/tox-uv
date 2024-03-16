from __future__ import annotations

import importlib.util
import os
import os.path
import pathlib
import subprocess  # noqa: S404
import sys
from configparser import ConfigParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tox.pytest import ToxProjectCreator


def test_uv_venv_self(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip"})
    result = project.run("-vv")
    result.assert_success()


def test_uv_venv_pass_env(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip"})
    result = project.run("c", "-k", "pass_env")
    result.assert_success()

    parser = ConfigParser()
    parser.read_string(result.out)
    pass_through = set(parser["testenv:py"]["pass_env"].splitlines())

    if sys.platform == "darwin":  # pragma: darwin cover
        assert "MACOSX_DEPLOYMENT_TARGET" in pass_through
    assert "UV_*" in pass_through
    assert "PKG_CONFIG_PATH" in pass_through


def test_uv_venv_spec(tox_project: ToxProjectCreator) -> None:
    ver = sys.version_info
    project = tox_project({"tox.ini": f"[testenv]\npackage=skip\nbase_python={ver.major}.{ver.minor}"})
    result = project.run("-vv")
    result.assert_success()


def test_uv_venv_spec_major_only(tox_project: ToxProjectCreator) -> None:
    ver = sys.version_info
    project = tox_project({"tox.ini": f"[testenv]\npackage=skip\nbase_python={ver.major}"})
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


def test_uv_env_python_not_in_path(tox_project: ToxProjectCreator) -> None:
    # Make sure there is no pythonX.Y in the search path
    ver = sys.version_info
    exe_ext = ".exe" if sys.platform == "win32" else ""
    python_exe = f"python{ver.major}.{ver.minor}{exe_ext}"
    env = dict(os.environ)
    env["PATH"] = os.path.pathsep.join(
        path for path in env["PATH"].split(os.path.pathsep) if not (pathlib.Path(path) / python_exe).is_file()
    )

    # Make sure the Python interpreter can find our Tox module
    tox_spec = importlib.util.find_spec("tox")
    assert tox_spec is not None
    tox_lines = subprocess.check_output(
        [sys.executable, "-c", "import tox; print(tox.__file__);"], encoding="UTF-8", env=env
    ).splitlines()
    assert tox_lines == [tox_spec.origin]

    # Now use that Python interpreter to run Tox
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python -c 'print(\"{env_python}\")'"})
    tox_ini = project.path / "tox.ini"
    assert tox_ini.is_file()
    subprocess.check_call([sys.executable, "-m", "tox", "-c", tox_ini], env=env)
