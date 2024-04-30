"""GitHub Actions integration."""

from __future__ import annotations

import json
import sys
from abc import ABC
from functools import cached_property

if sys.version_info >= (3, 9):  # pragma: no cover (py39+)
    from importlib.resources import as_file, files
else:  # pragma: no cover (py38+)
    from importlib_resources import as_file, files


from pathlib import Path
from platform import python_implementation
from typing import TYPE_CHECKING, Any, cast

from tox.execute.local_sub_process import LocalSubProcessExecutor
from tox.execute.request import StdinSource
from tox.tox_env.python.api import Python, PythonInfo, VersionInfo
from uv import find_uv_bin
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
        self._created = False
        super().__init__(create_args)

    def register_config(self) -> None:
        super().register_config()
        desc = "add seed packages to the created venv"
        self.conf.add_config(keys=["uv_seed"], of_type=bool, default=False, desc=desc)

    def python_cache(self) -> dict[str, Any]:
        result = super().python_cache()
        result["seed"] = self.conf["uv_seed"]
        return result

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
        return find_uv_bin()

    @property
    def venv_dir(self) -> Path:
        return cast(Path, self.conf["env_dir"]) / ".venv"

    @property
    def environment_variables(self) -> dict[str, str]:
        env = super().environment_variables
        env["VIRTUAL_ENV"] = str(self.venv_dir)
        return env

    def _default_pass_env(self) -> list[str]:
        env = super()._default_pass_env()
        env.append("UV_*")  # accept uv env vars
        if sys.platform == "darwin":  # pragma: darwin cover
            env.append("MACOSX_DEPLOYMENT_TARGET")  # needed for macOS binary builds
        env.append("PKG_CONFIG_PATH")  # needed for binary builds
        return env

    def create_python_env(self) -> None:
        base, imp = self.base_python.version_info, self.base_python.impl_lower
        if (base.major, base.minor) == sys.version_info[:2] and (sys.implementation.name.lower() == imp):
            version_spec = sys.executable
        else:
            uv_imp = "" if (imp and imp == "cpython") else imp
            version_spec = f"{uv_imp or ''}{base.major}.{base.minor}" if base.minor else f"{uv_imp or ''}{base.major}"
        cmd: list[str] = [self.uv, "venv", "-p", version_spec]
        if self.options.verbosity > 2:  # noqa: PLR2004
            cmd.append("-v")
        if self.conf["uv_seed"]:
            cmd.append("--seed")
        cmd.append(str(self.venv_dir))
        outcome = self.execute(cmd, stdin=StdinSource.OFF, run_id="venv", show=None)
        outcome.assert_success()
        self._created = True

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
        else:  # pragma: win32 no cover # noqa: RET505
            return self.venv_dir / "bin"

    def env_python(self) -> Path:
        suffix = ".exe" if sys.platform == "win32" else ""
        return self.env_bin_dir() / f"python{suffix}"

    def env_site_package_dir(self) -> Path:
        if sys.platform == "win32":  # pragma: win32 cover
            return self.venv_dir / "Lib" / "site-packages"
        else:  # pragma: win32 no cover # noqa: RET505
            py = self._py_info
            impl = "pypy" if py.implementation == "pypy" else "python"
            return self.venv_dir / "lib" / f"{impl}{py.version_dot}" / "site-packages"

    @cached_property
    def _py_info(self) -> PythonInfo:  # pragma: win32 no cover
        if not self._created and not self.env_python().exists():  # called during config, no environment setup
            self.create_python_env()
            self._paths = self.prepend_env_var_path()
        with as_file(files("tox_uv") / "_venv_query.py") as filename:
            cmd = [str(self.env_python()), str(filename)]
            outcome = self.execute(cmd, stdin=StdinSource.OFF, run_id="venv-query", show=False)
        outcome.assert_success()
        res = json.loads(outcome.out)
        return PythonInfo(
            implementation=res["implementation"],
            version_info=VersionInfo(
                major=res["version_info"][0],
                minor=res["version_info"][1],
                micro=res["version_info"][2],
                releaselevel=res["version_info"][3],
                serial=res["version_info"][4],
            ),
            version=res["version"],
            is_64=res["is_64"],
            platform=sys.platform,
            extra={},
        )


__all__ = [
    "UvVenv",
]
