"""GitHub Actions integration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

from tox.tox_env.errors import Recreate
from tox.tox_env.python.dependency_groups import resolve as resolve_dependency_groups
from tox.tox_env.python.pip.req_file import PythonDeps
from tox.tox_env.python.runner import PythonRun

from ._package_types import UvEditablePackage, UvPackage
from ._venv import UvVenv

_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


class UvVenvRunner(UvVenv, PythonRun):
    @property
    def _package_tox_env_type(self) -> str:
        return "uv-venv-pep-517"

    @property
    def _external_pkg_tox_env_type(self) -> str:
        return "uv-venv-cmd-builder"  # pragma: no cover tox reads this type name when it builds a package env

    @property
    def default_pkg_type(self) -> str:
        tox_root: Path = self.core["tox_root"]
        if not (any((tox_root / i).exists() for i in ("pyproject.toml", "setup.py", "setup.cfg"))):
            return "skip"
        return super().default_pkg_type

    @property
    def _package_types(self) -> tuple[str, ...]:
        return *super()._package_types, UvPackage.KEY, UvEditablePackage.KEY

    @staticmethod
    def id() -> str:
        return "uv-venv-runner"

    def _install_deps(self) -> None:
        with self.cache.compare(None, PythonRun.__name__, "deps") as (_, old):
            if old is not None:
                msg = "dependency install cache format changed"
                raise Recreate(msg)
        requirements: PythonDeps = self.conf["deps"]
        groups: set[str] = self.conf["dependency_groups"]
        uv_resolution: str = self.conf["uv_resolution"]

        if uv_resolution and groups:
            try:
                root = self.core.get("package_root", Path)
            except KeyError:
                root = self.core.get("tox_root", Path)
            # Preserve tox's environment expansion when combining requirements.
            requirements += PythonDeps(list(resolve_dependency_groups(root, groups)), requirements.path.parent)

            _LOGGER.info(
                "combining deps and dependency groups for uv_resolution=%s to ensure correct resolution",
                uv_resolution,
            )
        # Both modes share a cache, separate from earlier releases' list-installer format.
        self._install(requirements, UvVenvRunner.__name__, "deps")

    def _install_dependency_groups(self) -> None:
        groups: set[str] = self.conf["dependency_groups"]
        uv_resolution: str = self.conf["uv_resolution"]

        if uv_resolution and groups:
            return
        super()._install_dependency_groups()


__all__ = [
    "UvVenvRunner",
]
