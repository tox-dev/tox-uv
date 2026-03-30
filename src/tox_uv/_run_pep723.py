"""uv-backed PEP 723 runner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tox.tox_env.python.pep723 import Pep723Mixin
from tox.tox_env.runner import RunToxEnv

from ._venv import UvVenv

if TYPE_CHECKING:
    from tox.tox_env.package import Package


class UvVenvPep723Runner(Pep723Mixin, UvVenv, RunToxEnv):
    @staticmethod
    def id() -> str:
        return "uv-venv-pep-723"

    def _register_package_conf(self) -> bool:  # noqa: PLR6301
        return False

    @property
    def _package_tox_env_type(self) -> str:
        raise NotImplementedError

    @property
    def _external_pkg_tox_env_type(self) -> str:
        raise NotImplementedError

    def _build_packages(self) -> list[Package]:
        raise NotImplementedError


__all__ = [
    "UvVenvPep723Runner",
]
