from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from tox.tox_env.register import ToxEnvRegister

from tox_uv._run_pep723 import UvVenvPep723Runner
from tox_uv.plugin import tox_register_tox_env

if TYPE_CHECKING:
    from tox.pytest import ToxProjectCreator


def _tox_ini(extra: str = "") -> str:
    lines = ["[testenv:check]", "runner = uv-venv-pep-723", "script = check.py"]
    if extra:
        lines.append(extra)
    return "\n".join(lines) + "\n"


def _py_ver() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}"


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_deps_installed(tox_project: ToxProjectCreator) -> None:
    script = "# /// script\n# dependencies = [\"setuptools\"]\n# ///\nprint('ok')\n"
    project = tox_project({"tox.ini": _tox_ini(), "check.py": script})
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable)
    result.assert_success()
    install_cmds = [i[0][3].cmd for i in execute_calls.call_args_list if "install" in i[0][3].run_id]
    assert any("setuptools" in arg for cmd in install_cmds for arg in cmd)


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_no_deps_when_only_requires_python(tox_project: ToxProjectCreator) -> None:
    script = f'# /// script\n# requires-python = ">={_py_ver()}"\n# ///\nprint("ok")\n'
    project = tox_project({"tox.ini": _tox_ini(), "check.py": script})
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable)
    result.assert_success()
    assert not [i for i in execute_calls.call_args_list if "install" in i[0][3].run_id]


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_no_deps_when_no_metadata(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": _tox_ini(), "check.py": 'print("ok")\n'})
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable)
    result.assert_success()
    assert not [i for i in execute_calls.call_args_list if "install" in i[0][3].run_id]


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_custom_commands_override(tox_project: ToxProjectCreator) -> None:
    script = "# /// script\n# dependencies = [\"setuptools\"]\n# ///\nprint('ok')\n"
    project = tox_project({
        "tox.ini": _tox_ini("commands = python -c \"print('custom')\""),
        "check.py": script,
    })
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable)
    result.assert_success()
    cmd_calls = [i[0][3].cmd for i in execute_calls.call_args_list if i[0][3].run_id == "commands[0]"]
    assert any("custom" in str(cmd) for cmd in cmd_calls)


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_default_commands_forward_posargs(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": _tox_ini(), "check.py": 'print("ok")\n'})
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable, "--", "arg1", "arg2")
    result.assert_success()
    cmd = next(i[0][3].cmd for i in execute_calls.call_args_list if i[0][3].run_id == "commands[0]")
    assert "arg1" in cmd
    assert "arg2" in cmd


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_requires_python_satisfied(tox_project: ToxProjectCreator) -> None:
    script = f'# /// script\n# requires-python = ">={_py_ver()}"\n# ///\nprint("ok")\n'
    project = tox_project({"tox.ini": _tox_ini(), "check.py": script})
    project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable)
    result.assert_success()


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_requires_python_not_satisfied(tox_project: ToxProjectCreator) -> None:
    script = '# /// script\n# requires-python = ">=99.0"\n# ///\nprint("ok")\n'
    project = tox_project({"tox.ini": _tox_ini(), "check.py": script})
    project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable)
    result.assert_failed()
    assert "does not satisfy requires-python" in result.out


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_skip_env_install(tox_project: ToxProjectCreator) -> None:
    script = "# /// script\n# dependencies = [\"setuptools\"]\n# ///\nprint('ok')\n"
    project = tox_project({"tox.ini": _tox_ini(), "check.py": script})
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable, "--skip-env-install")
    result.assert_success()
    assert not [i for i in execute_calls.call_args_list if "install" in i[0][3].run_id]


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_missing_script_file(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": _tox_ini()})
    project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable)
    result.assert_failed()
    assert "script file not found" in result.out


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_base_python_rejected(tox_project: ToxProjectCreator) -> None:
    script = f'# /// script\n# requires-python = ">={_py_ver()}"\n# ///\n'
    project = tox_project({"tox.ini": _tox_ini("base_python = python3"), "check.py": script})
    project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable)
    result.assert_failed()
    assert "cannot set base_python" in result.out


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_virtualenv_pep723_promoted_to_uv(tox_project: ToxProjectCreator) -> None:
    script = "# /// script\n# dependencies = [\"setuptools\"]\n# ///\nprint('ok')\n"
    ini = "[testenv:check]\nrunner = virtualenv-pep-723\nscript = check.py\n"
    project = tox_project({"tox.ini": ini, "check.py": script})
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable, "-vv")
    result.assert_success()
    venv_calls = [i[0][3].cmd for i in execute_calls.call_args_list if i[0][3].run_id == "venv"]
    assert venv_calls
    assert Path(venv_calls[0][0]).stem == "uv"
    assert venv_calls[0][1] == "venv"


def test_no_pep723_promotion_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TOX_UV_NO_PEP723", "1")
    register = ToxEnvRegister()
    tox_register_tox_env(register)
    assert register._run_envs["uv-venv-pep-723"] is UvVenvPep723Runner  # noqa: SLF001
    assert register._run_envs.get("virtualenv-pep-723") is None  # noqa: SLF001


def test_pep723_promotion_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TOX_UV_NO_PEP723", raising=False)
    register = ToxEnvRegister()
    tox_register_tox_env(register)
    assert register._run_envs["uv-venv-pep-723"] is UvVenvPep723Runner  # noqa: SLF001
    assert register._run_envs["virtualenv-pep-723"] is UvVenvPep723Runner  # noqa: SLF001


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uses_uv_venv(tox_project: ToxProjectCreator) -> None:
    script = "# /// script\n# dependencies = [\"setuptools\"]\n# ///\nprint('ok')\n"
    project = tox_project({"tox.ini": _tox_ini(), "check.py": script})
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("r", "-e", "check", "--discover", sys.executable, "-vv")
    result.assert_success()
    venv_calls = [i[0][3].cmd for i in execute_calls.call_args_list if i[0][3].run_id == "venv"]
    assert venv_calls
    assert Path(venv_calls[0][0]).stem == "uv"
    assert venv_calls[0][1] == "venv"
