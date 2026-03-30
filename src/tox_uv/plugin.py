"""GitHub Actions integration."""

from __future__ import annotations

import os
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

from tox.config.loader.str_convert import StrConvert
from tox.plugin import impl

from ._package import UvVenvCmdBuilder, UvVenvPep517Packager
from ._run import UvVenvRunner
from ._run_lock import UvVenvLockRunner
from ._run_pep723 import UvVenvPep723Runner

if TYPE_CHECKING:
    from tox.config.cli.parser import ToxParser
    from tox.tox_env.register import ToxEnvRegister


@impl
def tox_register_tox_env(register: ToxEnvRegister) -> None:
    register.add_run_env(UvVenvRunner)
    register.add_run_env(UvVenvLockRunner)
    register.add_run_env(UvVenvPep723Runner)
    if not StrConvert.to_bool(os.environ.get("TOX_UV_NO_PEP723", "false")):
        register._run_envs["virtualenv-pep-723"] = UvVenvPep723Runner  # noqa: SLF001
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
    try:
        uv_version = version("uv")
    except PackageNotFoundError:
        return ""
    return f"with uv=={uv_version}"


__all__ = [
    "tox_register_tox_env",
]
