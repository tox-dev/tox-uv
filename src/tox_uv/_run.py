"""GitHub Actions integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from packaging.requirements import Requirement
from tox.tox_env.python.dependency_groups import resolve as resolve_dependency_groups
from tox.tox_env.python.runner import PythonRun

from ._package_types import UvEditablePackage, UvPackage
from ._venv import UvVenv

if TYPE_CHECKING:
    from pathlib import Path

_LOGGER = logging.getLogger(__name__)


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

    @property
    def _package_types(self) -> tuple[str, ...]:
        return *super()._package_types, UvPackage.KEY, UvEditablePackage.KEY

    def _install_deps(self) -> None:
        groups: set[str] = self.conf["dependency_groups"]
        uv_resolution: str = self.conf["uv_resolution"]

        if uv_resolution and groups:
            try:
                root: Path = self.core["package_root"]
            except KeyError:
                root = self.core["tox_root"]
            group_reqs = list(resolve_dependency_groups(root, groups))
            deps_file = self.conf["deps"]
            deps_reqs = [Requirement(line) for line in deps_file.lines()]
            combined_reqs = deps_reqs + group_reqs

            _LOGGER.info(
                "combining deps and dependency groups for uv_resolution=%s to ensure correct resolution",
                uv_resolution,
            )
            self._install(combined_reqs, PythonRun.__name__, "deps")
        else:
            super()._install_deps()

    def _install_dependency_groups(self) -> None:
        groups: set[str] = self.conf["dependency_groups"]
        uv_resolution: str = self.conf["uv_resolution"]

        if uv_resolution and groups:
            return
        super()._install_dependency_groups()


__all__ = [
    "UvVenvRunner",
]
