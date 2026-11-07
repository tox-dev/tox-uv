from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from tox.pytest import ToxProjectCreator


def test_uv_package_skip(tox_project: ToxProjectCreator) -> None:
    tox_project({"tox.ini": "[testenv]\npackage=skip"}).run("-vv").assert_success()


def test_uv_package_use_default_from_file(tox_project: ToxProjectCreator) -> None:
    tox_project({"tox.ini": "[testenv]\npackage=skip", "pyproject.toml": ""}).run("-vv").assert_success()


@pytest.mark.parametrize("with_dash", [True, False], ids=["name_dash", "name_underscore"])
@pytest.mark.parametrize("package", ["sdist", "wheel", "editable", "uv", "uv-editable"])
def test_uv_package_artifact(
    tox_project: ToxProjectCreator, package: str, demo_pkg_inline: Path, with_dash: bool
) -> None:
    ini = f"[testenv]\npackage={package}"
    if with_dash:
        ini += "\n[testenv:.pkg]\nset_env = WITH_DASH = 1"
    tox_project({"tox.ini": ini}, base=demo_pkg_inline).run().assert_success()


def test_uv_package_editable_legacy(tox_project: ToxProjectCreator, demo_pkg_setuptools: Path) -> None:
    ini = """
    [testenv]
    package=editable-legacy

    [testenv:.pkg]
    uv_seed = true
    """
    tox_project({"tox.ini": ini}, base=demo_pkg_setuptools).run().assert_success()


def test_uv_package_requirements(tox_project: ToxProjectCreator) -> None:
    result = tox_project({"tox.ini": "[testenv]\npackage=skip\ndeps=-r demo.txt", "demo.txt": "tomli"}).run("-vv")
    result.assert_success()


def test_uv_package_list_sources(tox_project: ToxProjectCreator, demo_pkg_inline: Path) -> None:
    ini = """
    [testenv]
    """
    project = tox_project({"tox.ini": ini}, base=demo_pkg_inline)
    pyproject = project.path / "pyproject.toml"
    pyproject.write_text(
        f"""{pyproject.read_text()}[tool.uv.sources]
some-dep = [
  {{index = "foo", marker = "sys_platform == 'linux'"}},
  {{index = "bar", marker = "sys_platform == 'darwin'"}},
]
"""
    )
    project.run().assert_success()


def test_uv_package_workspace(tox_project: ToxProjectCreator, demo_pkg_workspace: Path) -> None:
    # Tests ability to install uv workspace projects.
    ini = """
    [testenv]

    [testenv:.pkg]
    uv_seed = true
    """
    tox_project({"tox.ini": ini}, base=demo_pkg_workspace).run().assert_success()


def test_uv_package_no_pyproject(tox_project: ToxProjectCreator, demo_pkg_no_pyproject: Path) -> None:
    # Tests ability to install uv workspace projects.
    ini = """
    [testenv]

    [testenv:.pkg]
    uv_seed = true
    """
    tox_project({"tox.ini": ini}, base=demo_pkg_no_pyproject).run().assert_success()
