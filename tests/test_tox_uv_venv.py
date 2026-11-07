from __future__ import annotations

import builtins
import importlib.util
import json
import os
import os.path
import pathlib
import platform
import shutil
import subprocess
import sys
import sysconfig
from configparser import ConfigParser
from typing import TYPE_CHECKING, Any, Final, get_args

import pytest
import tox.tox_env.errors
from tox.tox_env.api import ToxEnvCreateArgs
from tox.tox_env.python.api import PythonInfo, VersionInfo
from virtualenv.discovery.py_info import PythonInfo as VirtualenvPythonInfo

from tox_uv._venv import PythonPreference, UvVenv

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from tox.pytest import ToxProjectCreator

_THREADED: Final[str] = "t" if sysconfig.get_config_var("Py_GIL_DISABLED") else ""
_DEBUG: Final[str] = "d" if sysconfig.get_config_var("Py_DEBUG") else ""
_CONFLICTING_IMPLEMENTATION: Final[str] = "pypy" if platform.python_implementation() == "CPython" else "cpython"
_BIN_DIR: Final[str] = "Scripts" if sys.platform == "win32" else "bin"
_PYTHON_EXE: Final[str] = "python.exe" if sys.platform == "win32" else "python"
_EXE_SUFFIX: Final[str] = ".exe" if sys.platform == "win32" else ""


def test_uv_venv_self(tox_project: ToxProjectCreator) -> None:
    tox_project({"tox.ini": "[testenv]\npackage=skip"}).run("-vv").assert_success()


@pytest.mark.parametrize(
    "env_name",
    [pytest.param("doc8", id="doc8"), pytest.param("flake8", id="flake8"), pytest.param("check2", id="check2")],
)
def test_uv_venv_non_python_env_name_with_trailing_digit(tox_project: ToxProjectCreator, env_name: str) -> None:
    project = tox_project({
        "tox.ini": f"[testenv:{env_name}]\nskip_install = true\ncommands = python --version",
    })
    result = project.run("-vve", env_name)
    result.assert_success()
    assert f"-p {env_name}" not in result.out


def test_uv_venv_pass_env(tox_project: ToxProjectCreator) -> None:
    result = tox_project({"tox.ini": "[testenv]\npackage=skip"}).run("c", "-k", "pass_env")
    result.assert_success()

    parser = ConfigParser()
    parser.read_string(result.out)
    pass_through = set(parser["testenv:py"]["pass_env"].splitlines())

    assert "UV_*" in pass_through
    assert "PKG_CONFIG_PATH" in pass_through


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS adds its deployment target to pass_env")
def test_uv_venv_pass_env_macos(tox_project: ToxProjectCreator) -> None:  # pragma: darwin cover
    result = tox_project({"tox.ini": "[testenv]\npackage=skip"}).run("c", "-k", "pass_env")
    result.assert_success()

    parser = ConfigParser()
    parser.read_string(result.out)
    pass_through = set(parser["testenv:py"]["pass_env"].splitlines())

    assert "MACOSX_DEPLOYMENT_TARGET" in pass_through


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_venv_preference_system_by_default(tox_project: ToxProjectCreator) -> None:

    result = tox_project({"tox.ini": "[testenv]"}).run("c", "-k", "uv_python_preference")
    result.assert_success()

    parser = ConfigParser()
    parser.read_string(result.out)
    got = parser["testenv:py"]["uv_python_preference"]

    assert got == "system"


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_venv_preference_empty_falls_back_to_system(tox_project: ToxProjectCreator) -> None:

    result = tox_project({"tox.ini": "[testenv]\nuv_python_preference ="}).run("c", "-k", "uv_python_preference")
    result.assert_success()

    parser = ConfigParser()
    parser.read_string(result.out)
    got = parser["testenv:py"]["uv_python_preference"]

    assert got == "system"


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize(
    "env_var",
    [
        pytest.param("UV_NO_MANAGED_PYTHON", id="UV_NO_MANAGED_PYTHON"),
        pytest.param("UV_MANAGED_PYTHON", id="UV_MANAGED_PYTHON"),
    ],
)
def test_uv_venv_preference_not_set_if_uv_no_managed_python(
    tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch, env_var: str
) -> None:
    # --(no-)managed-python cannot be used together with --python-preference
    project = tox_project({"tox.ini": "[testenv]"})
    monkeypatch.setenv(env_var, "True")

    result = project.run("c", "-k", "uv_python_preference")
    result.assert_success()

    parser = ConfigParser()
    parser.read_string(result.out)
    got = parser["testenv:py"]

    assert got.get("uv_python_preference") == "none"


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
    result = tox_project({"tox.ini": f"[testenv]\npackage=skip\nbase_python={ver.major}.{ver.minor}"}).run("-vv")
    result.assert_success()


