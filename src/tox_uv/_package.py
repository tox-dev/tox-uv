from __future__ import annotations

from typing import TYPE_CHECKING

from tox.tox_env.python.virtual_env.package.cmd_builder import VenvCmdBuilder
from tox.tox_env.python.virtual_env.package.pyproject import Pep517VenvPackager

if TYPE_CHECKING:
    from tox.config.sets import EnvConfigSet
    from tox.tox_env.package import Package

from ._package_types import UvFromDirEditablePackage, UvFromDirPackage
from ._venv import UvVenv


class UvVenvPep517Packager(Pep517VenvPackager, UvVenv):
    @staticmethod
    def id() -> str:
        return "uv-venv-pep-517"

    def perform_packaging(self, for_env: EnvConfigSet) -> list[Package]:
        of_type: str = for_env["package"]
        types = {
            "from-dir": UvFromDirPackage,
            "from-dir-editable": UvFromDirEditablePackage,
        }
        if of_type not in types:
            return super().perform_packaging(for_env)

        extras: list[str] = for_env["extras"]
        return [types[of_type](self.core["tox_root"], extras)]


class UvVenvCmdBuilder(VenvCmdBuilder, UvVenv):
    @staticmethod
    def id() -> str:
        return "uv-venv-cmd-builder"


__all__ = [
    "UvVenvCmdBuilder",
    "UvVenvPep517Packager",
]
