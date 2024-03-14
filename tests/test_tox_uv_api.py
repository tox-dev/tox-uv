from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tox.execute import ExecuteRequest
    from tox.pytest import ToxProjectCreator


def test_uv_list_dependencies_command(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip"})
    execute_calls = project.patch_execute(lambda r: 0 if "install" in r.run_id else None)
    result = project.run("--list-dependencies", "-vv")
    result.assert_success()
    request: ExecuteRequest = execute_calls.call_args[0][3]
    assert request.cmd[1:] == ["--color", "never", "pip", "freeze"]
