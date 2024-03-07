from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from tox.pytest import ToxProjectCreator


def test_uv_package_skip(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip"})
    result = project.run("-vv")
    result.assert_success()


def test_uv_package_use_default_from_file(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip", "pyproject.toml": ""})
    result = project.run("-vv")
    result.assert_success()


@pytest.mark.parametrize("with_dash", [True, False], ids=["name_dash", "name_underscore"])
@pytest.mark.parametrize("package", ["sdist", "wheel", "editable"])
def test_uv_package_artifact(
    tox_project: ToxProjectCreator, package: str, demo_pkg_inline: Path, with_dash: bool
) -> None:
    ini = f"[testenv]\npackage={package}"
    if with_dash:
        ini += "\n[testenv:.pkg]\nset_env = WITH_DASH = 1"
    project = tox_project({"tox.ini": ini}, base=demo_pkg_inline)
    result = project.run()
    result.assert_success()


def test_uv_package_editable_legacy(tox_project: ToxProjectCreator, demo_pkg_setuptools: Path) -> None:
    ini = f"""
    [testenv]
    package=editable-legacy

    [testenv:.pkg]
    uv_seed = true
    {"deps = wheel" if sys.version_info >= (3, 12) else ""}
    """
    project = tox_project({"tox.ini": ini}, base=demo_pkg_setuptools)
    result = project.run()
    result.assert_success()


def test_uv_package_requirements(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ndeps=-r demo.txt", "demo.txt": "tomli"})
    result = project.run("-vv")
    result.assert_success()
