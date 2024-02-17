"""GitHub Actions integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tox.plugin import impl

from ._package import UvVenvCmdBuilder, UvVenvPep517Packager
from ._run import UvVenvRunner

if TYPE_CHECKING:
    from tox.tox_env.register import ToxEnvRegister


@impl
def tox_register_tox_env(register: ToxEnvRegister) -> None:
    register.add_run_env(UvVenvRunner)
    register.add_package_env(UvVenvPep517Packager)
    register.add_package_env(UvVenvCmdBuilder)
    register._default_run_env = UvVenvRunner.id()  # noqa: SLF001


__all__ = [
    "tox_register_tox_env",
]
