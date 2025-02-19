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
from unittest import mock

import pytest
import tox.tox_env.errors
from tox.tox_env.python.api import PythonInfo, VersionInfo

from tox_uv._venv import PythonPreference, UvVenv

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


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_venv_preference_system_by_default(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]"})

    result = project.run("c", "-k", "uv_python_preference")
    result.assert_success()

    parser = ConfigParser()
    parser.read_string(result.out)
    got = parser["testenv:py"]["uv_python_preference"]

    assert got == "system"


def test_uv_venv_preference_override_via_env_var(
    tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tox_project({"tox.ini": "[testenv]"})
    monkeypatch.setenv("UV_PYTHON_PREFERENCE", "only-managed")

    result = project.run("c", "-k", "uv_python_preference")
    result.assert_success()

    parser = ConfigParser()
    parser.read_string(result.out)
    got = parser["testenv:py"]["uv_python_preference"]

    assert got == "only-managed"


def test_uv_venv_preference_override_via_env_var_and_set_env_depends_on_py(
    tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tox_project({"tox.ini": "[testenv]\nset_env=A={env_site_packages_dir}"})
    monkeypatch.setenv("UV_PYTHON_PREFERENCE", "only-managed")

    result = project.run("c", "-k", "set_env")
    result.assert_success()

    assert str(project.path) in result.out


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


@pytest.mark.parametrize(
    ("pypy", "expected_uv_pypy"),
    [
        ("pypy", "pypy"),
        ("pypy9", "pypy9"),
        ("pypy999", "pypy9.99"),
        ("pypy9.99", "pypy9.99"),
    ],
)
def test_uv_venv_spec_pypy(
    capfd: pytest.CaptureFixture[str],
    tox_project: ToxProjectCreator,
    pypy: str,
    expected_uv_pypy: str,
) -> None:
    """Validate that major and minor versions are correctly applied to implementations.

    This test prevents a regression that occurred when the testenv name was "pypy":
    the uv runner was asked to use "pypyNone" as the Python version.

    The test is dependent on what PyPy interpreters are installed on the system;
    if any PyPy is available then the "pypy" value will not raise a Skip exception,
    and STDOUT will be captured in `result.out`.

    However, it is expected that no system will have PyPy v9.x installed,
    so STDOUT must be read from `capfd` after the Skip exception is caught.

    Since it is unknown whether any PyPy interpreter will be installed,
    the `else` block's branch coverage is disabled.
    """

    project = tox_project({"tox.ini": f"[tox]\nenv_list = {pypy}"})
    try:
        result = project.run("config", "-vv")
    except tox.tox_env.errors.Skip:
        stdout, _ = capfd.readouterr()
    else:  # pragma: no cover (PyPy might not be available on the system)
        stdout = result.out
    assert "pypyNone" not in stdout
    assert f"-p {expected_uv_pypy} " in stdout


@pytest.mark.parametrize(
    ("implementation", "expected_implementation", "expected_name"),
    [
        ("", "cpython", "cpython"),
        ("py", "cpython", "cpython"),
        ("pypy", "pypy", "pypy"),
    ],
)
def test_uv_venv_spec_full_implementation(
    tox_project: ToxProjectCreator,
    implementation: str,
    expected_implementation: str,
    expected_name: str,
) -> None:
    """Validate that Python implementations are explicitly passed to uv's `-p` argument.

    This test ensures that uv searches for the target Python implementation and version,
    even if another implementation -- with the same language version --
    is found on the path first.

    This prevents a regression to a bug that occurred when PyPy 3.10 was on the PATH
    and tox was invoked with `tox -e py3.10`:
    uv was invoked with `-p 3.10` and found PyPy 3.10, not CPython 3.10.
    """

    project = tox_project({})
    result = project.run("run", "-vve", f"{implementation}9.99")

    # Verify that uv was invoked with the full Python implementation and version.
    assert f" -p {expected_implementation}9.99 " in result.out

    # Verify that uv interpreted the `-p` argument as a Python spec, not an executable.
    # This confirms that tox-uv is passing recognizable, usable `-p` arguments to uv.
    assert f"no interpreter found for {expected_name} 9.99" in result.err.lower()


def test_uv_venv_system_site_packages(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\nsystem_site_packages=true"})
    result = project.run("-vv")
    result.assert_success()


@pytest.fixture
def other_interpreter_exe() -> pathlib.Path:  # pragma: no cover
    """Returns an interpreter executable path that is not the exact same as `sys.executable`.

    Necessary because `sys.executable` gets short-circuited when used as `base_python`."""

    exe = pathlib.Path(sys.executable)
    base_python: pathlib.Path | None = None
    if exe.name in {"python", "python3"}:
        # python -> pythonX.Y
        ver = sys.version_info
        base_python = exe.with_name(f"python{ver.major}.{ver.minor}")
    elif exe.name[-1].isdigit():
        # python X.Y -> python
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


def test_uv_pip_constraints(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": f"""
            [testenv]
            package=skip
            setenv=
                PIP_CONSTRAINTS={os.devnull}
            commands=python --version
            """
    })
    result = project.run()
    result.assert_success()
    assert (
        result.out.count(
            "Found PIP_CONSTRAINTS defined, you may want to also define UV_CONSTRAINT to match pip behavior."
        )
        == 1
    ), "Warning should be found once and only once in output."


def test_uv_pip_constraints_no(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": f"""
            [testenv]
            package=skip
            setenv=
                PIP_CONSTRAINTS={os.devnull}
                UV_CONSTRAINT={os.devnull}
            commands=python --version
            """
    })
    result = project.run()
    result.assert_success()
    assert (
        "Found PIP_CONSTRAINTS defined, you may want to also define UV_CONSTRAINT to match pip behavior."
        not in result.out
    )


class _TestUvVenv(UvVenv):
    @staticmethod
    def id() -> str:
        return "uv-venv-test"  # pragma: no cover

    def set_base_python(self, python_info: PythonInfo) -> None:
        self._base_python_searched = True
        self._base_python = python_info

    def get_python_info(self, base_python: str) -> PythonInfo | None:
        return self._get_python([base_python])


@pytest.mark.parametrize(
    ("base_python", "architecture"), [("python3.11", None), ("python3.11-32", 32), ("python3.11-64", 64)]
)
def test_get_python_architecture(base_python: str, architecture: int | None) -> None:
    uv_venv = _TestUvVenv(create_args=mock.Mock())
    python_info = uv_venv.get_python_info(base_python)
    assert python_info is not None
    assert python_info.extra["architecture"] == architecture


def test_env_version_spec_no_architecture() -> None:
    uv_venv = _TestUvVenv(create_args=mock.MagicMock())
    python_info = PythonInfo(
        implementation="cpython",
        version_info=VersionInfo(
            major=3,
            minor=11,
            micro=9,
            releaselevel="",
            serial=0,
        ),
        version="",
        is_64=True,
        platform="win32",
        extra={"architecture": None},
    )
    uv_venv.set_base_python(python_info)
    with mock.patch("sys.version_info", (0, 0, 0)):  # prevent picking sys.executable
        assert uv_venv.env_version_spec() == "cpython3.11"


@pytest.mark.parametrize("architecture", [32, 64])
def test_env_version_spec_architecture_configured(architecture: int) -> None:
    uv_venv = _TestUvVenv(create_args=mock.MagicMock())
    python_info = PythonInfo(
        implementation="cpython",
        version_info=VersionInfo(
            major=3,
            minor=11,
            micro=9,
            releaselevel="",
            serial=0,
        ),
        version="",
        is_64=architecture == 64,
        platform="win32",
        extra={"architecture": architecture},
    )
    uv_venv.set_base_python(python_info)
    uv_arch = {32: "x86", 64: "x86_64"}[architecture]
    assert uv_venv.env_version_spec() == f"cpython-3.11-windows-{uv_arch}-none"


@pytest.mark.skipif(sys.platform != "win32", reason="architecture configuration only on Windows")
def test_env_version_spec_architecture_configured_overwrite_sys_exe() -> None:  # pragma: win32 cover
    uv_venv = _TestUvVenv(create_args=mock.MagicMock())
    (major, minor) = sys.version_info[:2]
    python_info = PythonInfo(
        implementation="cpython",
        version_info=VersionInfo(
            major=major,
            minor=minor,
            micro=0,
            releaselevel="",
            serial=0,
        ),
        version="",
        is_64=False,
        platform="win32",
        extra={"architecture": 32},
    )
    uv_venv.set_base_python(python_info)
    assert uv_venv.env_version_spec() == f"cpython-{major}.{minor}-windows-x86-none"
