from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest
from uv import find_uv_bin

if TYPE_CHECKING:
    from tox.pytest import ToxProjectCreator


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
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run("--list-dependencies", "-vv")
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = find_uv_bin()
    expected = [
        (
            "py",
            "venv",
            [uv, "venv", "-p", sys.executable, "--allow-existing", "-v", str(project.path / ".tox" / "py")],
        ),
        ("py", "uv-sync", ["uv", "sync", "--frozen", "--extra", "dev", "--extra", "type", "--no-dev", "-v"]),
        ("py", "freeze", [uv, "--color", "never", "pip", "freeze"]),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


@pytest.mark.parametrize("verbose", ["", "-v", "-vv", "-vvv"])
def test_uv_lock_command(tox_project: ToxProjectCreator, verbose: str) -> None:
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
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run(*[verbose] if verbose else [])
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = find_uv_bin()
    v_args = ["-v"] if verbose not in {"", "-v"} else []
    expected = [
        (
            "py",
            "venv",
            [uv, "venv", "-p", sys.executable, "--allow-existing", *v_args, str(project.path / ".tox" / "py")],
        ),
        ("py", "uv-sync", ["uv", "sync", "--frozen", "--extra", "dev", "--extra", "type", "--no-dev", *v_args]),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected
    show_uv_output = execute_calls.call_args_list[1].args[4]
    assert show_uv_output is (bool(verbose))


def test_uv_lock_with_dev(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    with_dev = True
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run("-vv")
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = find_uv_bin()
    expected = [
        (
            "py",
            "venv",
            [uv, "venv", "-p", sys.executable, "--allow-existing", "-v", str(project.path / ".tox" / "py")],
        ),
        ("py", "uv-sync", ["uv", "sync", "--frozen", "-v"]),
    ]
    assert calls == expected


@pytest.mark.parametrize(
    "name",
    [
        "tox_uv-1.12.2-py3-none-any.whl",
        "tox_uv-1.12.2.tar.gz",
    ],
)
def test_uv_lock_with_install_pkg(tox_project: ToxProjectCreator, name: str) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    wheel = project.path / name
    wheel.write_text("")
    result = project.run("-vv", "run", "--installpkg", str(wheel))
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = find_uv_bin()
    expected = [
        (
            "py",
            "venv",
            [uv, "venv", "-p", sys.executable, "--allow-existing", "-v", str(project.path / ".tox" / "py")],
        ),
        ("py", "uv-sync", ["uv", "sync", "--frozen", "--no-dev", "--no-install-project", "-v"]),
        (
            "py",
            "install_external",
            [uv, "pip", "install", "--reinstall", "--no-deps", f"tox-uv@{wheel}", "-v"],
        ),
    ]
    assert calls == expected


def test_uv_sync_extra_flags(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
    [testenv]
    runner = uv-venv-lock-runner
    with_dev = true
    uv_sync_flags = --no-editable, --inexact
    commands = python hello
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run()
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = find_uv_bin()

    expected = [
        (
            "py",
            "venv",
            [uv, "venv", "-p", sys.executable, "--allow-existing", str(project.path / ".tox" / "py")],
        ),
        (
            "py",
            "uv-sync",
            ["uv", "sync", "--frozen", "--no-editable", "--inexact"],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


def test_uv_sync_extra_flags_toml(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.toml": """
    [env_run_base]
    runner = "uv-venv-lock-runner"
    with_dev = true
    uv_sync_flags = ["--no-editable", "--inexact"]
    commands = [["python", "hello"]]
    """
    })
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run()
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = find_uv_bin()

    expected = [
        (
            "py",
            "venv",
            [uv, "venv", "-p", sys.executable, "--allow-existing", str(project.path / ".tox" / "py")],
        ),
        (
            "py",
            "uv-sync",
            ["uv", "sync", "--frozen", "--no-editable", "--inexact"],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


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
    execute_calls = project.patch_execute(lambda r: 0 if r.run_id != "venv" else None)
    result = project.run()
    result.assert_success()

    calls = [(i[0][0].conf.name, i[0][3].run_id, i[0][3].cmd) for i in execute_calls.call_args_list]
    uv = find_uv_bin()

    expected = [
        (
            "py",
            "venv",
            [uv, "venv", "-p", sys.executable, "--allow-existing", str(project.path / ".tox" / "py")],
        ),
        (
            "py",
            "uv-sync",
            ["uv", "sync", "--frozen", "--group", "test", "--group", "type"],
        ),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected
