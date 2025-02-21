from __future__ import annotations

from typing import TYPE_CHECKING

from tox.tox_env.python.virtual_env.package.cmd_builder import VenvCmdBuilder
from tox.tox_env.python.virtual_env.package.pyproject import Pep517VenvPackager

from ._package_types import UvEditablePackage, UvPackage
from ._venv import UvVenv

if TYPE_CHECKING:
    from tox.config.sets import EnvConfigSet
    from tox.tox_env.package import Package


class UvVenvPep517Packager(Pep517VenvPackager, UvVenv):
    @staticmethod
    def id() -> str:
        return "uv-venv-pep-517"

    def perform_packaging(self, for_env: EnvConfigSet) -> list[Package]:
        of_type: str = for_env["package"]
        if of_type == UvPackage.KEY:
            return [UvPackage(self.core["tox_root"], for_env["extras"])]
        if of_type == UvEditablePackage.KEY:
            return [UvEditablePackage(self.core["tox_root"], for_env["extras"])]
        return super().perform_packaging(for_env)


class UvVenvCmdBuilder(VenvCmdBuilder, UvVenv):
    @staticmethod
    def id() -> str:
        return "uv-venv-cmd-builder"


__all__ = [
    "UvVenvCmdBuilder",
    "UvVenvPep517Packager",
]
