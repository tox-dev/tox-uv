from __future__ import annotations

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


@pytest.mark.parametrize("package", ["sdist", "wheel", "editable"])
def test_uv_package_editable(tox_project: ToxProjectCreator, package: str, demo_pkg_inline: Path) -> None:
    project = tox_project({"tox.ini": f"[testenv]\npackage={package}"}, base=demo_pkg_inline)
    result = project.run()
    if package == "sdist":
        result.assert_failed(code=2)
    else:
        result.assert_success()


def test_uv_package_editable_legacy(tox_project: ToxProjectCreator, demo_pkg_setuptools: Path) -> None:
    project = tox_project(
        {"tox.ini": "[testenv]\npackage=editable-legacy\n[testenv:.pkg]\nuv_seed=true"}, base=demo_pkg_setuptools
    )
    result = project.run()
    result.assert_success()


def test_uv_package_requirements(tox_project: ToxProjectCreator) -> None:
    project = tox_project({"tox.ini": "[testenv]\npackage=skip\ndeps=-r demo.txt", "demo.txt": "tomli"})
    result = project.run("-vv")
    result.assert_success()
