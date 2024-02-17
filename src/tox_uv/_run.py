"""GitHub Actions integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tox.tox_env.python.runner import PythonRun

from ._venv import UvVenv

if TYPE_CHECKING:
    from pathlib import Path


class UvVenvRunner(UvVenv, PythonRun):
    @staticmethod
    def id() -> str:
        return "uv-venv-runner"

    @property
    def _package_tox_env_type(self) -> str:
        return "uv-venv-pep-517"

    @property
    def _external_pkg_tox_env_type(self) -> str:
        return "uv-venv-cmd-builder"  # pragma: no cover

    @property
    def default_pkg_type(self) -> str:
        tox_root: Path = self.core["tox_root"]
        if not (any((tox_root / i).exists() for i in ("pyproject.toml", "setup.py", "setup.cfg"))):
            return "skip"
        return super().default_pkg_type


__all__ = [
    "UvVenvRunner",
]