def test_uv_venv_spec_major_only(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": f"[testenv]\npackage=skip\nbase_python={sys.version_info.major}"})
    project.run("-vv").assert_success()


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="Bug https://github.com/tox-dev/tox-uv/issues/193 https://github.com/astral-sh/uv/issues/14239",
)
@pytest.mark.parametrize(
    ("pypy", "expected_uv_pypy"),
    [
        pytest.param("pypy", "pypy", id="pypy-pypy"),
        pytest.param("pypy9", "pypy9", id="pypy9-pypy9"),
        pytest.param("pypy999", "pypy9.99", id="pypy999-pypy9.99"),
        pytest.param("pypy9.99", "pypy9.99", id="pypy9.99-pypy9.99"),
    ],
)
def test_uv_venv_spec_pypy(
    capfd: pytest.CaptureFixture[str],
    tox_project: ToxProjectCreator,
    pypy: str,
    expected_uv_pypy: str,
) -> None:
    # Validate that major and minor versions are correctly applied to implementations.
    #
    # This test prevents a regression that occurred when the testenv name was "pypy":
    # the uv runner was asked to use "pypyNone" as the Python version.
    #
    # The test is dependent on what PyPy interpreters are installed on the system;
    # if any PyPy is available then the "pypy" value will not raise a Skip exception,
    # and STDOUT will be captured in `result.out`.
    #
    # However, it is expected that no system will have PyPy v9.x installed,
    # so STDOUT must be read from `capfd` after the Skip exception is caught.
    #
    # Since it is unknown whether any PyPy interpreter will be installed,
    # the `else` block's branch coverage is disabled.
    project = tox_project({"tox.ini": f"[tox]\nenv_list = {pypy}"})
    try:
        result = project.run("config", "-vv")
    except tox.tox_env.errors.Skip:  # pragma: no cover (PyPy might be available on the system)
        stdout, _ = capfd.readouterr()
    else:  # pragma: no cover (PyPy might not be available on the system)
        stdout = result.out
    assert "pypyNone" not in stdout
    assert f"-p {expected_uv_pypy} " in stdout


@pytest.mark.parametrize(
    ("implementation", "expected_implementation", "expected_name"),
    [
        pytest.param("py", "cpython", "cpython", id="py-cpython-cpython"),
        pytest.param("pypy", "pypy", "pypy", id="pypy-pypy-pypy"),
    ],
)
def test_uv_venv_spec_full_implementation(
    tox_project: ToxProjectCreator,
    implementation: str,
    expected_implementation: str,
    expected_name: str,
) -> None:
    # Validate that Python implementations are explicitly passed to uv's `-p` argument.
    #
    # This test ensures that uv searches for the target Python implementation and version,
    # even if another implementation -- with the same language version --
    # is found on the path first.
    #
    # This prevents a regression to a bug that occurred when PyPy 3.10 was on the PATH
    # and tox was invoked with `tox -e py3.10`:
    # uv was invoked with `-p 3.10` and found PyPy 3.10, not CPython 3.10.
    result = tox_project({}).run("run", "-vve", f"{implementation}9.99")

    # Verify that uv was invoked with the full Python implementation and version.
    assert f" -p {expected_implementation}9.99 " in result.out

    # Verify that uv interpreted the `-p` argument as a Python spec, not an executable.
    # This confirms that tox-uv is passing recognizable, usable `-p` arguments to uv.
    assert f"no interpreter found for {expected_name} 9.99" in result.err.lower()


def test_uv_venv_system_site_packages(tox_project: ToxProjectCreator) -> None:
    tox_project({"tox.ini": "[testenv]\npackage=skip\nsystem_site_packages=true"}).run("-vv").assert_success()


@pytest.mark.parametrize(
    ("initial", "updated"),
    [pytest.param("false", "true", id="enable"), pytest.param("true", "false", id="disable")],
)
def test_uv_venv_system_site_packages_change_recreates(
    tox_project: ToxProjectCreator, initial: str, updated: str
) -> None:
    project = tox_project({"tox.ini": f"[testenv]\npackage=skip\nsystem_site_packages={initial}"})

    project.run("r").assert_success()
    (project.path / "tox.ini").write_text(f"[testenv]\npackage=skip\nsystem_site_packages={updated}\n")
    project.run("r").assert_success()

    config = ConfigParser()
    # pyvenv.cfg has no section header, so give it one
    config.read_string(f"[cfg]\n{(project.path / '.tox' / 'py' / 'pyvenv.cfg').read_text()}")

    assert config["cfg"]["include-system-site-packages"].strip() == updated


