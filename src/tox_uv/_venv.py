"""GitHub Actions integration."""

from __future__ import annotations

import sys
from abc import ABC
from pathlib import Path
from platform import python_implementation
from typing import TYPE_CHECKING, Any, cast

from tox.execute.local_sub_process import LocalSubProcessExecutor
from tox.execute.request import StdinSource
from tox.tox_env.python.api import Python, PythonInfo, VersionInfo
from virtualenv.discovery.py_spec import PythonSpec

from ._installer import UvInstaller

if TYPE_CHECKING:
    from tox.execute.api import Execute
    from tox.tox_env.api import ToxEnvCreateArgs
    from tox.tox_env.installer import Installer


class UvVenv(Python, ABC):
    def __init__(self, create_args: ToxEnvCreateArgs) -> None:
        self._executor: Execute | None = None
        self._installer: UvInstaller | None = None
        super().__init__(create_args)

    @property
    def executor(self) -> Execute:
        if self._executor is None:
            self._executor = LocalSubProcessExecutor(self.options.is_colored)
        return self._executor

    @property
    def installer(self) -> Installer[Any]:
        if self._installer is None:
            self._installer = UvInstaller(self)
        return self._installer

    @property
    def runs_on_platform(self) -> str:
        return sys.platform

    def _get_python(self, base_python: list[str]) -> PythonInfo | None:  # noqa: PLR6301
        for base in base_python:  # pragma: no branch
            if base == sys.executable:
                version_info = sys.version_info
                return PythonInfo(
                    implementation=python_implementation(),
                    version_info=VersionInfo(
                        major=version_info.major,
                        minor=version_info.minor,
                        micro=version_info.micro,
                        releaselevel=version_info.releaselevel,
                        serial=version_info.serial,
                    ),
                    version=sys.version,
                    is_64=sys.maxsize > 2**32,
                    platform=sys.platform,
                    extra={},
                )
            spec = PythonSpec.from_string_spec(base)
            return PythonInfo(
                implementation=spec.implementation or "CPython",
                version_info=VersionInfo(
                    major=spec.major,
                    minor=spec.minor,
                    micro=spec.micro,
                    releaselevel="",
                    serial=0,
                ),
                version=str(spec),
                is_64=spec.architecture == 64,  # noqa: PLR2004
                platform=sys.platform,
                extra={},
            )
        return None  # pragma: no cover

    @property
    def uv(self) -> str:
        return str(Path(sys.executable).parent / "uv")

    @property
    def venv_dir(self) -> Path:
        return cast(Path, self.conf["env_dir"]) / ".venv"

    @property
    def environment_variables(self) -> dict[str, str]:
        env = super().environment_variables
        env["VIRTUAL_ENV"] = str(self.venv_dir)
        return env

    def create_python_env(self) -> None:
        base = self.base_python
        cmd = [self.uv, "venv", "-p", base.version_dot, "--seed", str(self.venv_dir)]
        outcome = self.execute(cmd, stdin=StdinSource.OFF, run_id="venv", show=False)
        outcome.assert_success()

    @property
    def _allow_externals(self) -> list[str]:
        result = super()._allow_externals
        result.append(self.uv)
        return result

    def prepend_env_var_path(self) -> list[Path]:
        return [self.env_bin_dir()]

    def env_bin_dir(self) -> Path:
        if sys.platform == "win32":  # pragma: win32 cover
            return self.venv_dir / "Scripts"
        # pragma: win32 no cover
        return self.venv_dir / "bin"

    def env_python(self) -> Path:
        suffix = ".exe" if sys.platform == "win32" else ""
        return self.env_bin_dir() / f"python{suffix}"

    def env_site_package_dir(self) -> Path:
        if sys.platform == "win32":  # pragma: win32 cover
            return self.venv_dir / "Lib" / "site-packages"
        # pragma: win32 no cover
        return self.venv_dir / "lib" / f"python{self.base_python.version_dot}" / "site-packages"


__all__ = [
    "UvVenv",
]
