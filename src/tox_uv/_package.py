from __future__ import annotations

from tox.tox_env.python.virtual_env.package.cmd_builder import VenvCmdBuilder
from tox.tox_env.python.virtual_env.package.pyproject import Pep517VenvPackager

from ._venv import UvVenv


class UvVenvPep517Packager(Pep517VenvPackager, UvVenv):
    @staticmethod
    def id() -> str:
        return "uv-venv-pep-517"


class UvVenvCmdBuilder(VenvCmdBuilder, UvVenv):
    @staticmethod
    def id() -> str:
        return "uv-venv-cmd-builder"


__all__ = [
    "UvVenvCmdBuilder",
    "UvVenvPep517Packager",
]