def test_uv_venv_system_site_packages_env_var(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip"})
    monkeypatch.setenv("VIRTUALENV_SYSTEM_SITE_PACKAGES", "1")

    result = project.run("c", "-k", "system_site_packages")
    result.assert_success()

    parser = ConfigParser()
    parser.read_string(result.out)
    got = parser["testenv:py"]["system_site_packages"]

    assert got == "True"


@pytest.fixture
def other_interpreter_exe() -> (
    pathlib.Path
):  # pragma: no cover the fixture needs a second interpreter; excluded where none is installed
    # Returns an interpreter executable path that is not the exact same as `sys.executable`.
    #
    # Necessary because `sys.executable` gets short-circuited when used as `base_python`.
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
            exe.with_name(f"{exe.stem[:-1]}.exe") if exe.stem.endswith("w") else exe.with_name(f"{exe.stem}w.exe")
        )
    if not base_python or not base_python.is_file():
        pytest.fail("Tried to pick a base_python that is not sys.executable, but failed.")
    return base_python


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="Bug https://github.com/tox-dev/tox-uv/issues/193 https://github.com/astral-sh/uv/issues/14239",
)
def test_uv_venv_spec_abs_path(
    tox_project: ToxProjectCreator, other_interpreter_exe: pathlib.Path
) -> None:  # pragma: win32 no cover
    result = tox_project({"tox.ini": f"[testenv]\npackage=skip\nbase_python={other_interpreter_exe}"}).run("-vv")
    result.assert_success()


@pytest.mark.parametrize(
    "runner",
    [pytest.param("uv-venv-runner", id="venv"), pytest.param("uv-venv-lock-runner", id="lock")],
)
@pytest.mark.parametrize(
    "env_template",
    [
        pytest.param("py{major}{minor}{variant}", id="py"),
        pytest.param("cpython{major}{minor}{variant}", id="cpython"),
        pytest.param("{major}.{minor}{variant}", id="version"),
        pytest.param("py{major}{minor}{variant}-unit", id="factor"),
    ],
)
@pytest.mark.parametrize(
    "configuration",
    [
        pytest.param(
            (
                "tox.ini",
                "[testenv]\npackage=skip\nrunner={runner}\nbase_python={base_python}\n[testenv:{env_name}]\n",
                (),
            ),
            id="ini",
        ),
        pytest.param(
            (
                "tox.toml",
                (
                    "[env_run_base]\npackage = 'skip'\nrunner = '{runner}'\n"
                    "base_python = [{base_python_json}]\n[env.{env_name!r}]\n"
                ),
                (),
            ),
            id="toml",
        ),
        pytest.param(
            (
                "tox.ini",
                "[testenv]\npackage=skip\nrunner={runner}\n[testenv:{env_name}]\n",
                ("-x", "testenv:{env_name}.base_python={base_python}"),
            ),
            id="override",
        ),
    ],
)
def test_uv_venv_explicit_path_in_python_env(
    tox_project: ToxProjectCreator,
    runner: str,
    env_template: str,
    configuration: tuple[str, str, tuple[str, ...]],
) -> None:
    config_file, config_template, override_args = configuration
    executable = pathlib.Path(sys.executable)
    # Tox special-cases the exact sys.executable string.
    base_python = executable.parent / ".." / executable.parent.name / executable.name
    env_name = env_template.format(
        major=sys.version_info.major, minor=sys.version_info.minor, variant=f"{_THREADED}{_DEBUG}"
    )
    config_values = {
        "runner": runner,
        "base_python": str(base_python),
        "base_python_json": json.dumps(str(base_python)),
        "env_name": env_name,
    }
    project = tox_project({config_file: config_template.format(**config_values)})
    result = project.run(
        "c", "-e", env_name, "-k", "base_python", *(arg.format(**config_values) for arg in override_args)
    )
    result.assert_success()
    environment = result.state.envs[env_name]
    assert isinstance(environment, UvVenv)
    assert environment.env_version_spec() == str(base_python)


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="Bug https://github.com/tox-dev/tox-uv/issues/193 https://github.com/astral-sh/uv/issues/14239",
)
def test_uv_venv_spec_abs_path_conflict_ver(
    tox_project: ToxProjectCreator, other_interpreter_exe: pathlib.Path
) -> None:  # pragma: win32 no cover
    # py27 is long gone, but still matches the testenv capture regex, so we know it will fail
    project = tox_project({"tox.ini": f"[testenv:py27]\npackage=skip\nbase_python={other_interpreter_exe}"})
    result = project.run("-vv", "-e", "py27")
    result.assert_failed()
    assert f"failed with env name py27 conflicting with base python {other_interpreter_exe}" in result.out


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="Bug https://github.com/tox-dev/tox-uv/issues/193 https://github.com/astral-sh/uv/issues/14239",
)
def test_uv_venv_spec_abs_path_conflict_impl(
    tox_project: ToxProjectCreator, other_interpreter_exe: pathlib.Path
) -> None:  # pragma: win32 no cover
    env = _CONFLICTING_IMPLEMENTATION
    project = tox_project({"tox.ini": f"[testenv:{env}]\npackage=skip\nbase_python={other_interpreter_exe}"})
    result = project.run("-vv", "-e", env)
    result.assert_failed()
    assert f"failed with env name {env} conflicting with base python {other_interpreter_exe}" in result.out


