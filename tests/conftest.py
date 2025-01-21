from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(autouse=True)
def mock_settings_env_vars() -> Generator[None, None, None]:
    """Isolated testing from user's environment."""
    with mock.patch.dict(os.environ, {"TOX_USER_CONFIG_FILE": os.devnull}):
        yield


@pytest.fixture(scope="session")
def root() -> Path:
    return Path(__file__).parent


@pytest.fixture(scope="session")
def demo_pkg_setuptools(root: Path) -> Path:
    return root / "demo_pkg_setuptools"


@pytest.fixture(scope="session")
def demo_pkg_inline(root: Path) -> Path:
    return root / "demo_pkg_inline"


@pytest.fixture
def clear_python_preference_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UV_PYTHON_PREFERENCE", raising=False)


pytest_plugins = [
    "tox.pytest",
]
