"""GitHub Actions integration."""

from __future__ import annotations

from importlib.metadata import version
from typing import TYPE_CHECKING

from tox.plugin import impl

from ._package import UvVenvCmdBuilder, UvVenvPep517Packager
from ._run import UvVenvRunner
from ._run_lock import UvVenvLockRunner

if TYPE_CHECKING:
    from tox.config.cli.parser import ToxParser
    from tox.tox_env.register import ToxEnvRegister


@impl
def tox_register_tox_env(register: ToxEnvRegister) -> None:
    register.add_run_env(UvVenvRunner)
    register.add_run_env(UvVenvLockRunner)
    register.add_package_env(UvVenvPep517Packager)
    register.add_package_env(UvVenvCmdBuilder)
    register._default_run_env = UvVenvRunner.id()  # noqa: SLF001


@impl
def tox_add_option(parser: ToxParser) -> None:
    for key in ("run", "exec"):
        parser.handlers[key][0].add_argument(
            "--skip-uv-sync",
            dest="skip_uv_sync",
            help="skip uv sync (lock mode only)",
            action="store_true",
        )


def tox_append_version_info() -> str:
    return f"with uv=={version('uv')}"


__all__ = [
    "tox_register_tox_env",
]