@pytest.mark.parametrize(
    "env_name",
    [
        pytest.param("control2", id="control2"),
        pytest.param("build3", id="build3"),
        pytest.param("lint", id="lint"),
        pytest.param("myenv", id="myenv"),
    ],
)
def test_uv_venv_non_python_env_name(tox_project: ToxProjectCreator, env_name: str) -> None:
    project = tox_project({
        "tox.ini": f"[testenv:{env_name}]\npackage=skip\nskip_install=true\ncommands=python --version"
    })
    project.run("-vve", env_name).assert_success()


def test_uv_venv_na(tox_project: ToxProjectCreator) -> None:
    # an unavailable interpreter is skipped (exit 1), not a hard error, when skip_missing_interpreters is on
    project = tox_project({
        "tox.ini": "[tox]\nskip_missing_interpreters=true\n[testenv]\npackage=skip\nbase_python=1.0"
    })
    project.run("-vv").assert_failed(code=1)


def test_uv_venv_na_uv_072(tox_project: ToxProjectCreator) -> None:
    # an unavailable interpreter is skipped (exit 1), not a hard error, when skip_missing_interpreters is on
    project = tox_project({
        "tox.ini": "[tox]\nskip_missing_interpreters=true\n[testenv]\npackage=skip\nbase_python=1.0\nrequires=uv==0.7.2"
    })
    project.run("-vv").assert_failed(code=1)


def test_uv_venv_skip_missing_interpreters_fail(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": "[tox]\nskip_missing_interpreters=false\n[testenv]\npackage=skip\nbase_python=1.0"
    })
    project.run("-vv").assert_failed(code=2)


def test_uv_venv_skip_missing_interpreters_pass(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": "[tox]\nskip_missing_interpreters=true\n[testenv]\npackage=skip\nbase_python=1.0"
    })
    project.run("-vv").assert_failed(code=1)


def test_uv_venv_platform_check(tox_project: ToxProjectCreator) -> None:
    tox_project({"tox.ini": f"[testenv]\nplatform={sys.platform}\npackage=skip"}).run("-vv").assert_success()


def test_uv_env_bin_dir(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": "[testenv]\npackage=skip\ncommands=python -c 'import sys; print(sys.argv[1])' \"{env_bin_dir}\""
    })
    result = project.run("-vv")
    result.assert_success()

    env_bin_dir = str(project.path / ".tox" / "py" / _BIN_DIR)
    assert env_bin_dir in result.out


def test_uv_env_has_access_to_plugin_uv(tox_project: ToxProjectCreator) -> None:
    result = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=uv --version"}).run()

    result.assert_success()
    uv_path = shutil.which("uv")
    assert uv_path is not None
    ver = subprocess.run([uv_path, "--version"], capture_output=True, text=True, check=True).stdout.strip().split()[1]
    assert f"uv {ver}" in result.out


def test_uv_env_python(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": "[testenv]\npackage=skip\ncommands=python -c 'import sys; print(sys.argv[1])' \"{env_python}\""
    })
    result = project.run("-vv")
    result.assert_success()

    env_bin_dir = str(project.path / ".tox" / "py" / _BIN_DIR / _PYTHON_EXE)
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
            "commands=python -c 'import sys; print(sys.argv[1])' \"{env_python}\""
        )
    })
    result = project.run("-vv")
    result.assert_success()

    env_bin_dir = str(project.path / ".tox" / "py" / _BIN_DIR / _PYTHON_EXE)
    assert env_bin_dir in result.out


