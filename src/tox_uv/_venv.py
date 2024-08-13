"""GitHub Actions integration."""

from __future__ import annotations

import json
import sys
from abc import ABC
from functools import cached_property
from pathlib import Path
from platform import python_implementation
from typing import TYPE_CHECKING, Any, Literal, Optional, Type, cast

from tox.execute.local_sub_process import LocalSubProcessExecutor
from tox.execute.request import StdinSource
from tox.tox_env.errors import Skip
from tox.tox_env.python.api import Python, PythonInfo, VersionInfo
from tox.tox_env.python.virtual_env.api import VirtualEnv
from uv import find_uv_bin
from virtualenv.discovery.py_spec import PythonSpec

from ._installer import UvInstaller

if sys.version_info >= (3, 10):  # pragma: no cover (py310+)
    from typing import TypeAlias
else:  # pragma: no cover (<py310)
    from typing_extensions import TypeAlias

if sys.version_info >= (3, 9):  # pragma: no cover (py39+)
    from importlib.resources import as_file, files
else:  # pragma: no cover (py38+)
    from importlib_resources import as_file, files

if TYPE_CHECKING:
    from tox.execute.api import Execute
    from tox.tox_env.api import ToxEnvCreateArgs
    from tox.tox_env.installer import Installer


PythonPreference: TypeAlias = Literal[
    "only-managed",
    "managed",
    "system",
    "only-system",
]


class UvVenv(Python, ABC):
    def __init__(self, create_args: ToxEnvCreateArgs) -> None:
        self._executor: Execute | None = None
        self._installer: UvInstaller | None = None
        self._created = False
        super().__init__(create_args)

    def register_config(self) -> None:
        super().register_config()
        self.conf.add_config(
            keys=["uv_seed"],
            of_type=bool,
            default=False,
            desc="add seed packages to the created venv",
        )
        # The cast(...) might seems superfluous but removing it makes mypy crash. The problem isy on tox typing side.
        self.conf.add_config(
            keys=["uv_python_preference"],
            of_type=cast(Type[Optional[PythonPreference]], Optional[PythonPreference]),
            default=None,
            desc=(
                "Whether to prefer using Python installations that are already"
                " present on the system, or those that are downloaded and"
                " installed by uv [possible values: only-managed, installed,"
                " managed, system, only-system]. Use none to use uv's"
                " default."
            ),
        )

    def python_cache(self) -> dict[str, Any]:
        result = super().python_cache()
        result["seed"] = self.conf["uv_seed"]
        result["python_preference"] = self.conf["uv_python_preference"]
        result["venv"] = str(self.venv_dir.relative_to(self.env_dir))
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
            base_path = Path(base)
            if base_path.is_absolute():
                info = VirtualEnv.get_virtualenv_py_info(base_path)
                return PythonInfo(
                    implementation=info.implementation,
                    version_info=VersionInfo(*info.version_info),
                    version=info.version,
                    is_64=info.architecture == 64,  # noqa: PLR2004
                    platform=info.platform,
                    extra={"executable": base},
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

    @classmethod
    def python_spec_for_path(cls, path: Path) -> PythonSpec:
        """
        Get the spec for an absolute path to a Python executable.

        :param path: the path investigated
        :return: the found spec
        """
        return VirtualEnv.python_spec_for_path(path)

    @property
    def uv(self) -> str:
        return find_uv_bin()

    @property
    def venv_dir(self) -> Path:
        return cast(Path, self.conf["env_dir"])

    @property
    def environment_variables(self) -> dict[str, str]:
        env = super().environment_variables
        env.pop("UV_PYTHON", None)  # UV_PYTHON takes precedence over VIRTUAL_ENV
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
        base = self.base_python.version_info
        imp = self.base_python.impl_lower
        executable = self.base_python.extra.get("executable")
        if executable:
            version_spec = executable
        elif (base.major, base.minor) == sys.version_info[:2] and (sys.implementation.name.lower() == imp):
            version_spec = sys.executable
        else:
            uv_imp = "" if (imp and imp == "cpython") else imp
            version_spec = f"{uv_imp or ''}{base.major}.{base.minor}" if base.minor else f"{uv_imp or ''}{base.major}"

        cmd: list[str] = [self.uv, "venv", "-p", version_spec, "--allow-existing"]
        if self.options.verbosity > 2:  # noqa: PLR2004
            cmd.append("-v")
        if self.conf["uv_seed"]:
            cmd.append("--seed")
        if self.conf["uv_python_preference"]:
            cmd.extend(["--python-preference", self.conf["uv_python_preference"]])
        cmd.append(str(self.venv_dir))
        outcome = self.execute(cmd, stdin=StdinSource.OFF, run_id="venv", show=None)

        if self.core["skip_missing_interpreters"] and outcome.exit_code == 1:
            msg = "could not find python interpreter with spec(s):" f" {version_spec}"
            raise Skip(msg)

        outcome.assert_success()
        self._created = True

    @property
    def _allow_externals(self) -> list[str]:
        result = super()._allow_externals
        result.append(self.uv)
        return result

    def prepend_env_var_path(self) -> list[Path]:
        return [self.env_bin_dir(), Path(self.uv).parent]

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
