from __future__ import annotations

import shutil
import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from tox.pytest import ToxProjectCreator


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_lock_with_setupdir(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """\
[testenv]
runner = uv-venv-lock-runner
package_root = src
""",
    })
    (project.path / "src").mkdir()
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run("run", "--notest", "-vv").assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "-v",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--directory",
                str(project.path / "src"),
                "--locked",
                "--python-preference",
                "system",
                "-v",
                "-p",
                sys.executable,
            ],
        ),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_lock_list_dependencies_command(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    extras =
        type
        dev
    commands = python hello
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run("--list-dependencies", "-vv").assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "-v",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--extra",
                "dev",
                "--extra",
                "type",
                "-v",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "freeze", [uv, "--color", "never", "pip", "freeze"]),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize(
    ("cli_args", "v_args"),
    [
        pytest.param([], [], id="default"),
        pytest.param(["-v"], [], id="v"),
        pytest.param(["-vv"], ["-v"], id="vv"),
        pytest.param(["-vvv"], ["-v"], id="vvv"),
    ],
)
def test_uv_lock_command(tox_project: ToxProjectCreator, cli_args: list[str], v_args: list[str]) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    extras =
        type
        dev
    commands = python hello
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run(*cli_args).assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                *v_args,
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--extra",
                "dev",
                "--extra",
                "type",
                *v_args,
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected
    show_uv_output = execute_calls.call_args_list[1].args[4]
    assert show_uv_output is bool(cli_args)


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_lock_with_default_groups(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    no_default_groups = False
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run("-vv").assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "-v",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        ("py", "uv-sync", [uv, "sync", "--locked", "--python-preference", "system", "-v", "-p", sys.executable]),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize(
    "name",
    [
        pytest.param("tox_uv-1.12.2-py3-none-any.whl", id="tox_uv-1.12.2-py3-none-any.whl"),
        pytest.param("tox_uv-1.12.2.tar.gz", id="tox_uv-1.12.2.tar.gz"),
    ],
)
def test_uv_lock_with_install_pkg(tox_project: ToxProjectCreator, name: str) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    wheel = project.path / name
    wheel.write_text("")
    project.run("-vv", "run", "--installpkg", str(wheel)).assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "-v",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--no-install-project",
                "-v",
                "-p",
                sys.executable,
            ],
        ),
        (
            "py",
            "install_external",
            [uv, "pip", "install", "--reinstall", "--no-deps", f"tox-uv@{wheel}", "-v"],
        ),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize(
    ("uv_sync_locked", "locked_flags"),
    [
        pytest.param(True, ["--locked"], id="locked"),
        pytest.param(False, [], id="unlocked"),
    ],
)
def test_uv_sync_extra_flags(tox_project: ToxProjectCreator, uv_sync_locked: bool, locked_flags: list[str]) -> None:
    uv_sync_locked_str = str(uv_sync_locked).lower()
    project = tox_project({
        "tox.ini": f"""
    [testenv]
    runner = uv-venv-lock-runner
    no_default_groups = false
    uv_sync_flags = --no-editable, --inexact
    uv_sync_locked = {uv_sync_locked_str}
    commands = python hello
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run().assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                *locked_flags,
                "--python-preference",
                "system",
                "--no-editable",
                "--inexact",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_sync_extra_flags_toml(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.toml": """
    [env_run_base]
    runner = "uv-venv-lock-runner"
    no_default_groups = false
    uv_sync_flags = ["--no-editable", "--inexact"]
    commands = [["python", "hello"]]
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run().assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--no-editable",
                "--inexact",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize(
    ("env", "tox_ini_extra"),
    [
        pytest.param({"UV_FROZEN": "1"}, "", id="uv_frozen_env"),
        pytest.param({"UV_FROZEN": "1"}, "uv_sync_locked = false", id="frozen_env_with_locked_disabled"),
        pytest.param({}, "uv_sync_flags = --frozen", id="frozen_flag"),
    ],
)
def test_uv_sync_frozen_suppresses_locked(
    tox_project: ToxProjectCreator,
    monkeypatch: pytest.MonkeyPatch,
    env: dict[str, str],
    tox_ini_extra: str,
) -> None:
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    project = tox_project({
        "tox.ini": f"""
    [testenv]
    runner = uv-venv-lock-runner
    no_default_groups = false
    {tox_ini_extra}
    commands = python hello
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run().assert_success()

    uv_sync_cmd = next(i[0][3].cmd for i in execute_calls.call_args_list if i[0][3].run_id == "uv-sync")
    assert "--locked" not in uv_sync_cmd
    assert "--frozen" in uv_sync_cmd


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_sync_dependency_groups(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.toml": """
    [env_run_base]
    runner = "uv-venv-lock-runner"
    with_dev = true
    dependency_groups = ["test", "type"]
    commands = [["python", "hello"]]
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run().assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--no-default-groups",
                "--group",
                "test",
                "--group",
                "type",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.parametrize(
    ("uv_python_preference", "injected"),
    [
        pytest.param("none", [], id="on"),
        pytest.param("system", ["--python-preference", "system"], id="off"),
    ],
)
def test_uv_sync_uv_python_preference(
    tox_project: ToxProjectCreator, uv_python_preference: str, injected: list[str]
) -> None:
    project = tox_project({
        "tox.toml": f"""
    [env_run_base]
    runner = "uv-venv-lock-runner"
    with_dev = true
    dependency_groups = ["test", "type"]
    commands = [["python", "hello"]]
    uv_python_preference = "{uv_python_preference}"
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run().assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                *injected,
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                *injected,
                "--no-default-groups",
                "--group",
                "test",
                "--group",
                "type",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


def test_skip_uv_sync(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)
    project = tox_project({
        "tox.toml": """
    [env_run_base]
    runner = "uv-venv-lock-runner"
    commands = [["python", "hello"]]
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run("run", "--skip-uv-sync").assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.parametrize("package", [pytest.param("wheel", id="wheel"), pytest.param("uv", id="uv")])
def test_uv_package_non_editable(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch, package: str) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)
    project = tox_project({
        "tox.toml": f"""
            [env_run_base]
            runner = "uv-venv-lock-runner"
            package = "{package}"
            """,
        "pyproject.toml": """
            [project]
            name = "demo"
            """,
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run("run", "--notest").assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--no-editable",
                "--reinstall-package",
                "demo",
                "-p",
                sys.executable,
            ],
        ),
    ]
    assert calls == expected


@pytest.mark.parametrize("package", [pytest.param("wheel", id="wheel"), pytest.param("uv", id="uv")])
def test_uv_package_non_editable_no_pyproject(
    tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch, package: str
) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)
    project = tox_project({
        "tox.toml": f"""
            [env_run_base]
            runner = "uv-venv-lock-runner"
            package = "{package}"
            """,
    })
    project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)

    project.run("run", "--notest").assert_failed()


def test_uv_package_uv_editable(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)
    project = tox_project({
        "tox.toml": """
            [env_run_base]
            runner = "uv-venv-lock-runner"
            package = "uv-editable"
            """,
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run("run", "--notest").assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "-p",
                sys.executable,
            ],
        ),
    ]
    assert calls == expected


def test_skip_uv_package_skip(tox_project: ToxProjectCreator, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)
    project = tox_project({
        "tox.toml": """
    [env_run_base]
    runner = "uv-venv-lock-runner"
    package = "skip"
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run("run", "--notest").assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"

    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--no-install-project",
                "-p",
                sys.executable,
            ],
        ),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_lock_ith_resolution(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    uv_resolution = highest
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run("run", "--notest").assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--resolution",
                "highest",
                "-p",
                sys.executable,
            ],
        ),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
def test_uv_sync_only_groups(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.toml": """\
[env_run_base]
runner = "uv-venv-lock-runner"
only_groups = ["ci"]
commands = [["python", "hello"]]
"""
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run().assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = shutil.which("uv")
    prompt = f"{project.path.name}[py]"
    expected = [
        (
            "py",
            "venv",
            [
                uv,
                "venv",
                "-p",
                sys.executable,
                "--allow-existing",
                f"--prompt={prompt}",
                "--python-preference",
                "system",
                str(project.path / ".tox" / "py"),
            ],
        ),
        (
            "py",
            "uv-sync",
            [
                uv,
                "sync",
                "--locked",
                "--python-preference",
                "system",
                "--only-group",
                "ci",
                "-p",
                sys.executable,
            ],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.usefixtures("clear_python_preference_env_var")
@pytest.mark.parametrize(
    ("extra_tox_ini", "run_args", "expected_count"),
    [
        pytest.param("", ("--recreate",), 1, id="recreate-adds-reinstall"),
        pytest.param("uv_sync_flags = --reinstall", ("--recreate",), 1, id="recreate-skips-when-user-set"),
        pytest.param("", (), 0, id="no-recreate-omits-reinstall"),
    ],
)
def test_uv_lock_recreate_reinstall(
    tox_project: ToxProjectCreator, extra_tox_ini: str, run_args: tuple[str, ...], expected_count: int
) -> None:
    project = tox_project({
        "tox.ini": f"""
    [testenv]
    runner = uv-venv-lock-runner
    {extra_tox_ini}
    """
    })
    execute_calls = project.patch_execute(lambda request: 0 if request.run_id != "venv" else None)
    project.run("run", "--notest", *run_args).assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv_sync_call = next(c for c in calls if c[1] == "uv-sync")
    assert uv_sync_call[2].count("--reinstall") == expected_count