@pytest.mark.parametrize(
    "env",
    [pytest.param("3.10", id="3.10"), pytest.param("3.10-onlymanaged", id="3.10-onlymanaged")],
)
def test_uv_env_python_preference_complex(
    tox_project: ToxProjectCreator,
    *,
    env: str,
) -> None:
    project = tox_project({
        "tox.ini": (
            "[tox]\n"
            "env_list =\n"
            "    3.10\n"
            "[testenv]\n"
            "package=skip\n"
            "uv_python_preference=\n"
            "    onlymanaged: only-managed\n"
            "commands=python -c 'import sys; print(sys.argv[1])' \"{env_python}\""
        )
    })
    result = project.run("-vv", "-e", env)
    result.assert_success()

    env_bin_dir = str(project.path / ".tox" / env / _BIN_DIR / _PYTHON_EXE)
    assert env_bin_dir in result.out


def test_uv_env_site_package_dir_run(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": (
            "[testenv]\npackage=skip\ncommands=python -c 'import sys; print(sys.argv[1])' \"{envsitepackagesdir}\""
        )
    })
    result = project.run("-vv")
    result.assert_success()

    assert str(_expected_site_package_dir(project.path / ".tox" / "py")) in result.out


def _expected_site_package_dir(env_dir: pathlib.Path) -> pathlib.Path:
    if sys.platform != "win32":  # pragma: win32 no cover
        implementation = "pypy" if sys.implementation.name.lower() == "pypy" else "python"
        version_info = sys.version_info
        abi_thread = "t" if sysconfig.get_config_var("Py_GIL_DISABLED") else ""
        return (
            env_dir / "lib" / f"{implementation}{version_info.major}.{version_info.minor}{abi_thread}" / "site-packages"
        )
    return env_dir / "Lib" / "site-packages"  # pragma: win32 cover


def test_uv_env_site_package_dir_conf(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands={envsitepackagesdir}"})
    result = project.run("c", "-e", "py", "-k", "commands")
    result.assert_success()

    assert str(_expected_site_package_dir(project.path / ".tox" / "py")) in result.out


def test_uv_env_python_not_in_path(tox_project: ToxProjectCreator) -> None:
    # Make sure there is no pythonX.Y in the search path
    ver = sys.version_info
    python_exe = f"python{ver.major}.{ver.minor}{_EXE_SUFFIX}"
    uv_path = shutil.which("uv")
    assert uv_path is not None
    uv_dir = str(pathlib.Path(uv_path).parent)
    env = dict(os.environ)
    env["PATH"] = os.path.pathsep.join(
        path
        for path in env["PATH"].split(os.path.pathsep)
        if not (pathlib.Path(path) / python_exe).is_file() or path == uv_dir
    )

    # Make sure the Python interpreter can find our Tox module
    tox_spec = importlib.util.find_spec("tox")
    assert tox_spec is not None
    tox_lines = subprocess.check_output(
        [sys.executable, "-c", "import tox; print(tox.__file__);"], encoding="UTF-8", env=env
    ).splitlines()
    assert tox_lines == [tox_spec.origin]

    # Now use that Python interpreter to run Tox
    project = tox_project({
        "tox.ini": "[testenv]\npackage=skip\ncommands=python -c 'import sys; print(sys.argv[1])' \"{env_python}\""
    })
    tox_ini = project.path / "tox.ini"
    assert tox_ini.is_file()
    subprocess.check_call([sys.executable, "-m", "tox", "-c", tox_ini], env=env)


def test_uv_python_set(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UV_PYTHON", sys.executable)
    project = tox_project({
        "tox.ini": "[testenv]\npackage=skip\ndeps=setuptools\ncommands=python -c 'import setuptools'"
    })
    project.run("-vv").assert_success()


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


def test_get_python_abs_path_with_python_env_name(mocker: MockerFixture) -> None:  # pragma: win32 no cover
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
    mocker.patch.object(type(uv_venv), "name", new_callable=mocker.PropertyMock, return_value="py999")
    python_info = uv_venv.get_python_info(sys.executable)
    assert python_info is not None
    assert (python_info.version_info.major, python_info.version_info.minor) == (9, 99)
    assert python_info.implementation == "CPython"


class _TestUvVenv(UvVenv):
    @staticmethod
    def id() -> str:
        return "uv-venv-test"  # pragma: no cover tox never looks up the id of this test subclass

    def set_base_python(self, python_info: PythonInfo) -> None:
        self._base_python_searched = True
        self._base_python = python_info

    def get_python_info(self, base_python: str) -> PythonInfo | None:
        # These direct probes model an implicit fallback, not configured base_python.
        self._base_python_explicitly_set = False
        return self._get_python([base_python])


def test_get_python_abs_path_variants(mocker: MockerFixture) -> None:
    mocker.patch.object(
        UvVenv,
        "_get_virtualenv_py_info",
        autospec=True,
        return_value=mocker.MagicMock(
            spec=VirtualenvPythonInfo,
            implementation="CPython",
            version_info=VersionInfo(3, 13, 0, "final", 0),
            version="3.13.0",
            architecture=64,
            platform=sys.platform,
            free_threaded=True,
            debug_build=True,
            machine="x86_64",
        ),
    )
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
    mocker.patch.object(type(uv_venv), "name", new_callable=mocker.PropertyMock, return_value="lint")
    python_info = uv_venv.get_python_info(sys.executable)
    assert python_info is not None
    python_spec = uv_venv.python_spec_for_path(pathlib.Path(sys.executable))
    assert ((python_info.free_threaded, python_info.debug), (python_spec.free_threaded, python_spec.debug)) == (
        (True, True),
        (True, True),
    )


@pytest.mark.parametrize(
    ("base_python", "architecture"),
    [
        pytest.param("python3.11", None, id="python3.11-None"),
        pytest.param("python3.11-32", 32, id="python3.11-32-32"),
        pytest.param("python3.11-64", 64, id="python3.11-64-64"),
    ],
)
def test_get_python_architecture(base_python: str, architecture: int | None, mocker: MockerFixture) -> None:
    python_info = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True)).get_python_info(
        base_python
    )
    assert python_info is not None
    assert python_info.extra["architecture"] == architecture


