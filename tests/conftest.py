from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def root() -> Path:
    return Path(__file__).parent


@pytest.fixture(scope="session")
def demo_pkg_setuptools(root: Path) -> Path:
    return root / "demo_pkg_setuptools"


@pytest.fixture(scope="session")
def demo_pkg_inline(root: Path) -> Path:
    return root / "demo_pkg_inline"


pytest_plugins = [
    "tox.pytest",
]
