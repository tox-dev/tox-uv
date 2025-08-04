from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tox.pytest import ToxProjectCreator


def test_setupdir_respected(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
[tox]
skipsdist = true
setupdir = src
env_list = py
[testenv]
runner = uv-venv-runner
commands = python -c 'print("hello")'
""",
        "src": {
            "pyproject.toml": """
[project]
name = 'demo'
version = '0'
""",
        },
    })
    result = project.run("-e", "py")
    result.assert_success()


def test_setupdir_with_package_root(tox_project: ToxProjectCreator) -> None:
    project = tox_project({
        "tox.ini": """
[tox]
skipsdist = true
setupdir = src
env_list = py
[testenv]
runner = uv-venv-runner
package_root = src
commands = python -c 'print("hello")'
""",
        "pyproject.toml": "",
        "src": {
            "pyproject.toml": """
[project]
name = 'demo'
version = '0'
""",
        },
    })
    result = project.run("-e", "py")
    result.assert_success()