@pytest.mark.parametrize(
    ("base_python", "expected"),
    [
        pytest.param("py313", (False, False), id="regular"),
        pytest.param("py313t", (True, False), id="free-threaded"),
        pytest.param("py313d", (False, True), id="debug"),
        pytest.param("py313td", (True, True), id="free-threaded-debug"),
    ],
)
def test_get_python_variants(base_python: str, expected: tuple[bool, bool], mocker: MockerFixture) -> None:
    python_info = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True)).get_python_info(
        base_python
    )
    assert python_info is not None
    assert (python_info.free_threaded, python_info.debug) == expected


@pytest.mark.parametrize(
    ("env_name", "expected"),
    [
        pytest.param("py313d", "cpython3.13+debug", id="debug"),
        pytest.param("py313td", "cpython3.13+freethreaded+debug", id="free-threaded-debug"),
    ],
)
def test_uv_venv_debug_request(tox_project: ToxProjectCreator, env_name: str, expected: str) -> None:
    project = tox_project({"tox.ini": "[tox]\nskip_missing_interpreters=true\n[testenv]\npackage=skip"})
    execute_calls = project.patch_execute(lambda request: 2 if request.run_id == "venv" else None)

    project.run("r", "-e", env_name).assert_failed(code=1)

    venv_cmd = next(call.args[3].cmd for call in execute_calls.call_args_list if call.args[3].run_id == "venv")
    assert venv_cmd[venv_cmd.index("-p") + 1] == expected


@pytest.mark.parametrize(
    ("env_name", "expected"),
    [
        pytest.param("py313", (False, False), id="regular"),
        pytest.param("py313t", (True, False), id="free-threaded"),
        pytest.param("py313d", (False, True), id="debug"),
        pytest.param("py313td", (True, True), id="free-threaded-debug"),
    ],
)
def test_uv_venv_variant_cache(tox_project: ToxProjectCreator, env_name: str, expected: tuple[bool, bool]) -> None:
    result = tox_project({"tox.ini": "[testenv]\npackage=skip"}).run("c", "-e", env_name, "-k", "base_python")
    result.assert_success()

    environment = result.state.envs[env_name]
    assert isinstance(environment, UvVenv)
    cache = environment.python_cache()
    assert (cache["free_threaded"], cache["debug"], environment.py_debug()) == (*expected, expected[1])


