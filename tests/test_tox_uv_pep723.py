from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from tox.tox_env.register import ToxEnvRegister

from tox_uv._run_pep723 import UvVenvPep723Runner
from tox_uv.plugin import tox_register_tox_env

if TYPE_CHECKING:
    from tox.pytest import ToxProjectCreator

_PY_VER = f"{sys.version_info.major}.{sys.version_info.minor}"

_SCRIPT_WITH_DEPS = dedent("""\
    # /// script
    # dependencies = ["setuptools"]
    # ///
    print('ok')
""")

_SCRIPT_REQUIRES_PYTHON = dedent(f"""\
    # /// script
    # requires-python = ">={_PY_VER}"
    # ///
    print("ok")
""")

_SCRIPT_BARE = 'print("ok")\n'


def _tox_ini(runner: str = "uv-venv-pep-723", extra: str = "") -> str:
    lines = ["[testenv:check]", f"runner = {runner}", "script = check.py"]
    if extra:
        lines.append(extra)
    return "\n".join(lines) + "\n"


def _run(project: ToxProjectCreator, files: dict[str, str], *extra_args: str) -> tuple:
    proj = project(files)
    execute_calls = proj.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = proj.run("r", "-e", "check", "--discover", sys.executable, *extra_args)
    return result, execute_calls


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_deps_installed(tox_project: ToxProjectCreator) -> None:
    result, execute_calls = _run(tox_project, {"tox.ini": _tox_ini(), "check.py": _SCRIPT_WITH_DEPS})
    result.assert_success()
    install_cmds = [i[0][3].cmd for i in execute_calls.call_args_list if "install" in i[0][3].run_id]
    assert any("setuptools" in arg for cmd in install_cmds for arg in cmd)


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize(
    ("script", "test_id"),
    [
        pytest.param(_SCRIPT_REQUIRES_PYTHON, "only-requires-python", id="only-requires-python"),
        pytest.param(_SCRIPT_BARE, "no-metadata", id="no-metadata"),
    ],
)
def test_no_deps_installed(tox_project: ToxProjectCreator, script: str, test_id: str) -> None:  # noqa: ARG001
    result, execute_calls = _run(tox_project, {"tox.ini": _tox_ini(), "check.py": script})
    result.assert_success()
    assert not [i for i in execute_calls.call_args_list if "install" in i[0][3].run_id]


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_custom_commands_override(tox_project: ToxProjectCreator) -> None:
    result, execute_calls = _run(
        tox_project,
        {"tox.ini": _tox_ini(extra="commands = python -c \"print('custom')\""), "check.py": _SCRIPT_WITH_DEPS},
    )
    result.assert_success()
    cmd_calls = [i[0][3].cmd for i in execute_calls.call_args_list if i[0][3].run_id == "commands[0]"]
    assert any("custom" in str(cmd) for cmd in cmd_calls)


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_default_commands_forward_posargs(tox_project: ToxProjectCreator) -> None:
    result, execute_calls = _run(tox_project, {"tox.ini": _tox_ini(), "check.py": _SCRIPT_BARE}, "--", "arg1", "arg2")
    result.assert_success()
    cmd = next(i[0][3].cmd for i in execute_calls.call_args_list if i[0][3].run_id == "commands[0]")
    assert "arg1" in cmd
    assert "arg2" in cmd


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_requires_python_satisfied(tox_project: ToxProjectCreator) -> None:
    result, _ = _run(tox_project, {"tox.ini": _tox_ini(), "check.py": _SCRIPT_REQUIRES_PYTHON})
    result.assert_success()


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_requires_python_not_satisfied(tox_project: ToxProjectCreator) -> None:
    script = dedent("""\
        # /// script
        # requires-python = ">=99.0"
        # ///
        print("ok")
    """)
    result, _ = _run(tox_project, {"tox.ini": _tox_ini(), "check.py": script})
    result.assert_failed()
    assert "does not satisfy requires-python" in result.out


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_skip_env_install(tox_project: ToxProjectCreator) -> None:
    result, execute_calls = _run(
        tox_project, {"tox.ini": _tox_ini(), "check.py": _SCRIPT_WITH_DEPS}, "--skip-env-install"
    )
    result.assert_success()
    assert not [i for i in execute_calls.call_args_list if "install" in i[0][3].run_id]


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_missing_script_file(tox_project: ToxProjectCreator) -> None:
    result, _ = _run(tox_project, {"tox.ini": _tox_ini()})
    result.assert_failed()
    assert "script file not found" in result.out


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_base_python_rejected(tox_project: ToxProjectCreator) -> None:
    result, _ = _run(
        tox_project,
        {"tox.ini": _tox_ini(extra="base_python = python3"), "check.py": _SCRIPT_REQUIRES_PYTHON},
    )
    result.assert_failed()
    assert "cannot set base_python" in result.out


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize(
    "runner",
    [
        pytest.param("uv-venv-pep-723", id="explicit"),
        pytest.param("virtualenv-pep-723", id="promoted"),
    ],
)
def test_uses_uv_venv(tox_project: ToxProjectCreator, runner: str) -> None:
    result, execute_calls = _run(
        tox_project, {"tox.ini": _tox_ini(runner=runner), "check.py": _SCRIPT_WITH_DEPS}, "-vv"
    )
    result.assert_success()
    venv_calls = [i[0][3].cmd for i in execute_calls.call_args_list if i[0][3].run_id == "venv"]
    assert venv_calls
    assert Path(venv_calls[0][0]).stem == "uv"
    assert venv_calls[0][1] == "venv"


@pytest.mark.parametrize(
    ("env_val", "promoted"),
    [
        pytest.param(None, True, id="default"),
        pytest.param("1", False, id="disabled"),
    ],
)
def test_pep723_promotion_env_var(monkeypatch: pytest.MonkeyPatch, env_val: str | None, promoted: bool) -> None:
    if env_val is None:
        monkeypatch.delenv("TOX_UV_NO_PEP723", raising=False)
    else:
        monkeypatch.setenv("TOX_UV_NO_PEP723", env_val)
    register = ToxEnvRegister()
    tox_register_tox_env(register)
    assert register._run_envs["uv-venv-pep-723"] is UvVenvPep723Runner  # noqa: SLF001
    if promoted:
        assert register._run_envs["virtualenv-pep-723"] is UvVenvPep723Runner  # noqa: SLF001
    else:
        assert register._run_envs.get("virtualenv-pep-723") is None  # noqa: SLF001
