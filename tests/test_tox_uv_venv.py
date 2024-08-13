from __future__ import annotations

import importlib.util
import os
import os.path
import pathlib
import platform
import subprocess
import sys
from configparser import ConfigParser
from importlib.metadata import version
from typing import TYPE_CHECKING, get_args

import pytest

from tox_uv._venv import PythonPreference

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


@pytest.fixture
def other_interpreter_exe() -> pathlib.Path:  # pragma: no cover
    """Returns an interpreter executable path that is not the exact same as `sys.executable`.

    Necessary because `sys.executable` gets short-circuited when used as `base_python`."""

    exe = pathlib.Path(sys.executable)
    base_python: pathlib.Path | None = None
    if exe.name == "python":
        # python -> pythonX.Y
        ver = sys.version_info
        base_python = exe.with_name(f"python{ver.major}.{ver.minor}")
    elif exe.name[-1].isdigit():
        # python X[.Y] -> python
        base_python = exe.with_name(exe.stem[:-1])
    elif exe.suffix == ".exe":
        # python.exe <-> pythonw.exe
        base_python = (
            exe.with_name(exe.stem[:-1] + ".exe") if exe.stem.endswith("w") else exe.with_name(exe.stem + "w.exe")
        )
    if not base_python or not base_python.is_file():
        pytest.fail("Tried to pick a base_python that is not sys.executable, but failed.")
    return base_python


def test_uv_venv_spec_abs_path(tox_project: ToxProjectCreator, other_interpreter_exe: pathlib.Path) -> None:
    project = tox_project({"tox.ini": f"[testenv]\npackage=skip\nbase_python={other_interpreter_exe}"})
    result = project.run("-vv")
    result.assert_success()


def test_uv_venv_spec_abs_path_conflict_ver(
    tox_project: ToxProjectCreator, other_interpreter_exe: pathlib.Path
) -> None:
    # py27 is long gone, but still matches the testenv capture regex, so we know it will fail
    project = tox_project({"tox.ini": f"[testenv:py27]\npackage=skip\nbase_python={other_interpreter_exe}"})
    result = project.run("-vv", "-e", "py27")
    result.assert_failed()
    assert f"failed with env name py27 conflicting with base python {other_interpreter_exe}" in result.out


def test_uv_venv_spec_abs_path_conflict_impl(
    tox_project: ToxProjectCreator, other_interpreter_exe: pathlib.Path
) -> None:
    env = "pypy" if platform.python_implementation() == "CPython" else "cpython"
    project = tox_project({"tox.ini": f"[testenv:{env}]\npackage=skip\nbase_python={other_interpreter_exe}"})
    result = project.run("-vv", "-e", env)
    result.assert_failed()
    assert f"failed with env name {env} conflicting with base python {other_interpreter_exe}" in result.out


def test_uv_venv_na(tox_project: ToxProjectCreator) -> None:
    # skip_missing_interpreters is true by default
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\nbase_python=1.0"})
    result = project.run("-vv")

    # When a Python interpreter is missing in a pytest environment, project.run
    # return code is equal to -1
    result.assert_failed(code=-1)


def test_uv_venv_skip_missing_interpreters_fail(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": "[tox]\nskip_missing_interpreters=false\n[testenv]\npackage=skip\nbase_python=1.0"
    })
    result = project.run("-vv")
    result.assert_failed(code=1)


def test_uv_venv_skip_missing_interpreters_pass(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": "[tox]\nskip_missing_interpreters=true\n[testenv]\npackage=skip\nbase_python=1.0"
    })
    result = project.run("-vv")
    # When a Python interpreter is missing in a pytest environment, project.run
    # return code is equal to -1
    result.assert_failed(code=-1)


def test_uv_venv_platform_check(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": f"[testenv]\nplatform={sys.platform}\npackage=skip"})
    result = project.run("-vv")
    result.assert_success()


def test_uv_env_bin_dir(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python -c 'print(\"{env_bin_dir}\")'"})
    result = project.run("-vv")
    result.assert_success()

    env_bin_dir = str(project.path / ".tox" / "py" / ("Scripts" if sys.platform == "win32" else "bin"))
    assert env_bin_dir in result.out


def test_uv_env_has_access_to_plugin_uv(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=uv --version"})
    result = project.run()

    result.assert_success()
    ver = version("uv")
    assert f"uv {ver}" in result.out


def test_uv_env_python(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python -c 'print(\"{env_python}\")'"})
    result = project.run("-vv")
    result.assert_success()

    exe = "python.exe" if sys.platform == "win32" else "python"
    env_bin_dir = str(project.path / ".tox" / "py" / ("Scripts" if sys.platform == "win32" else "bin") / exe)
    assert env_bin_dir in result.out


@pytest.mark.parametrize(
    "preference",
    get_args(PythonPreference),
)
def test_uv_env_python_preference(
    tox_project: ToxProjectCreator,
    *,
    preference: str,
) -> None:
    project = tox_project({
        "tox.ini": (
            "[testenv]\n"
            "package=skip\n"
            f"uv_python_preference={preference}\n"
            "commands=python -c 'print(\"{env_python}\")'"
        )
    })
    result = project.run("-vv")
    result.assert_success()

    exe = "python.exe" if sys.platform == "win32" else "python"
    env_bin_dir = str(project.path / ".tox" / "py" / ("Scripts" if sys.platform == "win32" else "bin") / exe)
    assert env_bin_dir in result.out


def test_uv_env_site_package_dir_run(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python -c 'print(\"{envsitepackagesdir}\")'"})
    result = project.run("-vv")
    result.assert_success()

    env_dir = project.path / ".tox" / "py"
    ver = sys.version_info
    if sys.platform == "win32":  # pragma: win32 cover
        path = str(env_dir / "Lib" / "site-packages")
    else:  # pragma: win32 no cover
        impl = "pypy" if sys.implementation.name.lower() == "pypy" else "python"
        path = str(env_dir / "lib" / f"{impl}{ver.major}.{ver.minor}" / "site-packages")
    assert path in result.out


def test_uv_env_site_package_dir_conf(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands={envsitepackagesdir}"})
    result = project.run("c", "-e", "py", "-k", "commands")
    result.assert_success()

    env_dir = project.path / ".tox" / "py"
    ver = sys.version_info
    if sys.platform == "win32":  # pragma: win32 cover
        path = str(env_dir / "Lib" / "site-packages")
    else:  # pragma: win32 no cover
        impl = "pypy" if sys.implementation.name.lower() == "pypy" else "python"
        path = str(env_dir / "lib" / f"{impl}{ver.major}.{ver.minor}" / "site-packages")
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


def test_uv_python_set(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UV_PYTHON", sys.executable)
    project = tox_project({
        "tox.ini": "[testenv]\npackage=skip\ndeps=setuptools\ncommands=python -c 'import setuptools'"
    })
    result = project.run("-vv")
    result.assert_success()