@pytest.mark.parametrize(
    ("env_name", "expected_impl"),
    [
        pytest.param("pypy", "pypy", id="pypy"),
        pytest.param("cpython", "CPython", id="cpython"),
    ],
)
def test_get_python_abs_path_with_impl(env_name: str, expected_impl: str, mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
    mocker.patch.object(type(uv_venv), "name", new_callable=mocker.PropertyMock, return_value=env_name)
    python_info = uv_venv.get_python_info(sys.executable)
    assert python_info is not None
    assert python_info.implementation.lower() == expected_impl.lower()


@pytest.mark.parametrize(
    ("base_python", "expected"),
    [
        pytest.param("python3.13", "cpython3.13", id="no-micro"),
        pytest.param("python3.13.0", "cpython3.13.0", id="zero-micro"),
        pytest.param("python3.13.1", "cpython3.13.1", id="micro"),
        pytest.param("python3.13.1t", "cpython3.13.1+freethreaded", id="micro-free-threaded"),
        pytest.param("python3.13.1d", "cpython3.13.1+debug", id="micro-debug"),
        pytest.param("python3.13.1td", "cpython3.13.1+freethreaded+debug", id="micro-free-threaded-debug"),
        pytest.param("python3.13.1-64", "cpython-3.13.1-windows-x86_64-none", id="micro-architecture"),
        pytest.param(
            "python3.13.1t-64", "cpython-3.13.1+freethreaded-windows-x86_64-none", id="micro-free-threaded-architecture"
        ),
        pytest.param("python3.13.1d-64", "cpython-3.13.1+debug-windows-x86_64-none", id="micro-debug-architecture"),
        pytest.param(
            "python3.13.1td-64",
            "cpython-3.13.1+freethreaded+debug-windows-x86_64-none",
            id="micro-free-threaded-debug-architecture",
        ),
    ],
)
def test_env_version_spec_preserves_requested_micro(base_python: str, expected: str, mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
    mocker.patch("sys.platform", "win32")
    python_info = uv_venv.get_python_info(base_python)
    assert python_info is not None
    uv_venv.set_base_python(python_info)
    assert uv_venv.env_version_spec() == expected


def test_env_version_spec_no_architecture(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    assert uv_venv.env_version_spec() == "cpython3.11"


@pytest.mark.parametrize("architecture", [pytest.param(32, id="32"), pytest.param(64, id="64")])
def test_env_version_spec_architecture_configured(architecture: int, mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
def test_env_version_spec_architecture_configured_overwrite_sys_exe(
    mocker: MockerFixture,
) -> None:  # pragma: win32 cover
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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


def test_env_version_spec_free_threaded(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
    python_info = PythonInfo(
        implementation="cpython",
        version_info=VersionInfo(
            major=3,
            minor=13,
            micro=3,
            releaselevel="",
            serial=0,
        ),
        version="",
        is_64=True,
        platform="win32",
        extra={"architecture": None},
        free_threaded=True,
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    assert uv_venv.env_version_spec() == "cpython3.13+freethreaded"


def test_env_version_spec_machine_none(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="linux",
        extra={"architecture": None},
        machine=None,
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    assert uv_venv.env_version_spec() == "cpython3.11"


def test_env_version_spec_machine_none_with_architecture(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="linux",
        extra={"architecture": 64},
        machine=None,
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    # When machine is None, uv_arch becomes empty and no os/arch/libc suffix is appended
    assert uv_venv.env_version_spec() == "cpython-3.11"


@pytest.mark.parametrize(
    ("machine", "expected_uv_arch"),
    [
        pytest.param("arm64", "aarch64", id="arm64-aarch64"),
        pytest.param("aarch64", "aarch64", id="aarch64-aarch64"),
        pytest.param("amd64", "x86_64", id="amd64-x86_64"),
        pytest.param("x86_64", "x86_64", id="x86_64-x86_64"),
        pytest.param("x86", "i686", id="x86-i686"),
        pytest.param("i386", "i686", id="i386-i686"),
        pytest.param("i686", "i686", id="i686-i686"),
    ],
)
def test_env_version_spec_machine_architecture_mapping(
    machine: str, expected_uv_arch: str, mocker: MockerFixture
) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="linux",
        extra={"architecture": None},
        machine=machine,
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    assert uv_venv.env_version_spec() == f"cpython-3.11-linux-{expected_uv_arch}-gnu"


def test_env_version_spec_machine_x86_64_macos_32bit(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="darwin",
        extra={"architecture": 32},
        machine="x86_64",
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    # On macOS with 32-bit architecture, x86_64 maps to i686
    assert uv_venv.env_version_spec() == "cpython-3.11-macos-i686-none"


def test_env_version_spec_machine_x86_64_macos_64bit(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="darwin",
        extra={"architecture": 64},
        machine="x86_64",
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    # On macOS with 64-bit architecture, x86_64 maps to x86_64
    assert uv_venv.env_version_spec() == "cpython-3.11-macos-x86_64-none"


def test_env_version_spec_machine_x86_64_macos_no_architecture(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="darwin",
        extra={"architecture": None},
        machine="x86_64",
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    # On macOS with no architecture specified, x86_64 maps to x86_64
    assert uv_venv.env_version_spec() == "cpython-3.11-macos-x86_64-none"


def test_env_version_spec_machine_arm64_macos_32bit(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="darwin",
        extra={"architecture": 32},
        machine="arm64",
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    # On macOS, arm64 always maps to aarch64 regardless of architecture setting
    assert uv_venv.env_version_spec() == "cpython-3.11-macos-aarch64-none"


def test_env_version_spec_machine_arm64_macos_64bit(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="darwin",
        extra={"architecture": 64},
        machine="arm64",
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    # On macOS, arm64 always maps to aarch64 regardless of architecture setting
    assert uv_venv.env_version_spec() == "cpython-3.11-macos-aarch64-none"


def test_env_version_spec_machine_arm64_macos_no_architecture(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="darwin",
        extra={"architecture": None},
        machine="arm64",
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))  # prevent picking sys.executable
    # On macOS, arm64 always maps to aarch64 regardless of architecture setting
    assert uv_venv.env_version_spec() == "cpython-3.11-macos-aarch64-none"


def test_env_version_spec_libc_musl_linux(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="linux",
        extra={"architecture": None, "libc": "musl"},
        machine="x86_64",
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))
    assert uv_venv.env_version_spec() == "cpython-3.11-linux-x86_64-musl"


def test_env_version_spec_libc_glibc_linux(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="linux",
        extra={"architecture": None, "libc": "glibc"},
        machine="x86_64",
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))
    assert uv_venv.env_version_spec() == "cpython-3.11-linux-x86_64-gnu"


def test_env_version_spec_libc_windows(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        platform="windows",
        extra={"architecture": None, "libc": "anything"},
        machine="x86_64",
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))
    assert uv_venv.env_version_spec() == "cpython-3.11-windows-x86_64-none"


def test_env_version_spec_machine_x86_windows(mocker: MockerFixture) -> None:
    uv_venv = _TestUvVenv(create_args=mocker.create_autospec(ToxEnvCreateArgs, instance=True))
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
        is_64=False,
        platform="windows",
        extra={"architecture": None},
        machine="x86",
    )
    uv_venv.set_base_python(python_info)
    mocker.patch("sys.version_info", (0, 0, 0))
    assert uv_venv.env_version_spec() == "cpython-3.11-windows-x86-none"


def test_relative_workdir_with_changedir(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """\
[tox]
toxworkdir=.tox

[testenv:demo]
changedir={toxinidir}/sub
package = skip
commands = python -c "print('ok')"
allowlist_externals = python
""",
    })
    (project.path / "sub").mkdir()
    project.run("-e", "demo").assert_success()


def test_uv_path_env_var_invalid(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOX_UV_PATH", "nonexistent_uv_binary")
    project = tox_project({"tox.ini": "[testenv]\npackage=skip"})
    with pytest.raises(RuntimeError, match="TOX_UV_PATH=nonexistent_uv_binary not found in PATH"):
        project.run()


def test_uv_path_env_var_valid(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    uv_path = shutil.which("uv")
    assert uv_path is not None
    monkeypatch.setenv("TOX_UV_PATH", "uv")
    tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python --version"}).run().assert_success()


def test_uv_version_timeout(tox_project: ToxProjectCreator, mocker: MockerFixture) -> None:
    mock_run = mocker.patch("subprocess.run", autospec=True, side_effect=subprocess.TimeoutExpired("uv", 5))
    tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python --version"}).run().assert_success()
    mock_run.assert_called()


def test_uv_version_os_error(tox_project: ToxProjectCreator, mocker: MockerFixture) -> None:
    mock_run = mocker.patch("subprocess.run", autospec=True, side_effect=OSError("mock error"))
    tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python --version"}).run().assert_success()
    mock_run.assert_called()


def test_uv_bundled_import_error(tox_project: ToxProjectCreator, mocker: MockerFixture) -> None:
    original_import = builtins.__import__

    def mock_import(name: str, *args: Any, **kwargs: Any) -> Any:  # ruff:ignore[any-type] the replacement takes the untyped arguments of builtins.__import__
        if name == "uv":
            msg = "mocked import error"
            raise ImportError(msg)
        return original_import(name, *args, **kwargs)

    mocker.patch("builtins.__import__", autospec=True, side_effect=mock_import)
    tox_project({"tox.ini": "[testenv]\npackage=skip\ncommands=python --version"}).run().assert_success()
