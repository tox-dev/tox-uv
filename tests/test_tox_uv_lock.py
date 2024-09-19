from __future__ import annotations

import sys
from typing import TYPE_CHECKING

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
        ("py", "uv-sync", ["uv", "sync", "--frozen", "--extra", "dev", "--extra", "type"]),
        ("py", "freeze", [uv, "--color", "never", "pip", "freeze"]),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected


def test_uv_lock_command(tox_project: ToxProjectCreator) -> None:
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
        ("py", "uv-sync", ["uv", "sync", "--frozen", "--extra", "dev", "--extra", "type"]),
        ("py", "commands[0]", ["python", "hello"]),
    ]
    assert calls == expected
